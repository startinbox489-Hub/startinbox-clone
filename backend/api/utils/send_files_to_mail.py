"""
send_report_files_via_mail
"""

from typing import Dict, Any
import os

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from api.service.report_generator_service import report_generator_service
from api.repository.user_repo import user_repository
from api.service.resend_email_service import resend_email_service
from api.utils.remove_pdfs_and_docs import remove_pdf_and_doc
from api.utils.task_logger import create_logger

logger = create_logger()


async def send_report_files_via_mail(
    prompt_reply: Dict[str, Any],
    session: AsyncSession,
    user_id: str,
    prompt: str,
) -> None:
    """
    Sends report files to email using resend service.

    Args:
        propmt_reply (dict): The prompt to generate files off of.
        session (AsyncSession): The db async session object
        user_id (str): The current user ID
    """
    try:
        pdf = report_generator_service.export_pdf(
            data=prompt_reply, validated_idea=prompt
        )
        docx = report_generator_service.export_docx(
            data=prompt_reply, validated_idea=prompt
        )

        user = await user_repository.fetch(session=session, user_id=user_id)
        if user and user.phone_number:
            attachments = []
            if pdf:
                pdf_file_path = os.path.join(
                    os.getcwd(), "startup_reports", "pdfs", pdf
                )
                attachments.append(pdf_file_path)
            if docx:
                docx_file_path = os.path.join(
                    os.getcwd(), "startup_reports", "docs", docx
                )
                attachments.append(docx_file_path)

            if docx or pdf:
                context_data = None
                if user.firstname:
                    context_data = {"firstname": user.firstname}
                email_response = resend_email_service.send_email(
                    to_email=user.email,
                    attachments=attachments,
                    context_data=context_data,
                    subject="🚀 Your startup report is ready!",
                )
                if email_response:
                    res_id = email_response.get("id")
                    if docx and res_id:
                        remove_pdf_and_doc(filename=docx, is_docx=True)
                    if pdf and res_id:
                        remove_pdf_and_doc(filename=pdf, is_pdf=True)
    except HTTPException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.detail,
        ) from exc
    except Exception as exc:
        logger.warning("could not send email file reports: %s", str(exc))
