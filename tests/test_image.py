"""Tests for image handler and image tools."""

import base64
import json
import os

import pytest

from aurora.image.handler import (
    MAX_FILE_SIZE,
    MIME_MAP,
    SUPPORTED_EXTENSIONS,
    ImageHandler,
)
from aurora.tools.image_tools import _register_tools
from aurora.tools.registry import ToolRegistry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# Minimal 1x1 red PNG (67 bytes)
_MINIMAL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
)

# Minimal JPEG (smallest valid JFIF)
_MINIMAL_JPG = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c"
    b"\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c"
    b"\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01"
    b"\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01"
    b"\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08"
    b"\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04"
    b"\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07\"q\x14"
    b"\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19"
    b"\x1a%&'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87"
    b"\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6"
    b"\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5"
    b"\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3"
    b"\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa"
    b"\xff\xda\x00\x08\x01\x01\x00\x00?\x00T\x9f\xff\xd9"
)


@pytest.fixture
def handler():
    return ImageHandler()


@pytest.fixture
def test_png(tmp_path):
    """Create a minimal valid PNG file."""
    path = tmp_path / "test.png"
    path.write_bytes(_MINIMAL_PNG)
    return str(path)


@pytest.fixture
def test_jpg(tmp_path):
    """Create a minimal valid JPG file."""
    path = tmp_path / "test.jpg"
    path.write_bytes(_MINIMAL_JPG)
    return str(path)


@pytest.fixture
def test_gif(tmp_path):
    """Create a minimal valid GIF file."""
    # GIF87a 1x1 transparent
    gif_data = (
        b"GIF87a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff"
        b"\x00\x00\x00!\xf9\x04\x00\x00\x00\x00\x00,"
        b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
    )
    path = tmp_path / "test.gif"
    path.write_bytes(gif_data)
    return str(path)


# ---------------------------------------------------------------------------
# validate_image tests
# ---------------------------------------------------------------------------


class TestValidateImage:
    def test_valid_png(self, handler, test_png):
        result = handler.validate_image(test_png)
        assert result["valid"] is True
        assert result["error"] is None
        assert result["info"]["extension"] == ".png"
        assert result["info"]["size"] > 0
        assert result["info"]["file_name"] == "test.png"

    def test_valid_jpg(self, handler, test_jpg):
        result = handler.validate_image(test_jpg)
        assert result["valid"] is True
        assert result["error"] is None
        assert result["info"]["extension"] == ".jpg"

    def test_valid_gif(self, handler, test_gif):
        result = handler.validate_image(test_gif)
        assert result["valid"] is True
        assert result["info"]["extension"] == ".gif"

    def test_nonexistent_file(self, handler):
        result = handler.validate_image("/nonexistent/path/image.png")
        assert result["valid"] is False
        assert "not found" in result["error"].lower()

    def test_unsupported_extension(self, handler, tmp_path):
        path = tmp_path / "test.txt"
        path.write_text("not an image")
        result = handler.validate_image(str(path))
        assert result["valid"] is False
        assert "unsupported" in result["error"].lower()

    def test_empty_path(self, handler):
        result = handler.validate_image("")
        assert result["valid"] is False
        assert result["error"] == "File path is empty"

    def test_directory_path(self, handler, tmp_path):
        result = handler.validate_image(str(tmp_path))
        assert result["valid"] is False
        assert "not a file" in result["error"].lower()

    def test_oversized_file(self, handler, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "aurora.image.handler.MAX_FILE_SIZE", 10
        )
        path = tmp_path / "big.png"
        path.write_bytes(b"\x00" * 100)
        result = handler.validate_image(str(path))
        assert result["valid"] is False
        assert "too large" in result["error"].lower()

    def test_case_insensitive_extension(self, handler, tmp_path):
        path = tmp_path / "test.PNG"
        path.write_bytes(_MINIMAL_PNG)
        result = handler.validate_image(str(path))
        assert result["valid"] is True
        assert result["info"]["extension"] == ".png"

    def test_webp_extension(self, handler, tmp_path):
        path = tmp_path / "test.webp"
        path.write_bytes(b"RIFF\x00\x00\x00\x00WEBP")
        result = handler.validate_image(str(path))
        assert result["valid"] is True
        assert result["info"]["extension"] == ".webp"

    def test_bmp_extension(self, handler, tmp_path):
        path = tmp_path / "test.bmp"
        path.write_bytes(b"BM\x00\x00\x00\x00\x00\x00")
        result = handler.validate_image(str(path))
        assert result["valid"] is True
        assert result["info"]["extension"] == ".bmp"


