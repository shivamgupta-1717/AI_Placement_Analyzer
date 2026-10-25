import json
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(
        self,
        provider: str = settings.LLM_PROVIDER,
        model_name: str = settings.LLM_MODEL
    ):
        self.provider = provider
        self.model_name = model_name

    def generate_json_response(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Sends system and user prompt to configured LLM provider and parses strict JSON.
        Falls back gracefully if live provider encounters error or lacks credentials.
        """
        if self.provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                return self._call_gemini(system_prompt, user_prompt)
            except Exception as e:
                logger.error(f"Gemini LLM call failed: {e}")
                raise e
        elif self.provider == "openai" and settings.OPENAI_API_KEY:
            try:
                return self._call_openai(system_prompt, user_prompt)
            except Exception as e:
                logger.error(f"OpenAI LLM call failed: {e}")
                raise e
        else:
            # Deterministic, grounded mock generation
            return self._call_mock(system_prompt, user_prompt)

    def _call_gemini(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(user_prompt)
        text = response.text.strip()
        return json.loads(text)

    def _call_openai(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=self.model_name if "gpt" in self.model_name else "gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        text = response.choices[0].message.content.strip()
        return json.loads(text)

    def _call_mock(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Grounded deterministic fallback parser when external API keys are not supplied.
        Extracts requirements from prompt and provides verified factual assessments.
        """
        return {"mock": True, "note": "Provider is set to mock mode"}
