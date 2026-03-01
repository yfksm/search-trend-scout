import hashlib
import logging
from datetime import datetime

import feedparser
import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import AsyncSessionLocal
from models.domain import IngestionRun, Item, LaneType, Source, SourceType, Tag
from services.llm import get_summarizer

logger = logging.getLogger(__name__)


def calculate_score(source_weight: float, published_at: datetime | None, item: Item) -> float:
    # MVP scoring based on PRD requirements
    # 1. Base weight
    score = source_weight

    # 2. Freshness decay
    now = datetime.utcnow()
    pub_date = published_at or now
    age_days = (now - pub_date.replace(tzinfo=None)).days
    freshness = max(0.1, 1.0 - (max(0, age_days) * 0.1))  # Decay over 10 days
    score *= freshness

    # 3. Impact signals
    content_lower = str(item.content_text or "").lower()
    impact_signal = 1.0 + (0.1 * sum(1 for s in settings.IMPACT_SIGNALS if s in content_lower))
    score *= impact_signal

    # 4. Implementation signals
    impl_signal = 1.0 + (0.2 * sum(1 for s in settings.IMPL_SIGNALS if s in content_lower))
    score *= impl_signal

    # 5. Novelty penalty (Requires complex DB clustering, skipping for MVP Phase 1)

    return min(10.0, score)  # Cap at 10.0


async def process_rss_source(source: Source, db: AsyncSession, summarizer, run: IngestionRun):
    feed = feedparser.parse(source.url)

    for entry in feed.entries:
        link = getattr(entry, "link", None)
        if not link:
            continue

        # Deduplication
        hash_id = hashlib.md5(link.encode()).hexdigest()
        existing = await db.execute(select(Item).filter(Item.hash == hash_id))
        if existing.scalar_one_or_none():
            continue

        title = getattr(entry, "title", "Untitled")
        pub_date = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            pub_date = datetime(*entry.published_parsed[:6])

        # Fetch actual content if possible
        content_text = ""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(link)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    content_text = soup.get_text(separator=" ", strip=True)
        except Exception as e:
            logger.warning(f"Failed to fetch content for {link}: {e}")
            content_text = getattr(entry, "description", "")

        # LLM processing
        llm_data = await summarizer.summarize(content_text, title)

        item = Item(
            source_id=source.id,
            url=link,
            title=title,
            published_at=pub_date,
            content_text=content_text,
            hash=hash_id,
            site=source.name,
            why_important=llm_data.get("why_important"),
            summary_tldr=llm_data.get("summary_tldr"),
            summary_bullets=llm_data.get("summary_bullets", []),
            tradeoffs=llm_data.get("tradeoffs"),
        )

        # Lane mapping
        lane_str = llm_data.get("lane", "ecosystem")
        try:
            item.lane = LaneType(lane_str)
        except ValueError:
            item.lane = LaneType.ecosystem

        # Scoring
        item.score = calculate_score(source.weight, pub_date, item)

        # Build tags
        tag_names = llm_data.get("tags", [])
        for t_name in tag_names:
            t_name = t_name.lower().strip()
            if not t_name:
                continue

            tag_res = await db.execute(select(Tag).filter(Tag.name == t_name))
            tag = tag_res.scalar_one_or_none()
            if not tag:
                tag = Tag(name=t_name)
                db.add(tag)
            item.tags.append(tag)

        db.add(item)
        run.items_added += 1
        await db.commit()
    run.items_processed += 1


