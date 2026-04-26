"""
Reports Service
"""

import os
from fastapi.responses import FileResponse
from fastapi import HTTPException, status

from api.service.url_secret_service import URLSecretService
from api.utils.task_logger import create_logger

logger = create_logger(":: ReportsService ::")


REPORTS_DIR = f"{os.getcwd()}/startup_reports"  # /docs or /pdfs


class ReportsService:
    """
    REPORTS SERVICE
    """

    def serve_file(self, filename: str, token: str, expires: int | str) -> FileResponse:
        """
        Serves file for twillio.

        Args:
            filename (str): The name of the file having a file extension of either .pdf or .docx
        Returns:
            FileResponse
        Raises:
            HTTPException 404: if file is missing.
        """
        try:
            expires_int = int(expires)
        except TypeError as exc:
            logger.error("Error typecasting expires_in from url: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="expires is invalid",
            ) from exc

        URLSecretService.verify_signed_url(
            expires=expires_int, token=token, filename=filename
        )
        file_path = ""
        if filename.endswith("pdf"):
            file_path += os.path.join(f"{REPORTS_DIR}/pdfs", filename)
        else:
            file_path += os.path.join(f"{REPORTS_DIR}/docs", filename)
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="file not found"
            )
        return FileResponse(
            file_path,
            media_type="application/octet-stream",  # auto-detect
            filename=filename,
        )


reports_service = ReportsService()
