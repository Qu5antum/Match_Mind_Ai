import asyncio
import time
from typing import Any, Type
import httpx
from pydantic import BaseModel

from src.core.config import settings
from src.providers.base_provider import BaseProvider


class ManusProvider(BaseProvider):
    BASE_URL = "https://api.manus.ai"
    POLL_INTERVAL = 2
    TIMEOUT = 240

    def __init__(self):
        self.model = getattr(settings, "MANUS_MODEL", "manus")
        self.api_key = settings.MANUS_API_KEY

        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "x-manus-api-key": self.api_key,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    @staticmethod
    def _resolve_schema(
        schema: dict[str, Any],
        definitions: dict[str, Any],
    ) -> dict[str, Any]:
        if isinstance(schema, list):
            return [
                ManusProvider._resolve_schema(item, definitions)
                for item in schema
            ]

        if not isinstance(schema, dict):
            return schema

        if "$ref" in schema:
            ref = schema["$ref"]
            prefix = "#/$defs/"

            if not ref.startswith(prefix):
                raise ValueError(f"Unsupported JSON Schema reference: {ref}")

            name = ref[len(prefix):]
            if name not in definitions:
                raise ValueError(f"Schema definition not found: {name}")

            resolved = ManusProvider._resolve_schema(
                definitions[name], definitions
            )

            extra = {
                key: value
                for key, value in schema.items()
                if key != "$ref"
            }

            return {
                **resolved,
                **ManusProvider._resolve_schema(extra, definitions),
            }

        result = {
            key: ManusProvider._resolve_schema(value, definitions)
            for key, value in schema.items()
            if key not in {"$defs", "definitions"}
        }

        if result.get("type") == "object":
            properties = result.get("properties", {})
            result["required"] = list(properties.keys())
            result["additionalProperties"] = False

        return result

    @classmethod
    def _build_schema(
        cls,
        response_schema: Type[BaseModel],
    ) -> dict[str, Any]:
        raw_schema = response_schema.model_json_schema()
        definitions = raw_schema.get("$defs", {})

        return cls._resolve_schema(raw_schema, definitions)

    def text(
        self,
        text_to_analyze: str,
        response_schema: Type[BaseModel],
    ) -> BaseModel:
        schema = self._build_schema(response_schema)

        response = self.client.post(
            "/v2/task.create",
            json={
                "title": "MatchMind AI - Match Insights",
                "message": {
                    "content": text_to_analyze,
                },
                "locale": "en",
                "interactive_mode": False,
                "hide_in_task_list": True,
                "share_visibility": "private",
                "agent_profile": "lite",
                "structured_output_schema": schema,
            },
        )
        response.raise_for_status()

        payload = response.json()
        task_id = payload.get("task_id")

        if not task_id:
            raise RuntimeError(
                f"Manus did not return task_id: {payload}"
            )

        deadline = time.monotonic() + self.TIMEOUT

        while time.monotonic() < deadline:
            response = self.client.get(
                "/v2/task.listMessages",
                params={
                    "task_id": task_id,
                    "order": "desc",
                    "limit": 50,
                },
            )
            response.raise_for_status()

            payload = response.json()
            messages = payload.get("messages", [])

            for message in messages:
                message_type = message.get("type")

                if message_type == "structured_output_result":
                    result = message.get("structured_output_result", {})

                    if result.get("success") is not True:
                        raise RuntimeError(
                            "Manus structured output failed: "
                            f"{result.get('error', 'Unknown error')}"
                        )

                    return response_schema.model_validate(
                        result["value"]
                    )

                if message_type == "error_message":
                    error = message.get("error_message", {})
                    raise RuntimeError(
                        f"Manus task failed: {error}"
                    )

            statuses = [
                message.get("status_update", {}).get("agent_status")
                for message in messages
                if message.get("type") == "status_update"
            ]

            if "error" in statuses:
                raise RuntimeError(
                    f"Manus task {task_id} failed."
                )

            if "waiting" in statuses:
                raise RuntimeError(
                    f"Manus task {task_id} is waiting for input."
                )

            time.sleep(self.POLL_INTERVAL)

        raise TimeoutError(
            f"Manus task {task_id} exceeded {self.TIMEOUT} seconds."
        )

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
