"""Image tools registration for AuroraAgent."""

import json
import logging

from aurora.image.handler import ImageHandler

logger = logging.getLogger(__name__)

_handler = ImageHandler()


def _register_tools(registry):
    """Register image tools to the registry."""

    registry.register(
        "image_validate",
        "Validate an image file (check extension, size, existence)",
        {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute or relative path to the image file",
                },
            },
            "required": ["file_path"],
        },
        _image_validate_handler,
    )

    registry.register(
        "image_encode",
        "Encode an image file to base64 string",
        {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute or relative path to the image file",
                },
            },
            "required": ["file_path"],
        },
        _image_encode_handler,
    )

    registry.register(
        "image_batch_process",
        "Validate and encode multiple image files in batch",
        {
            "type": "object",
            "properties": {
                "file_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of image file paths to process",
                },
            },
            "required": ["file_paths"],
        },
        _image_batch_process_handler,
    )

    registry.register(
        "image_summary",
        "Generate summary metadata for a list of images",
        {
            "type": "object",
            "properties": {
                "images": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of image info dicts (each with 'size' and 'extension')",
                },
            },
            "required": ["images"],
        },
        _image_summary_handler,
    )


def _image_validate_handler(args):
    """Handle image_validate tool call."""
    try:
        file_path = args.get("file_path", "")
        result = _handler.validate_image(file_path)
        return result
    except Exception as exc:
        logger.exception("image_validate failed")
        return {"error": f"Validation failed: {exc}"}


def _image_encode_handler(args):
    """Handle image_encode tool call."""
    try:
        file_path = args.get("file_path", "")
        result = _handler.encode_image(file_path)
        return result
    except FileNotFoundError as exc:
        return {"error": str(exc)}
    except ValueError as exc:
        return {"error": str(exc)}
    except Exception as exc:
        logger.exception("image_encode failed")
        return {"error": f"Encoding failed: {exc}"}


def _image_batch_process_handler(args):
    """Handle image_batch_process tool call."""
    try:
        file_paths = args.get("file_paths", [])
        if not isinstance(file_paths, list):
            return {"error": "file_paths must be a list of strings"}
        result = _handler.batch_process(file_paths)
        return result
    except Exception as exc:
        logger.exception("image_batch_process failed")
        return {"error": f"Batch processing failed: {exc}"}


def _image_summary_handler(args):
    """Handle image_summary tool call."""
    try:
        images = args.get("images", [])
        if not isinstance(images, list):
            return {"error": "images must be a list of objects"}
        result = _handler.get_image_summary(images)
        return result
    except Exception as exc:
        logger.exception("image_summary failed")
        return {"error": f"Summary generation failed: {exc}"}
