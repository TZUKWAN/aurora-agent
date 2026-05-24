import docx
import os
import json
import logging

logger = logging.getLogger(__name__)

class SecretOutlineParser:
    """Parses proprietary docx outline and injects custom prompts."""

    SECTION_MAP = {
        "执行摘要": "executive_summary",
        "项目概述": "project_overview",
        "项目背景": "project_overview", # sometimes named this way
        "市场分析": "market_analysis",
        "产品服务": "product_service",
        "产品与服务": "product_service",
        "商业模式": "business_model",
        "营销策略": "marketing_strategy",
        "运营计划": "operation_plan",
        "团队介绍": "team_introduction",
        "财务分析": "financial_analysis",
        "风险评估": "risk_assessment"
    }

    def __init__(self, docx_path: str = None):
        if not docx_path:
            # default to relative local file
            docx_path = os.path.join(os.getcwd(), "商业计划书大纲2026.docx")
        self.docx_path = docx_path
        self._prompts_cache = None

    def get_section_prompts(self) -> dict:
        """Returns a dict of standard section ids mapped to proprietary prompts."""
        if self._prompts_cache is not None:
            return self._prompts_cache

        if not os.path.exists(self.docx_path):
            logger.warning(f"Proprietary outline not found at {self.docx_path}. Using fallbacks.")
            return {}

        try:
            doc = docx.Document(self.docx_path)
        except Exception as e:
            logger.error(f"Failed to load outline docx: {e}")
            return {}

        raw_sections = {}
        current_title = None
        current_content = []

        # Simple greedy parser: short unnumbered lines are likely titles
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            
            # Heuristic for section titles (short, usually without numbers at start if it's pure section name)
            # Or we can just look for keywords in short lines
            if len(text) < 15 and any(k in text for k in self.SECTION_MAP.keys()):
                if current_title:
                    raw_sections[current_title] = "\n".join(current_content)
                    current_content = []
                current_title = text
            else:
                if current_title:
                    current_content.append(text)
        
        # Flush last section
        if current_title:
            raw_sections[current_title] = "\n".join(current_content)

        # Normalize keys to standard system section ids
        mapped_prompts = {}
        for raw_title, prompt_text in raw_sections.items():
            for zh_key, sys_key in self.SECTION_MAP.items():
                if zh_key in raw_title:
                    if sys_key not in mapped_prompts:
                        mapped_prompts[sys_key] = prompt_text
                    else:
                        mapped_prompts[sys_key] += "\n" + prompt_text

        self._prompts_cache = mapped_prompts
        return mapped_prompts