# ---------------------------------------------------------------------------
# encode_image tests
# ---------------------------------------------------------------------------


class TestEncodeImage:
    def test_encode_png(self, handler, test_png):
        result = handler.encode_image(test_png)
        assert "base64" in result
        assert result["mime_type"] == "image/png"
        assert result["size"] == len(_MINIMAL_PNG)

        # Verify round-trip
        decoded = base64.b64decode(result["base64"])
        assert decoded == _MINIMAL_PNG

    def test_encode_jpg(self, handler, test_jpg):
        result = handler.encode_image(test_jpg)
        assert result["mime_type"] == "image/jpeg"
        assert "base64" in result

    def test_encode_nonexistent(self, handler):
        with pytest.raises(FileNotFoundError):
            handler.encode_image("/nonexistent/image.png")

    def test_encode_unsupported(self, handler, tmp_path):
        path = tmp_path / "test.txt"
        path.write_text("hello")
        with pytest.raises(ValueError, match="Unsupported"):
            handler.encode_image(str(path))


# ---------------------------------------------------------------------------
# batch_process tests
# ---------------------------------------------------------------------------


class TestBatchProcess:
    def test_batch_valid_files(self, handler, test_png, test_jpg, test_gif):
        result = handler.batch_process([test_png, test_jpg, test_gif])
        assert result["valid_count"] == 3
        assert result["invalid_count"] == 0
        assert result["errors"] == []
        assert len(result["results"]) == 3

        for r in result["results"]:
            assert r["valid"] is True
            assert "base64" in r
            assert "mime_type" in r

    def test_batch_mixed_valid_invalid(self, handler, test_png, tmp_path):
        bad_path = str(tmp_path / "nonexistent.png")
        txt_path = tmp_path / "test.txt"
        txt_path.write_text("not an image")

        result = handler.batch_process([test_png, bad_path, str(txt_path)])
        assert result["valid_count"] == 1
        assert result["invalid_count"] == 2
        assert len(result["errors"]) == 2

    def test_batch_empty_list(self, handler):
        result = handler.batch_process([])
        assert result["valid_count"] == 0
        assert result["invalid_count"] == 0
        assert result["results"] == []

    def test_batch_all_invalid(self, handler):
        result = handler.batch_process(["/a.png", "/b.jpg"])
        assert result["valid_count"] == 0
        assert result["invalid_count"] == 2


# ---------------------------------------------------------------------------
# get_image_summary tests
# ---------------------------------------------------------------------------


class TestGetImageSummary:
    def test_summary_normal(self, handler):
        images = [
            {"size": 1024, "extension": ".png"},
            {"size": 2048, "extension": ".jpg"},
            {"size": 512, "extension": ".png"},
        ]
        result = handler.get_image_summary(images)
        assert result["count"] == 3
        assert result["total_size"] == 3584
        assert result["types"] == {".png": 2, ".jpg": 1}
        assert result["sizes"]["min"] == 512
        assert result["sizes"]["max"] == 2048
        assert result["sizes"]["avg"] == 1194.67

    def test_summary_empty(self, handler):
        result = handler.get_image_summary([])
        assert result["count"] == 0
        assert result["total_size"] == 0
        assert result["types"] == {}

    def test_summary_single_image(self, handler):
        images = [{"size": 5000, "extension": ".webp"}]
        result = handler.get_image_summary(images)
        assert result["count"] == 1
        assert result["total_size"] == 5000
        assert result["sizes"]["min"] == result["sizes"]["max"] == 5000

    def test_summary_missing_keys(self, handler):
        images = [{}, {"size": 100}]
        result = handler.get_image_summary(images)
        assert result["count"] == 2
        assert result["total_size"] == 100
        assert result["types"]["unknown"] == 2