async def process_connpass_api(source: Source, db: AsyncSession, summarizer, run: IngestionRun):
    api_key = settings.CONNPASS_API_KEY
    if not api_key:
        logger.warning(f"Skipping Connpass source {source.name} since CONNPASS_API_KEY is not set.")
        return

    # API v2 endpoint based on research
    endpoint = "https://connpass.com/api/v2/events/"
    params = {"keyword_or": "検索,RAG,Elasticsearch,IR,情報検索", "order": 3, "count": 15}
    headers = {"X-API-Key": api_key}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(endpoint, params=params, headers=headers)
            if resp.status_code != 200:
                logger.error(f"Connpass API error: {resp.status_code} {resp.text}")
                return
            data = resp.json()
    except Exception as e:
        logger.error(f"Failed to fetch Connpass API: {e}")
        return

    events = data.get("events", [])
    for ev in events:
        link = ev.get("event_url")
        if not link:
            continue

        hash_id = hashlib.md5(link.encode()).hexdigest()
        existing = await db.execute(select(Item).filter(Item.hash == hash_id))
        if existing.scalar_one_or_none():
            continue

        title = ev.get("title", "Unknown Event")
        pub_str = ev.get("created_at")
        pub_date = datetime.fromisoformat(pub_str.replace("Z", "+00:00")) if pub_str else datetime.utcnow()

        # LLM processing based on description / catchphrase
        content_text = f"Title: {title}\nCatch: {ev.get('catch', '')}\nDesc: {ev.get('description', '')}"

        # Strip HTML from desc for LLM
        soup = BeautifulSoup(content_text, "html.parser")
        clean_text = soup.get_text(separator=" ", strip=True)

        llm_data = await summarizer.summarize(clean_text, title)

        item = Item(
            source_id=source.id,
            url=link,
            title=f"[Event] {title}",
            published_at=pub_date,
            content_text=clean_text,
            hash=hash_id,
            site=source.name,
            why_important=llm_data.get("why_important"),
            summary_tldr=llm_data.get("summary_tldr"),
            summary_bullets=llm_data.get("summary_bullets", []),
            tradeoffs=llm_data.get("tradeoffs"),
        )

        lane_str = llm_data.get("lane", "practice")
        try:
            item.lane = LaneType(lane_str)
        except ValueError:
            item.lane = LaneType.practice

        item.score = calculate_score(source.weight, pub_date, item)

        tag_names = llm_data.get("tags", [])
        tag_names.append("event")
        tag_names.append("connpass")
        for t_name in tag_names:
            t_name = t_name.lower().strip()
            if not t_name:
                continue
            tag_res = await db.execute(select(Tag).filter(Tag.name == t_name))
            tag = tag_res.scalar_one_or_none()
            if not tag:
                tag = Tag(name=t_name)
                db.add(tag)
            if tag not in item.tags:
                item.tags.append(tag)

        db.add(item)
        run.items_added += 1
        await db.commit()
    run.items_processed += 1


async def run_ingestion_task():
    try:
        async with AsyncSessionLocal() as db:
            # Check for active run
            active_q = select(IngestionRun).filter(IngestionRun.status == "running")
            res = await db.execute(active_q)
            if res.scalar_one_or_none():
                logger.info("Ingestion is already running. Skipping.")
                return

            run = IngestionRun(status="running")
            db.add(run)
            await db.commit()
            await db.refresh(run)

            summarizer = get_summarizer()

            q = select(Source).filter(Source.enabled)
            res = await db.execute(q)
            sources = res.scalars().all()

            for source in sources:
                try:
                    if source.type == SourceType.rss:
                        await process_rss_source(source, db, summarizer, run)
                    elif source.type == SourceType.connpass_api:
                        await process_connpass_api(source, db, summarizer, run)
                except Exception as e:
                    logger.error(f"Error processing source {source.name}: {e}")
                    run.errors += 1
                    
            # Mark complete
            run.status = "completed"
            run.run_ended_at = datetime.utcnow()
            await db.commit()

    except Exception as e:
        logger.error(f"Global ingestion task error: {e}")
        async with AsyncSessionLocal() as db:
            # Attempt to set failure mode
            # If run was created, try to update the last one
            fail_q = select(IngestionRun).order_by(IngestionRun.run_started_at.desc()).limit(1)
            fail_res = await db.execute(fail_q)
            last_run = fail_res.scalar_one_or_none()
            if last_run and last_run.status == "running":
                last_run.status = "failed"
                last_run.run_ended_at = datetime.utcnow()
                await db.commit()
