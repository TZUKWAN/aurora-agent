"""Tests for instruction loader."""

import os
import tempfile

import pytest

from aurora.instructions.loader import InstructionLoader


@pytest.fixture
def workspace(tmp_path):
    """Create a temporary workspace with instruction files."""
    # Create AGENTS.md
    agents = """# Project instructions

[system]
Project-specific system behavior.
Always respond in English.

[writing-style]
Use formal academic tone.
"""
    (tmp_path / "AGENTS.md").write_text(agents, encoding="utf-8")

    # Create override
    override = """# Override

[writing-style]
Override: Use casual tone instead.
"""
    (tmp_path / "AGENTS.override.md").write_text(override, encoding="utf-8")

    return str(tmp_path)


class TestInstructionLoader:
    def test_parse_sections(self):
        content = """[system]
System instructions here.

[writing-style]
Be formal.
"""
        sections = InstructionLoader._parse_sections(content)
        assert "system" in sections
        assert "writing_style" in sections or "writing-style" in sections

    def test_load_from_workspace(self, workspace):
        loader = InstructionLoader(workspace)
        sections = loader.load_instructions()
        assert "system" in sections
        assert "Project-specific" in sections["system"]

    def test_override_merges(self, workspace):
        loader = InstructionLoader(workspace)
        sections = loader.load_instructions()
        assert "writing-style" in sections
        # Should have both project and override content
        assert "casual tone" in sections["writing-style"]

    def test_empty_workspace(self, tmp_path):
        loader = InstructionLoader(str(tmp_path))
        sections = loader.load_instructions()
        # No instruction files = no sections
        assert isinstance(sections, dict)

    def test_get_system_prompt_addition(self, workspace):
        loader = InstructionLoader(workspace)
        addition = loader.get_system_prompt_addition()
        assert "system" in addition
        assert len(addition) > 0

    def test_list_loaded_files(self, workspace):
        loader = InstructionLoader(workspace)
        files = loader.list_loaded_files()
        assert len(files) >= 2  # project + override

    def test_no_instructions_returns_empty(self, tmp_path):
        loader = InstructionLoader(str(tmp_path))
        addition = loader.get_system_prompt_addition()
        assert addition == ""
