"""Tests for CLI argument parsing and subcommand routing."""

import json
import os
import sys
import tempfile

import pytest

from aurora.cli import main


class TestCLIParsing:
    def test_version_flag(self, capsys):
        """Test --version flag."""
        sys.argv = ["aurora", "--version"]
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "0.1.0" in captured.out

    def test_no_args_shows_help(self, capsys):
        """Test no arguments shows help."""
        sys.argv = ["aurora"]
        main()
        captured = capsys.readouterr()
        assert "aurora" in captured.out.lower() or "usage" in captured.out.lower()

    def test_sessions_runs(self, capsys):
        """Test sessions subcommand runs without error."""
        sys.argv = ["aurora", "sessions"]
        main()
        captured = capsys.readouterr()
        assert "ID" in captured.out or "No sessions" in captured.out

    def test_delete_nonexistent(self, capsys):
        """Test delete with non-existent session."""
        sys.argv = ["aurora", "delete", "nonexistent123"]
        main()
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()

    def test_batch_missing_file(self, capsys):
        """Test batch with missing file."""
        sys.argv = ["aurora", "batch", "nonexistent_file.json"]
        with pytest.raises(SystemExit):
            main()

    def test_batch_valid_file(self, capsys):
        """Test batch with a valid JSON tasks file."""
        # Create a minimal tasks file
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        with open(path, "w") as f:
            json.dump(["Say hello"], f)

        out_dir = tempfile.mkdtemp()
        try:
            sys.argv = ["aurora", "batch", path, "--output-dir", out_dir]
            main()
            captured = capsys.readouterr()
            assert "Done:" in captured.out
        finally:
            os.unlink(path)
            for f in os.listdir(out_dir):
                os.unlink(os.path.join(out_dir, f))
            os.rmdir(out_dir)

    def test_chat_help(self, capsys):
        """Test chat --help."""
        sys.argv = ["aurora", "chat", "--help"]
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    def test_exec_help(self, capsys):
        """Test exec --help."""
        sys.argv = ["aurora", "exec", "--help"]
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    def test_generate_help(self, capsys):
        """Test generate --help."""
        sys.argv = ["aurora", "generate", "--help"]
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "--name" in captured.out
        assert "--tech" in captured.out
