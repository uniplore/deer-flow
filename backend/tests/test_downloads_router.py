"""Unit tests for downloads router."""

import asyncio
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.responses import Response

import app.gateway.routers.downloads as downloads_router


@pytest.fixture
def app():
    """Create a FastAPI app with downloads router."""
    app = FastAPI()
    app.include_router(downloads_router.router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    with TestClient(app) as client:
        yield client


class TestDownloadFile:
    """Tests for download_file endpoint."""

    def test_download_file_returns_binary_content(self, tmp_path, monkeypatch) -> None:
        """Test that download returns file content as binary stream."""
        outputs_dir = tmp_path / "outputs"
        outputs_dir.mkdir()
        file_path = outputs_dir / "report.pdf"
        file_content = b"%PDF-1.4\n%fake pdf content"
        file_path.write_bytes(file_content)

        monkeypatch.setattr(downloads_router, "get_outputs_dir", lambda _thread_id: outputs_dir)

        app = FastAPI()
        app.include_router(downloads_router.router)

        with TestClient(app) as client:
            response = client.get("/api/threads/test-thread/downloads/report.pdf")

        assert response.status_code == 200
        assert response.content == file_content
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers.get("content-disposition", "")
        assert "report.pdf" in response.headers.get("content-disposition", "")

    def test_download_file_with_text_content(self, tmp_path, monkeypatch) -> None:
        """Test downloading a text file returns correct content."""
        outputs_dir = tmp_path / "outputs"
        outputs_dir.mkdir()
        file_path = outputs_dir / "notes.txt"
        file_content = b"Hello, this is a test file!"
        file_path.write_bytes(file_content)

        monkeypatch.setattr(downloads_router, "get_outputs_dir", lambda _thread_id: outputs_dir)

        app = FastAPI()
        app.include_router(downloads_router.router)

        with TestClient(app) as client:
            response = client.get("/api/threads/test-thread/downloads/notes.txt")

        assert response.status_code == 200
        assert response.content == file_content
        assert response.headers["content-type"] == "text/plain"

    def test_download_file_with_chinese_filename(self, tmp_path, monkeypatch) -> None:
        """Test downloading file with Chinese characters in filename."""
        outputs_dir = tmp_path / "outputs"
        outputs_dir.mkdir()
        file_path = outputs_dir / "报告.pdf"
        file_content = b"%PDF-1.4\n%chinese filename test"
        file_path.write_bytes(file_content)

        monkeypatch.setattr(downloads_router, "get_outputs_dir", lambda _thread_id: outputs_dir)

        app = FastAPI()
        app.include_router(downloads_router.router)

        with TestClient(app) as client:
            response = client.get("/api/threads/test-thread/downloads/%E6%8A%A5%E5%91%8A.pdf")

        assert response.status_code == 200
        assert response.content == file_content
        assert "attachment" in response.headers.get("content-disposition", "")

    def test_download_file_not_found(self, tmp_path, monkeypatch) -> None:
        """Test 404 response when file does not exist."""
        outputs_dir = tmp_path / "outputs"
        outputs_dir.mkdir()

        monkeypatch.setattr(downloads_router, "get_outputs_dir", lambda _thread_id: outputs_dir)

        app = FastAPI()
        app.include_router(downloads_router.router)

        with TestClient(app) as client:
            response = client.get("/api/threads/test-thread/downloads/nonexistent.pdf")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_download_file_invalid_thread_id(self, tmp_path, monkeypatch) -> None:
        """Test 400 response for invalid thread_id."""
        monkeypatch.setattr(
            downloads_router,
            "get_outputs_dir",
            lambda _thread_id: (_ for _ in ()).throw(ValueError("Invalid thread_id")),
        )

        app = FastAPI()
        app.include_router(downloads_router.router)

        with TestClient(app) as client:
            response = client.get("/api/threads/test-thread/downloads/file.pdf")

        assert response.status_code == 400

    def test_download_file_path_traversal_rejected(self, tmp_path, monkeypatch) -> None:
        """Test that path traversal attempts are rejected."""
        outputs_dir = tmp_path / "outputs"
        outputs_dir.mkdir()

        # Create a file outside outputs dir
        secret_file = tmp_path / "secret.txt"
        secret_file.write_bytes(b"secret data")

        monkeypatch.setattr(downloads_router, "get_outputs_dir", lambda _thread_id: outputs_dir)

        app = FastAPI()
        app.include_router(downloads_router.router)

        with TestClient(app) as client:
            # Try to access file using path traversal
            response = client.get("/api/threads/test-thread/downloads/../secret.txt")

        assert response.status_code == 400

    def test_download_file_directory_instead_of_file(self, tmp_path, monkeypatch) -> None:
        """Test 400 response when path is a directory."""
        outputs_dir = tmp_path / "outputs"
        outputs_dir.mkdir()
        subdir = outputs_dir / "subdir"
        subdir.mkdir()

        monkeypatch.setattr(downloads_router, "get_outputs_dir", lambda _thread_id: outputs_dir)

        app = FastAPI()
        app.include_router(downloads_router.router)

        with TestClient(app) as client:
            response = client.get("/api/threads/test-thread/downloads/subdir")

        assert response.status_code == 400
        assert "not a file" in response.json()["detail"].lower()

    def test_download_file_binary_image(self, tmp_path, monkeypatch) -> None:
        """Test downloading binary image file."""
        outputs_dir = tmp_path / "outputs"
        outputs_dir.mkdir()
        file_path = outputs_dir / "image.png"
        # Minimal PNG header
        file_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
        file_path.write_bytes(file_content)

        monkeypatch.setattr(downloads_router, "get_outputs_dir", lambda _thread_id: outputs_dir)

        app = FastAPI()
        app.include_router(downloads_router.router)

        with TestClient(app) as client:
            response = client.get("/api/threads/test-thread/downloads/image.png")

        assert response.status_code == 200
        assert response.content == file_content
        assert response.headers["content-type"] == "image/png"


class TestListDownloadableFiles:
    """Tests for list_downloadable_files endpoint."""

    def test_list_files_returns_empty_for_nonexistent_directory(self, tmp_path, monkeypatch) -> None:
        """Test that listing returns empty when directory doesn't exist."""
        outputs_dir = tmp_path / "outputs"
        # Don't create the directory

        monkeypatch.setattr(downloads_router, "get_outputs_dir", lambda _thread_id: outputs_dir)

        app = FastAPI()
        app.include_router(downloads_router.router)

        with TestClient(app) as client:
            response = client.get("/api/threads/test-thread/downloads")

        assert response.status_code == 200
        data = response.json()
        assert data["files"] == []
        assert data["count"] == 0
        assert data["thread_id"] == "test-thread"

    def test_list_files_returns_file_list(self, tmp_path, monkeypatch) -> None:
        """Test that listing returns correct file list."""
        outputs_dir = tmp_path / "outputs"
        outputs_dir.mkdir()
        (outputs_dir / "report.pdf").write_bytes(b"pdf content")
        (outputs_dir / "notes.txt").write_bytes(b"text content")

        monkeypatch.setattr(downloads_router, "get_outputs_dir", lambda _thread_id: outputs_dir)

        app = FastAPI()
        app.include_router(downloads_router.router)

        with TestClient(app) as client:
            response = client.get("/api/threads/test-thread/downloads")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["files"]) == 2

        filenames = [f["filename"] for f in data["files"]]
        assert "report.pdf" in filenames
        assert "notes.txt" in filenames

        for file_info in data["files"]:
            assert "size" in file_info
            assert "download_url" in file_info
            assert "modified" in file_info
            assert file_info["download_url"].startswith("/api/threads/test-thread/downloads/")

    def test_list_files_excludes_directories(self, tmp_path, monkeypatch) -> None:
        """Test that listing excludes subdirectories."""
        outputs_dir = tmp_path / "outputs"
        outputs_dir.mkdir()
        (outputs_dir / "file.txt").write_bytes(b"content")
        (outputs_dir / "subdir").mkdir()

        monkeypatch.setattr(downloads_router, "get_outputs_dir", lambda _thread_id: outputs_dir)

        app = FastAPI()
        app.include_router(downloads_router.router)

        with TestClient(app) as client:
            response = client.get("/api/threads/test-thread/downloads")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["files"][0]["filename"] == "file.txt"

    def test_list_files_sorted_by_name(self, tmp_path, monkeypatch) -> None:
        """Test that files are sorted by name."""
        outputs_dir = tmp_path / "outputs"
        outputs_dir.mkdir()
        (outputs_dir / "z_file.txt").write_bytes(b"z")
        (outputs_dir / "a_file.txt").write_bytes(b"a")
        (outputs_dir / "m_file.txt").write_bytes(b"m")

        monkeypatch.setattr(downloads_router, "get_outputs_dir", lambda _thread_id: outputs_dir)

        app = FastAPI()
        app.include_router(downloads_router.router)

        with TestClient(app) as client:
            response = client.get("/api/threads/test-thread/downloads")

        assert response.status_code == 200
        data = response.json()
        filenames = [f["filename"] for f in data["files"]]
        assert filenames == ["a_file.txt", "m_file.txt", "z_file.txt"]
