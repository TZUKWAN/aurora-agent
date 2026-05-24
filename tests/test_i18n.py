"""Tests for aurora.i18n module."""

import os
import pytest

from aurora.i18n import I18nManager, get_i18n
from aurora.i18n.manager import _instance as _global_instance_ref


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the global singleton between tests."""
    import aurora.i18n.manager as mod
    original = mod._instance
    mod._instance = None
    yield
    mod._instance = original


class TestI18nManagerCreation:
    """Test I18nManager instantiation."""

    def test_default_locale_is_zh(self):
        mgr = I18nManager()
        assert mgr.get_locale() == "zh"

    def test_explicit_zh_locale(self):
        mgr = I18nManager(locale="zh")
        assert mgr.get_locale() == "zh"

    def test_explicit_en_locale(self):
        mgr = I18nManager(locale="en")
        assert mgr.get_locale() == "en"

    def test_env_var_locale(self, monkeypatch):
        monkeypatch.setenv("AURORA_LOCALE", "en")
        mgr = I18nManager()
        assert mgr.get_locale() == "en"

    def test_env_var_overridden_by_explicit(self, monkeypatch):
        monkeypatch.setenv("AURORA_LOCALE", "en")
        mgr = I18nManager(locale="zh")
        assert mgr.get_locale() == "zh"


class TestTranslation:
    """Test the t() method."""

    def test_zh_translation(self):
        mgr = I18nManager(locale="zh")
        assert mgr.t("system.greeting") == "欢迎使用AuroraAgent"

    def test_en_translation(self):
        mgr = I18nManager(locale="en")
        assert mgr.t("system.greeting") == "Welcome to AuroraAgent"

    def test_override_locale_per_call(self):
        mgr = I18nManager(locale="zh")
        assert mgr.t("system.greeting", locale="en") == "Welcome to AuroraAgent"

    def test_unknown_key_returns_key(self):
        mgr = I18nManager()
        assert mgr.t("nonexistent.key") == "nonexistent.key"

    def test_format_kwargs(self):
        mgr = I18nManager()
        mgr.add_translation("zh", "test.greet", "你好, {name}!")
        assert mgr.t("test.greet", name="刘总") == "你好, 刘总!"

    def test_format_kwargs_missing_key_returns_unformatted(self):
        mgr = I18nManager()
        mgr.add_translation("zh", "test.template", "值: {value}")
        # Missing kwarg -> falls back to unformatted string
        result = mgr.t("test.template", other="x")
        assert result == "值: {value}"


class TestSetLocale:
    """Test locale switching."""

    def test_set_locale_to_en(self):
        mgr = I18nManager(locale="zh")
        mgr.set_locale("en")
        assert mgr.get_locale() == "en"
        assert mgr.t("system.greeting") == "Welcome to AuroraAgent"

    def test_set_locale_to_zh(self):
        mgr = I18nManager(locale="en")
        mgr.set_locale("zh")
        assert mgr.get_locale() == "zh"
        assert mgr.t("system.greeting") == "欢迎使用AuroraAgent"

    def test_set_locale_unsupported_ignored(self):
        mgr = I18nManager(locale="zh")
        mgr.set_locale("fr")
        assert mgr.get_locale() == "zh"


class TestAddTranslation:
    """Test custom translations."""

    def test_add_to_existing_locale(self):
        mgr = I18nManager()
        mgr.add_translation("zh", "custom.key", "自定义值")
        assert mgr.t("custom.key") == "自定义值"

    def test_add_to_new_locale(self):
        mgr = I18nManager()
        mgr.add_translation("fr", "custom.key", "Valeur")
        assert mgr.t("custom.key", locale="fr") == "Valeur"

    def test_add_overwrites_existing(self):
        mgr = I18nManager()
        original = mgr.t("system.greeting")
        mgr.add_translation("zh", "system.greeting", "新问候")
        assert mgr.t("system.greeting") == "新问候"
        assert mgr.t("system.greeting") != original


class TestGetAllKeys:
    """Test key listing."""

    def test_returns_list(self):
        mgr = I18nManager()
        keys = mgr.get_all_keys()
        assert isinstance(keys, list)
        assert len(keys) > 0

    def test_zh_keys_match_en_keys(self):
        mgr = I18nManager()
        zh_keys = set(mgr.get_all_keys("zh"))
        en_keys = set(mgr.get_all_keys("en"))
        assert zh_keys == en_keys, (
            f"Key mismatch between zh and en. "
            f"Missing in zh: {en_keys - zh_keys}. "
            f"Missing in en: {zh_keys - en_keys}"
        )

    def test_specific_locale_keys(self):
        mgr = I18nManager()
        en_keys = mgr.get_all_keys("en")
        assert "system.greeting" in en_keys
        assert "cmd.exit" in en_keys
        assert "bp.sections.team" in en_keys


class TestGetSectionTitle:
    """Test section title helper."""

    def test_zh_section_title(self):
        mgr = I18nManager(locale="zh")
        assert mgr.get_section_title("market_analysis") == "市场分析"

    def test_en_section_title(self):
        mgr = I18nManager(locale="en")
        assert mgr.get_section_title("market_analysis") == "Market Analysis"

    def test_unknown_section_returns_key(self):
        mgr = I18nManager()
        result = mgr.get_section_title("nonexistent")
        assert result == "bp.sections.nonexistent"


class TestGetI18nSingleton:
    """Test the get_i18n factory/singleton."""

    def test_returns_i18n_instance(self):
        mgr = get_i18n()
        assert isinstance(mgr, I18nManager)

    def test_singleton_same_instance(self):
        a = get_i18n()
        b = get_i18n()
        assert a is b

    def test_singleton_with_locale(self):
        mgr = get_i18n(locale="en")
        assert mgr.get_locale() == "en"

    def test_singleton_locale_update(self):
        get_i18n(locale="zh")
        mgr = get_i18n(locale="en")
        assert mgr.get_locale() == "en"

    def test_default_locale_zh(self):
        mgr = get_i18n()
        assert mgr.get_locale() == "zh"


class TestCompleteness:
    """Verify both locales have identical key sets and non-empty values."""

    def test_all_keys_exist_in_both_locales(self):
        mgr = I18nManager()
        zh = mgr._translations["zh"]
        en = mgr._translations["en"]

        zh_keys = set(zh.keys())
        en_keys = set(en.keys())

        assert zh_keys == en_keys, (
            f"Key mismatch. Only in zh: {zh_keys - en_keys}. "
            f"Only in en: {en_keys - zh_keys}"
        )

    def test_all_values_non_empty(self):
        mgr = I18nManager()
        for locale in ["zh", "en"]:
            for key, value in mgr._translations[locale].items():
                assert value, f"Empty value for {locale}.{key}"

    def test_no_duplicate_values_cause_issue(self):
        """Ensure translations dict is well-formed (no None values)."""
        mgr = I18nManager()
        for locale in ["zh", "en"]:
            for key, value in mgr._translations[locale].items():
                assert isinstance(value, str), (
                    f"Non-string value for {locale}.{key}: {type(value)}"
                )
