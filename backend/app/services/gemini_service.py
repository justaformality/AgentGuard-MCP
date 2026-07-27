import json
from typing import Any

from app.config import settings

try:
    from google import genai  # type: ignore
    from google.genai import types  # type: ignore
except ImportError:
    genai = None
    types = None


class GeminiServiceError(Exception):
    pass


class GeminiService:
    """Safe optional wrapper around Gemini; callers can always fall back deterministically."""

    def __init__(self):
        self.model = settings.gemini_model
        self.api_key = settings.gemini_api_key

    def _get_client(self):
        if genai is None or types is None:
            raise GeminiServiceError(
                "google-genai is not installed. "
                "Install backend requirements to enable AI-powered tools."
            )

        if not self.api_key:
            raise GeminiServiceError(
                "GEMINI_API_KEY is missing. "
                "Add it to backend/.env before using AI-powered mode."
            )

        return genai.Client(api_key=self.api_key)

    def generate_json(self, prompt: str) -> dict[str, Any]:
        client = self._get_client()

        try:
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )

            raw_text = response.text or ""

            try:
                return json.loads(raw_text)

            except json.JSONDecodeError as exc:
                raise GeminiServiceError(
                    f"Gemini returned invalid JSON. "
                    f"Raw response: {raw_text[:500]}"
                ) from exc

        except GeminiServiceError:
            raise

        except Exception as exc:
            raise GeminiServiceError(
                f"Gemini API call failed: {exc}"
            ) from exc


gemini_service = GeminiService()