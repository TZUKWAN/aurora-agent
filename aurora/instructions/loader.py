"""Load and merge hierarchical instruction files (AGENTS.md)."""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

INSTRUCTION_FILENAME = "AGENTS.md"
OVERRIDE_FILENAME = "AGENTS.override.md"
DEFAULT_GLOBAL_DIR = os.path.expanduser("~/.aurora")


class InstructionLoader:
    """Load instructions from a 3-level hierarchy:
    1. Global: ~/.aurora/AGENTS.md
    2. Project: <workspace>/AGENTS.md
    3. Override: <workspace>/AGENTS.override.md (highest priority)
    """

    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace = workspace_path or os.getcwd()

    def load_instructions(self) -> Dict[str, str]:
        """Load and merge instructions from all levels."""
        sections = {}

        # Level 1: Global
        global_path = os.path.join(DEFAULT_GLOBAL_DIR, INSTRUCTION_FILENAME)
        global_content = self._read_file(global_path)
        if global_content:
            self._merge_sections(sections, self._parse_sections(global_content))

        # Level 2: Project
        project_path = os.path.join(self.workspace, INSTRUCTION_FILENAME)
        project_content = self._read_file(project_path)
        if project_content:
            self._merge_sections(sections, self._parse_sections(project_content))

        # Level 3: Override
        override_path = os.path.join(self.workspace, OVERRIDE_FILENAME)
        override_content = self._read_file(override_path)
        if override_content:
            self._merge_sections(sections, self._parse_sections(override_content))

        return sections

    def get_system_prompt_addition(self) -> str:
        """Get merged instructions as a string for system prompt injection."""
        sections = self.load_instructions()
        if not sections:
            return ""

        parts = []
        for section_name, content in sections.items():
            parts.append(f"[{section_name}]\n{content}")

        return "\n\n".join(parts)

    @staticmethod
    def _read_file(path: str) -> Optional[str]:
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception as e:
            logger.debug(f"Cannot read instruction file {path}: {e}")
        return None

    @staticmethod
    def _parse_sections(content: str) -> Dict[str, str]:
        """Parse content into sections marked by [section_name] headers."""
        sections = {}
        current_section = "general"
        current_lines = []

        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                # Save previous section
                if current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = stripped[1:-1]
                current_lines = []
            elif stripped and not stripped.startswith("#"):
                current_lines.append(line)

        # Save last section
        if current_lines:
            sections[current_section] = "\n".join(current_lines).strip()

        return sections

    @staticmethod
    def _merge_sections(target: Dict[str, str], source: Dict[str, str]):
        """Merge source sections into target. Source overrides target."""
        for key, value in source.items():
            if key in target:
                target[key] = target[key] + "\n" + value
            else:
                target[key] = value

    def list_loaded_files(self) -> List[str]:
        """List which instruction files exist."""
        files = []
        for label, path in [
            ("global", os.path.join(DEFAULT_GLOBAL_DIR, INSTRUCTION_FILENAME)),
            ("project", os.path.join(self.workspace, INSTRUCTION_FILENAME)),
            ("override", os.path.join(self.workspace, OVERRIDE_FILENAME)),
        ]:
            if os.path.exists(path):
                files.append(f"{label}: {path}")
        return files
