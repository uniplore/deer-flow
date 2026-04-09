"""Download router for handling file downloads from outputs directory."""

import logging
import mimetypes
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from deerflow.config.paths import get_paths
from deerflow.uploads.manager import (
    PathTraversalError,
    normalize_filename,
    validate_path_traversal,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/downloads", tags=["downloads"])


def get_outputs_dir(thread_id: str) -> Path:
    """Return the outputs directory path for a thread.

    Args:
        thread_id: The thread ID.

    Returns:
        Path to the outputs directory.
    """
    return get_paths().sandbox_outputs_dir(thread_id)


@router.get(
    "",
    summary="Download File",
    description="Download a file from a thread's outputs directory (agent-generated artifacts) as binary stream.",
)
async def download_file(
    thread_id: str,
    filename: str,
) -> Response:
    """Download a file from a thread's outputs directory as binary stream.

    Args:
        thread_id: The thread ID.
        filename: Name of the file to download.

    Returns:
        Response with file content as binary stream (bytes).

    Raises:
        HTTPException:
            - 400 if filename is invalid or path traversal detected
            - 404 if file not found
            - 500 if download fails
    """
    try:
        outputs_dir = get_outputs_dir(thread_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        safe_filename = normalize_filename(filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid filename: {str(e)}")

    file_path = outputs_dir / safe_filename

    # Validate path traversal
    try:
        validate_path_traversal(file_path, outputs_dir)
    except PathTraversalError:
        raise HTTPException(status_code=400, detail="Invalid path")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")

    if not file_path.is_file():
        raise HTTPException(status_code=400, detail=f"Path is not a file: {filename}")

    logger.info(f"Downloading file: {safe_filename} from thread {thread_id}")

    # Read file as bytes
    try:
        file_content = file_path.read_bytes()
    except Exception as e:
        logger.error(f"Failed to read file {safe_filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

    # Determine MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    media_type = mime_type or "application/octet-stream"

    # Build headers
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{quote(safe_filename)}",
        "Content-Length": str(len(file_content)),
    }

    return Response(
        content=file_content,
        media_type=media_type,
        headers=headers,
    )


@router.get(
    "/list",
    summary="List Downloadable Files",
    description="List all files available for download in a thread's outputs directory (agent-generated artifacts).",
)
async def list_downloadable_files(thread_id: str) -> dict:
    """List all files available for download in a thread's outputs directory.

    Args:
        thread_id: The thread ID.

    Returns:
        Dict with list of downloadable files.

    Raises:
        HTTPException:
            - 400 if thread_id is invalid
    """
    try:
        outputs_dir = get_outputs_dir(thread_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not outputs_dir.exists():
        return {"files": [], "count": 0, "thread_id": thread_id}

    files = []
    for entry in sorted(outputs_dir.iterdir(), key=lambda e: e.name):
        if entry.is_file():
            stat = entry.stat()
            files.append({
                "filename": entry.name,
                "size": stat.st_size,
                "download_url": f"/api/threads/{thread_id}/downloads/{quote(entry.name, safe='')}",
                "modified": stat.st_mtime,
            })

    return {"files": files, "count": len(files), "thread_id": thread_id}
