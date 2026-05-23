"""
知识产权模块

提供专利辅助、软件著作权辅助、论文大纲生成等功能。
"""

from .patent import PatentAssistant
from .software import SoftwareCopyrightAssistant
from .paper import PaperOutlineGenerator

__all__ = ["PatentAssistant", "SoftwareCopyrightAssistant", "PaperOutlineGenerator"]
