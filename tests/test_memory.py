"""Tests for MemoryManager and ConversationHistory."""

import os
import tempfile

import pytest

from aurora.history import ConversationHistory
from aurora.memory.session_db import MemoryManager


@pytest.fixture
def db():
    """Create a temporary MemoryManager."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    mm = MemoryManager(db_path=path)
    yield mm
    os.unlink(path)


class TestMemoryManager:
    def test_create_session(self, db):
        sid = db.create_or_update_session("test1", {"technology": "AI"})
        assert sid == "test1"

    def test_create_auto_id(self, db):
        sid = db.create_or_update_session("", {"technology": "AI"})
        assert len(sid) == 12

    def test_update_session(self, db):
        db.create_or_update_session("s1", {"technology": "AI"})
        db.create_or_update_session("s1", {"technology": "NLP"})
        data = db.load_session("s1")
        assert data["project_info"]["technology"] == "NLP"

    def test_save_and_load_section(self, db):
        db.create_or_update_session("s1", {"technology": "AI"})
        db.save_section("s1", "executive_summary", "Test content")
        data = db.load_session("s1")
        assert data["sections"]["executive_summary"] == "Test content"

    def test_save_section_versioning(self, db):
        db.create_or_update_session("s1", {})
        db.save_section("s1", "sec1", "v1")
        db.save_section("s1", "sec1", "v2")
        data = db.load_session("s1")
        assert data["sections"]["sec1"] == "v2"

    def test_load_nonexistent_session(self, db):
        assert db.load_session("nonexistent") is None

    def test_list_sessions(self, db):
        db.create_or_update_session("s1", {"project_name": "Project A"})
        db.create_or_update_session("s2", {"project_name": "Project B"})
        sessions = db.list_sessions()
        assert len(sessions) == 2
        names = {s["session_id"] for s in sessions}
        assert names == {"s1", "s2"}

    def test_list_sessions_empty(self, db):
        assert db.list_sessions() == []

    def test_delete_session(self, db):
        db.create_or_update_session("s1", {"technology": "AI"})
        db.save_section("s1", "sec1", "content")
        assert db.delete_session("s1") is True
        assert db.load_session("s1") is None
        assert db.delete_session("nonexistent") is False

    def test_search_sessions(self, db):
        db.create_or_update_session("s1", {"technology": "Artificial Intelligence"})
        db.create_or_update_session("s2", {"technology": "Blockchain"})
        results = db.search_sessions("Artificial")
        assert len(results) == 1
        assert results[0]["session_id"] == "s1"

    def test_cleanup_old_sessions(self, db):
        db.create_or_update_session("s1", {"technology": "AI"})
        db.create_or_update_session("s2", {"technology": "NLP"})
        deleted = db.cleanup_old_sessions(max_age_days=0)
        assert deleted == 2
        assert db.list_sessions() == []

    def test_cleanup_keeps_recent(self, db):
        db.create_or_update_session("s1", {"technology": "AI"})
        deleted = db.cleanup_old_sessions(max_age_days=30)
        assert deleted == 0
        assert len(db.list_sessions()) == 1

    def test_save_and_load_messages(self, db):
        db.create_or_update_session("s1", {})
        db.save_message("s1", "user", "Hello")
        db.save_message("s1", "assistant", "Hi there")
        msgs = db.load_messages("s1")
        assert len(msgs) == 2
        assert msgs[0]["role"] == "user"
        assert msgs[1]["role"] == "assistant"


class TestCategorizedMemory:
    def test_store_and_recall(self, db):
        db.store_memory("preference", "language", "中文优先")
        results = db.recall_memory("中文")
        assert len(results) == 1
        assert results[0]["category"] == "preference"
        assert results[0]["key"] == "language"

    def test_recall_by_category(self, db):
        db.store_memory("preference", "lang", "中文")
        db.store_memory("fact", "user_name", "张三")
        results = db.recall_memory("张三", category="fact")
        assert len(results) == 1
        assert results[0]["key"] == "user_name"

    def test_recall_no_match(self, db):
        db.store_memory("note", "test", "content")
        results = db.recall_memory("nonexistent")
        assert len(results) == 0

    def test_upsert_same_key(self, db):
        db.store_memory("preference", "lang", "中文")
        db.store_memory("preference", "lang", "English")
        results = db.recall_memory("English")
        assert len(results) == 1
        assert results[0]["content"] == "English"

    def test_delete_memory(self, db):
        mid = db.store_memory("note", "test", "content")
        assert db.delete_memory(mid) is True
        assert db.delete_memory(9999) is False

    def test_access_count_increases(self, db):
        db.store_memory("fact", "name", "Alice")
        ctx = db.build_memory_context("Alice")
        assert "Alice" in ctx
        results = db.recall_memory("Alice")
        assert results[0]["access_count"] >= 1

    def test_build_memory_context_empty(self, db):
        ctx = db.build_memory_context("nothing")
        assert ctx == ""

    def test_build_memory_context_format(self, db):
        db.store_memory("preference", "style", "academic")
        ctx = db.build_memory_context("style")
        assert "[preference/style]" in ctx

    def test_list_categories(self, db):
        db.store_memory("preference", "a", "x")
        db.store_memory("fact", "b", "y")
        cats = db.list_memory_categories()
        assert "preference" in cats
        assert "fact" in cats

    def test_recall_ranked_by_access(self, db):
        db.store_memory("fact", "popular", "popular item")
        db.store_memory("fact", "rare", "rare item")
        # Access popular item multiple times
        for _ in range(5):
            db.build_memory_context("popular")
        results = db.recall_memory("item")
        assert results[0]["key"] == "popular"


class TestConversationHistory:
    def test_add_and_get(self):
        h = ConversationHistory()
        h.add("user", "Hello")
        h.add("assistant", "Hi")
        msgs = h.get_messages()
        assert len(msgs) == 2
        assert msgs[0]["content"] == "Hello"

    def test_len(self):
        h = ConversationHistory()
        assert len(h) == 0
        h.add("user", "test")
        assert len(h) == 1

    def test_edit(self):
        h = ConversationHistory()
        h.add("user", "Hello")
        h.add("assistant", "Hi")
        h.add("user", "How are you?")
        assert h.edit(1, "Hey there!") is True
        msgs = h.get_messages()
        assert len(msgs) == 2
        assert msgs[1]["content"] == "Hey there!"

    def test_edit_invalid_index(self):
        h = ConversationHistory()
        h.add("user", "test")
        assert h.edit(5, "new") is False
        assert h.edit(-1, "new") is False

    def test_undo(self):
        h = ConversationHistory()
        h.add("user", "A")
        h.add("assistant", "B")
        h.add("user", "C")
        h.edit(1, "X")
        assert len(h) == 2
        assert h.undo() is True
        assert len(h) == 3
        msgs = h.get_messages()
        assert msgs[1]["content"] == "B"
        assert msgs[2]["content"] == "C"

    def test_undo_empty(self):
        h = ConversationHistory()
        assert h.undo() is False

    def test_redo(self):
        h = ConversationHistory()
        h.add("user", "A")
        h.add("assistant", "B")
        h.edit(1, "X")
        h.undo()
        assert h.redo() is True
        msgs = h.get_messages()
        assert len(msgs) == 2
        assert msgs[1]["content"] == "X"

    def test_redo_empty(self):
        h = ConversationHistory()
        assert h.redo() is False

    def test_clear(self):
        h = ConversationHistory()
        h.add("user", "test")
        h.clear()
        assert len(h) == 0

    def test_messages_are_copies(self):
        h = ConversationHistory()
        h.add("user", "original")
        msgs = h.get_messages()
        msgs[0]["content"] = "modified"
        assert h.get_messages()[0]["content"] == "original"
