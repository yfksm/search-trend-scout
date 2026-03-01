import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from core.config import settings

logger = logging.getLogger(__name__)


class LLMResponse(ABC):
    why_important: str = ""
    summary_tldr: str = ""
    tradeoffs: str = ""
    summary_bullets: list[str] = []
    lane: str = "ecosystem"
    tags: list[str] = []


class Summarizer(ABC):
    @abstractmethod
    async def summarize(self, text: str, title: str) -> dict[str, Any]:
        """
        Returns a dict matching LLMResponse fields.
        Must handle errors gracefully and return default/fallback answers.
        """
        pass


class OpenAISummarizer(Summarizer):
    def __init__(self, api_key: str):
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key)

    async def summarize(self, text: str, title: str) -> dict[str, Any]:
        prompt = f"""
        You are an expert search and ranking engineer.
        Analyze this article: "{title}"
        Content:
        {text[:8000]} # Truncated for context

        Extract the following strictly as a JSON object:
        {{
            "why_important": "One short sentence explaining why a search engineer should care.",
            "summary_tldr": "3 lines summary.",
            "summary_bullets": ["point 1", "point 2", "point 3"],
            "tradeoffs": "What are the trade-offs? (Speed, Cost, Accuracy, Ops)",
            "lane": "research" | "practice" | "ecosystem",
            "tags": ["tag1", "tag2", "tag3"]
        }}
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"LLM Summarization failed: {e}")
            return self._fallback(title)

    def _fallback(self, title: str) -> dict[str, Any]:
        return {
            "why_important": "Failed to automatically summarize.",
            "summary_tldr": "Content must be read manually.",
            "summary_bullets": [],
            "tradeoffs": "N/A",
            "lane": "ecosystem",
            "tags": ["needs-review"],
        }


def get_summarizer() -> Summarizer:
    if settings.LLM_PROVIDER == "openai" and settings.LLM_API_KEY:
        return OpenAISummarizer(settings.LLM_API_KEY)

    # Simple fallback if no API key is provided
    class FallbackSummarizer(Summarizer):
        async def summarize(self, text: str, title: str) -> dict[str, Any]:
            return {
                "why_important": "LLM disabled. Manual review required.",
                "summary_tldr": f"Title: {title}",
                "summary_bullets": [],
                "tradeoffs": "N/A",
                "lane": "ecosystem",
                "tags": ["auto-ingested"],
            }

    return FallbackSummarizer()
