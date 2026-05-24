"""Multi-image input handler for AuroraAgent."""

import base64
import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"})
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

MIME_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
}


class ImageHandler:
    """Handle multi-image input: validation, encoding, and metadata."""

    def validate_image(self, file_path: str) -> Dict:
        """Validate an image file.

        Checks: file exists, extension supported, file size < 10MB.

        Returns:
            {
                "valid": bool,
                "error": str | None,
                "info": {"size": int, "extension": str, "file_name": str}
            }
        """
        if not file_path:
            return {
                "valid": False,
                "error": "File path is empty",
                "info": {},
            }

        if not os.path.exists(file_path):
            return {
                "valid": False,
                "error": f"File not found: {file_path}",
                "info": {},
            }

        if not os.path.isfile(file_path):
            return {
                "valid": False,
                "error": f"Path is not a file: {file_path}",
                "info": {},
            }

        _, ext = os.path.splitext(file_path)
        ext_lower = ext.lower()

        if ext_lower not in SUPPORTED_EXTENSIONS:
            return {
                "valid": False,
                "error": (
                    f"Unsupported extension: {ext}. "
                    f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
                ),
                "info": {
                    "size": 0,
                    "extension": ext_lower,
                    "file_name": os.path.basename(file_path),
                },
            }

        file_size = os.path.getsize(file_path)

        if file_size > MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            return {
                "valid": False,
                "error": (
                    f"File too large: {size_mb:.2f} MB "
                    f"(max {MAX_FILE_SIZE / (1024 * 1024):.0f} MB)"
                ),
                "info": {
                    "size": file_size,
                    "extension": ext_lower,
                    "file_name": os.path.basename(file_path),
                },
            }

        return {
            "valid": True,
            "error": None,
            "info": {
                "size": file_size,
                "extension": ext_lower,
                "file_name": os.path.basename(file_path),
            },
        }

    def encode_image(self, file_path: str) -> Dict:
        """Read an image file and encode it to base64.

        Returns:
            {"base64": str, "mime_type": str, "size": int}

        Raises:
            FileNotFoundError: if file does not exist.
            ValueError: if extension is unsupported.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        _, ext = os.path.splitext(file_path)
        ext_lower = ext.lower()

        mime_type = MIME_MAP.get(ext_lower)
        if mime_type is None:
            raise ValueError(
                f"Unsupported extension: {ext}. "
                f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )

        file_size = os.path.getsize(file_path)

        with open(file_path, "rb") as f:
            raw = f.read()

        encoded = base64.b64encode(raw).decode("ascii")

        return {
            "base64": encoded,
            "mime_type": mime_type,
            "size": file_size,
        }

    def batch_process(self, file_paths: List[str]) -> Dict:
        """Validate and encode multiple images.

        Returns:
            {
                "results": [{"file_path": str, "valid": bool, ...}],
                "valid_count": int,
                "invalid_count": int,
                "errors": [str, ...]
            }
        """
        results: List[Dict] = []
        errors: List[str] = []

        for path in file_paths:
            validation = self.validate_image(path)

            if not validation["valid"]:
                results.append({
                    "file_path": path,
                    "valid": False,
                    "error": validation["error"],
                    "info": validation["info"],
                })
                errors.append(f"{path}: {validation['error']}")
                continue

            try:
                encoded = self.encode_image(path)
                results.append({
                    "file_path": path,
                    "valid": True,
                    "error": None,
                    "info": validation["info"],
                    "base64": encoded["base64"],
                    "mime_type": encoded["mime_type"],
                    "size": encoded["size"],
                })
            except Exception as exc:
                results.append({
                    "file_path": path,
                    "valid": False,
                    "error": str(exc),
                    "info": validation["info"],
                })
                errors.append(f"{path}: {exc}")

        valid_count = sum(1 for r in results if r["valid"])
        invalid_count = len(results) - valid_count

        return {
            "results": results,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "errors": errors,
        }

    def get_image_summary(self, images: List[Dict]) -> Dict:
        """Generate summary metadata for a list of image info dicts.

        Each item in *images* should have at least "size" and "extension" keys.

        Returns:
            {
                "count": int,
                "total_size": int,
                "total_size_mb": float,
                "types": {ext: count, ...},
                "sizes": {"min": int, "max": int, "avg": float}
            }
        """
        if not images:
            return {
                "count": 0,
                "total_size": 0,
                "total_size_mb": 0.0,
                "types": {},
                "sizes": {"min": 0, "max": 0, "avg": 0.0},
            }

        count = len(images)
        total_size = sum(img.get("size", 0) for img in images)

        type_counts: Dict[str, int] = {}
        for img in images:
            ext = img.get("extension", "unknown")
            type_counts[ext] = type_counts.get(ext, 0) + 1

        sizes = [img.get("size", 0) for img in images]

        return {
            "count": count,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 4),
            "types": type_counts,
            "sizes": {
                "min": min(sizes),
                "max": max(sizes),
                "avg": round(sum(sizes) / len(sizes), 2),
            },
        }

    def supports_vision(self) -> bool:
        """Check if the current model supports vision input.

        GLM-4.7-Flash supports vision natively.
        """
        return True
