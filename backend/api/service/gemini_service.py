"""
GOOGLE GEMINI SERVICE
"""

from datetime import date

from fastapi import BackgroundTasks, HTTPException, status
from google.genai import Client
from google.genai.types import (
    # GenerateContentResponse,
    GenerateContentConfig,
    ThinkingConfig,
    GoogleSearch,
    Tool,
)

from api.core.config import settings
from api.utils.master_prompts import STARTER_PLAN_PROMPT
from api.utils.task_logger import create_logger
from api.service.resend_email_service import resend_email_service

logger = create_logger(":: GoogleGeminiService ::")


class GoogleGeminiService:
    """
    GOOGLE GEMINI SERVICE
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.client = Client(api_key=settings.google_gemini_api_key)
        self.model_id = settings.google_gemini_model

        return

    def generate_idea(
        self,
        prompt: str,
        background_tasks: BackgroundTasks,
        plan_prompt: str = STARTER_PLAN_PROMPT,
    ) -> str:
        """
        Generates ideas
        """

        try:
            full_prompt = f"{plan_prompt}\n\nUser Idea: {prompt}"

            config = GenerateContentConfig(
                thinking_config=ThinkingConfig(
                    include_thoughts=False, thinking_budget=0
                ),  # Disable thinking
                # response_mime_type="application/json",
                # Enable Google Search Grounding for more accurate data
                tools=[Tool(google_search=GoogleSearch())],
            )
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=full_prompt,
                config=config,
            )

            # if the model was blocked or empty
            if not response.text or response.text == "":
                logger.warning("Model returned an empty response.")
                raise HTTPException(
                    status_code=status.HTTP_417_EXPECTATION_FAILED,
                    detail="Model returned an empty response. Please try again later",
                )
            return response.text.replace("`", "").replace("json", "")
        except HTTPException as exc:
            raise HTTPException(
                status_code=exc.status_code,
                detail=exc.detail,
            ) from exc
        except Exception as exc:
            self._handle_exception(exc=exc, background_tasks=background_tasks)
            return ""

    def _handle_exception(self, exc: Exception, background_tasks: BackgroundTasks):
        """
        Centralized error handling with exponential backoff logic or
        admin notification based on error type.
        """
        error_string = str(exc).upper()
        logger.error("Error in Gemini Service: %s", error_string)

        background_tasks.add_task(
            resend_email_service.send_email,
            to_email=settings.admin_email,
            template_name="error-report.html",
            context_data={"current_year": date.today().year, "exception": str(exc)},
            subject="🚨 Attention! A.I API Error Occurred",
        )

        if "503" in error_string or "OVERLOADED" in error_string:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail="The model is currently overloaded. Please try again in a few moments.",
            ) from exc

        if "429" in error_string:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail="Rate limit exceeded. Please slow down.",
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="We encountered an issue validating your idea. Please try again later.",
        ) from exc


gemini_service = GoogleGeminiService()
