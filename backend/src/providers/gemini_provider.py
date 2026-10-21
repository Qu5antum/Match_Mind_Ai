import asyncio
import logging
from typing import Type
from pydantic import BaseModel
from google import genai
from google.genai import types
from google.genai import errors
import json

from .base_provider import BaseProvider
from src.core.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider(BaseProvider):
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY must be configured for AI requests")
        if not settings.GEMINI_MODEL:
            raise RuntimeError("GEMINI_MODEL must be configured for AI requests")

        self.model = settings.GEMINI_MODEL
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
            http_options=types.HttpOptions(timeout=settings.GEMINI_TIMEOUT_MS),
        )

    def text(self, text_to_analyze: str, response_schema: Type[BaseModel]) -> BaseModel:
        schema = response_schema.model_json_schema()

        logger.info(
            "Gemini request: model=%s, schema_name=%s, prompt_length=%s",
            self.model,
            response_schema.__name__,
            len(text_to_analyze),
        )
        logger.debug(
            "Gemini response schema:\n%s",
            json.dumps(schema, indent=2, ensure_ascii=False),
        )

        config = types.GenerateContentConfig(
            system_instruction=(
                "You are MatchMind AI, a football match analysis assistant. "
                "Use only the supplied match data. "
                "Never invent scores, statistics, events, or player performance. "
                "Return conclusions supported by the provided evidence."
            ),
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=0.2,
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=text_to_analyze,
                config=config,
            )
        except errors.APIError as exc:
            logger.error("Gemini API error type: %s", type(exc).__name__)
            logger.error("Gemini API error code: %s", exc.code)
            logger.error("Gemini API error message: %s", exc.message)
            logger.error("Gemini API error repr: %r", exc)
            logger.exception("Full Gemini API traceback")
            raise

        if not response.text:
            raise ValueError("Gemini returned an empty response")

        return response_schema.model_validate_json(response.text)


    async def atext(
        self,
        text_to_analyze: str,
        response_schema: Type[BaseModel],
    ) -> BaseModel:
        return await asyncio.to_thread(
            self.text,
            text_to_analyze,
            response_schema,
        )
