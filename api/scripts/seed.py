import asyncio

from sqlalchemy import select

from core.db import AsyncSessionLocal
from models.domain import Source, SourceType


async def seed_sources():
    default_sources = [
        # Example search engineering, IR, or AI news feeds
        {
            "name": "arXiv CS.IR",
            "url": "https://export.arxiv.org/rss/cs.IR",
            "weight": 1.2,
            "type": SourceType.rss,
            "enabled": True,
        },
        {
            "name": "Google Search Central",
            "url": "https://developers.google.com/search/blog/rss",
            "weight": 2.0,
            "type": SourceType.rss,
            "enabled": True,
        },
        {
            "name": "HackerNews Frontpage",
            "url": "https://hnrss.org/frontpage?points=100",
            "weight": 1.0,
            "type": SourceType.rss,
            "enabled": True,
        },
        {
            "name": "Connpass Search/IR Events",
            "url": "https://connpass.com/api/v2/events/",
            "weight": 1.5,
            "type": SourceType.connpass_api,
            "enabled": True,
        },
    ]

    async with AsyncSessionLocal() as db:
        for s in default_sources:
            # Check if exists
            q = select(Source).filter(Source.url == s["url"])
            res = await db.execute(q)
            if not res.scalar_one_or_none():
                new_source = Source(**s)
                db.add(new_source)
                print(f"Added source: {s['name']}")
            else:
                print(f"Skipped existing source: {s['name']}")

        await db.commit()
        print("Seed completed.")


if __name__ == "__main__":
    asyncio.run(seed_sources())
