"""
Remove files
"""

import os
from api.utils.task_logger import create_logger

logger = create_logger(__name__)


def remove_pdf_and_doc(
    filename: str, is_pdf: bool = False, is_docx: bool = False
) -> str | None:
    """
    Removes a file with the given name from the 'pdfs' or 'docs' subdirectory
    within the 'startup_reports' folder.

    Args:
        filename(str): The name of the file to remove (e.g., "report-2025").
        is_pdf(bool): If True, looks for the file in the 'pdfs' directory and adds '.pdf' extension.
        is_docx(bool): If True, looks for the file in the 'docs' directory and adds '.docx' extension.
    Returns:
        The full path of the file removed, or None if no action was taken.
    Raises:
        RuntimeError: If both is_pdf and is_docx are True.
    """

    if is_pdf and is_docx:
        raise RuntimeError(
            "is_pdf and is_docx cannot be True simultaneously. Please select only one file type."
        )

    if not is_pdf and not is_docx:
        raise ValueError("At least one of 'is_pdf' or 'is_docx' must be True.")

    cwd = os.getcwd()
    base_dir = os.path.join(cwd, "startup_reports")
    file_path = None
    extension = None

    if is_pdf:
        file_path = os.path.join(base_dir, "pdfs", filename)
        extension = ".pdf"
    elif is_docx:
        file_path = os.path.join(base_dir, "docs", filename)
        extension = ".docx"

    if file_path and extension and not file_path.lower().endswith(extension):
        file_path += extension

    if file_path:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info("Successfully removed file: %s", file_path)
                return file_path
            except OSError as exc:
                logger.error("Error removing file %s, Error: %s", file_path, str(exc))

    logger.warning("File not found, skipping removal: %s", file_path)
    return file_path