# ---------------------------------------------------------------------------
# supports_vision tests
# ---------------------------------------------------------------------------


class TestSupportsVision:
    def test_returns_true(self, handler):
        assert handler.supports_vision() is True


# ---------------------------------------------------------------------------
# Tool registration tests
# ---------------------------------------------------------------------------


class TestToolRegistration:
    def test_image_tools_registered(self):
        registry = ToolRegistry()
        _register_tools(registry)
        tools = registry.list_tools()

        assert "image_validate" in tools
        assert "image_encode" in tools
        assert "image_batch_process" in tools
        assert "image_summary" in tools

    def test_tool_schemas(self):
        registry = ToolRegistry()
        _register_tools(registry)
        schemas = registry.get_schemas()

        tool_names = [s["function"]["name"] for s in schemas]
        assert "image_validate" in tool_names
        assert "image_encode" in tool_names
        assert "image_batch_process" in tool_names
        assert "image_summary" in tool_names

        for schema in schemas:
            if schema["function"]["name"].startswith("image_"):
                assert "description" in schema["function"]
                assert "parameters" in schema["function"]


# ---------------------------------------------------------------------------
# Tool dispatch tests
# ---------------------------------------------------------------------------


class TestToolDispatch:
    def test_dispatch_validate_valid(self, test_png):
        registry = ToolRegistry()
        _register_tools(registry)

        result_json = registry.dispatch("image_validate", {"file_path": test_png})
        result = json.loads(result_json)
        assert result["valid"] is True
        assert result["error"] is None

    def test_dispatch_validate_invalid(self):
        registry = ToolRegistry()
        _register_tools(registry)

        result_json = registry.dispatch(
            "image_validate", {"file_path": "/nonexistent.png"}
        )
        result = json.loads(result_json)
        assert result["valid"] is False
        assert result["error"] is not None

    def test_dispatch_encode(self, test_png):
        registry = ToolRegistry()
        _register_tools(registry)

        result_json = registry.dispatch("image_encode", {"file_path": test_png})
        result = json.loads(result_json)
        assert "base64" in result
        assert result["mime_type"] == "image/png"

    def test_dispatch_encode_error(self):
        registry = ToolRegistry()
        _register_tools(registry)

        result_json = registry.dispatch(
            "image_encode", {"file_path": "/nonexistent.png"}
        )
        result = json.loads(result_json)
        assert "error" in result

    def test_dispatch_batch(self, test_png, test_jpg):
        registry = ToolRegistry()
        _register_tools(registry)

        result_json = registry.dispatch(
            "image_batch_process",
            {"file_paths": [test_png, test_jpg]},
        )
        result = json.loads(result_json)
        assert result["valid_count"] == 2
        assert result["invalid_count"] == 0

    def test_dispatch_summary(self):
        registry = ToolRegistry()
        _register_tools(registry)

        images = [{"size": 100, "extension": ".png"}]
        result_json = registry.dispatch("image_summary", {"images": images})
        result = json.loads(result_json)
        assert result["count"] == 1
        assert result["total_size"] == 100

    def test_dispatch_summary_invalid_input(self):
        registry = ToolRegistry()
        _register_tools(registry)

        result_json = registry.dispatch("image_summary", {"images": "not a list"})
        result = json.loads(result_json)
        assert "error" in result

    def test_dispatch_unknown_tool(self):
        registry = ToolRegistry()
        _register_tools(registry)

        result_json = registry.dispatch("image_nonexistent", {})
        result = json.loads(result_json)
        assert "error" in result
