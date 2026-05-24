import os
from typing import Dict, Optional


class I18nManager:
    """Simple internationalization manager."""

    DEFAULT_LOCALE = "zh"
    SUPPORTED_LOCALES = ["zh", "en"]

    def __init__(self, locale: str = None):
        self._locale = locale or os.environ.get("AURORA_LOCALE", self.DEFAULT_LOCALE)
        self._translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()

    def _load_translations(self):
        """Load built-in translations."""
        self._translations = {
            "zh": {
                # System
                "system.greeting": "欢迎使用AuroraAgent",
                "system.farewell": "感谢使用AuroraAgent",
                "system.error": "发生错误",
                "system.processing": "正在处理...",
                # Commands
                "cmd.help": "显示帮助信息",
                "cmd.tools": "列出可用工具",
                "cmd.history": "显示对话历史",
                "cmd.edit": "编辑消息",
                "cmd.undo": "撤销操作",
                "cmd.exit": "退出",
                # Business Plan
                "bp.generating": "正在生成商业计划书",
                "bp.complete": "商业计划书生成完成",
                "bp.exporting": "正在导出",
                "bp.sections.executive_summary": "执行摘要",
                "bp.sections.project_overview": "项目概述",
                "bp.sections.market_analysis": "市场分析",
                "bp.sections.business_model": "商业模式",
                "bp.sections.financial_analysis": "财务分析",
                "bp.sections.team": "团队介绍",
                "bp.sections.risk_management": "风险管理",
                # Evaluation
                "eval.scoring": "正在评估",
                "eval.complete": "评估完成",
                "eval.score": "得分",
                "eval.dimension.innovation": "创新性",
                "eval.dimension.business": "商业性",
                "eval.dimension.team": "团队情况",
                "eval.dimension.social_impact": "社会效益",
                "eval.dimension.feasibility": "可行性",
                # Competition
                "comp.searching": "正在搜索竞赛",
                "comp.matching": "正在匹配赛道",
                "comp.no_match": "未找到匹配的赛道",
                # Defense
                "defense.generating": "正在生成答辩问题",
                "defense.scoring": "正在评分",
                # Team
                "team.analyzing": "正在分析团队",
                "team.incomplete": "团队配置不完整",
                # Errors
                "error.not_found": "未找到",
                "error.invalid_input": "无效的输入",
                "error.timeout": "操作超时",
                "error.api_key": "API密钥未配置",
            },
            "en": {
                # System
                "system.greeting": "Welcome to AuroraAgent",
                "system.farewell": "Thank you for using AuroraAgent",
                "system.error": "An error occurred",
                "system.processing": "Processing...",
                # Commands
                "cmd.help": "Show help information",
                "cmd.tools": "List available tools",
                "cmd.history": "Show conversation history",
                "cmd.edit": "Edit message",
                "cmd.undo": "Undo operation",
                "cmd.exit": "Exit",
                # Business Plan
                "bp.generating": "Generating business plan",
                "bp.complete": "Business plan generation complete",
                "bp.exporting": "Exporting",
                "bp.sections.executive_summary": "Executive Summary",
                "bp.sections.project_overview": "Project Overview",
                "bp.sections.market_analysis": "Market Analysis",
                "bp.sections.business_model": "Business Model",
                "bp.sections.financial_analysis": "Financial Analysis",
                "bp.sections.team": "Team",
                "bp.sections.risk_management": "Risk Management",
                # Evaluation
                "eval.scoring": "Evaluating",
                "eval.complete": "Evaluation complete",
                "eval.score": "Score",
                "eval.dimension.innovation": "Innovation",
                "eval.dimension.business": "Business Viability",
                "eval.dimension.team": "Team",
                "eval.dimension.social_impact": "Social Impact",
                "eval.dimension.feasibility": "Feasibility",
                # Competition
                "comp.searching": "Searching competitions",
                "comp.matching": "Matching tracks",
                "comp.no_match": "No matching tracks found",
                # Defense
                "defense.generating": "Generating defense questions",
                "defense.scoring": "Scoring",
                # Team
                "team.analyzing": "Analyzing team",
                "team.incomplete": "Team configuration incomplete",
                # Errors
                "error.not_found": "Not found",
                "error.invalid_input": "Invalid input",
                "error.timeout": "Operation timed out",
                "error.api_key": "API key not configured",
            },
        }

    def t(self, key: str, locale: str = None, **kwargs) -> str:
        """Translate a key. Supports format kwargs."""
        loc = locale or self._locale
        text = self._translations.get(loc, {}).get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, IndexError):
                return text
        return text

    def set_locale(self, locale: str):
        """Set current locale."""
        if locale in self.SUPPORTED_LOCALES:
            self._locale = locale

    def get_locale(self) -> str:
        """Get current locale."""
        return self._locale

    def add_translation(self, locale: str, key: str, value: str):
        """Add a custom translation."""
        if locale not in self._translations:
            self._translations[locale] = {}
        self._translations[locale][key] = value

    def get_all_keys(self, locale: str = None) -> list:
        """Get all translation keys for a locale."""
        loc = locale or self._locale
        return list(self._translations.get(loc, {}).keys())

    def get_section_title(self, section_id: str, locale: str = None) -> str:
        """Get localized section title."""
        return self.t(f"bp.sections.{section_id}", locale)


# Global instance
_instance: Optional[I18nManager] = None


def get_i18n(locale: str = None) -> I18nManager:
    """Get or create the global I18nManager singleton."""
    global _instance
    if _instance is None:
        _instance = I18nManager(locale)
    elif locale and locale != _instance.get_locale():
        _instance.set_locale(locale)
    return _instance
