"""Plan optimizer that fixes issues found by the auditor."""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class PlanOptimizer:
    """Optimize plan based on audit report. Max 3 iterations."""

    MAX_ITERATIONS = 3

    def __init__(self, config=None):
        self.config = config
        self.llm_client = self._init_llm()

    def _init_llm(self):
        try:
            import os
            if self.config is None:
                from aurora.config import load_config
                self.config = load_config()

            api_key = self.config.model.api_key or os.environ.get("AURORA_API_KEY")
            base_url = self.config.model.base_url or os.environ.get("AURORA_BASE_URL")
            if not api_key:
                return None

            from openai import OpenAI
            return OpenAI(api_key=api_key, base_url=base_url)
        except Exception:
            return None

    def optimize(self, plan: Dict, audit_report: Dict) -> Dict:
        """Optimize plan based on audit issues. Returns updated plan."""
        critical_issues = audit_report.get("critical", [])
        warning_issues = audit_report.get("warnings", [])

        if not critical_issues and not warning_issues:
            return plan

        sections = plan.get("sections", {})

        # Fix critical issues: empty sections
        for issue in critical_issues:
            section_id = issue.get("section", "")
            if section_id in sections:
                sec = sections[section_id]
                content = sec.get("content", "") if isinstance(sec, dict) else str(sec)
                if not content.strip():
                    sections[section_id] = self._generate_placeholder(section_id, sec)

        # Fix warning issues: short sections
        for issue in warning_issues:
            section_id = issue.get("section", "")
            if section_id in sections:
                sec = sections[section_id]
                content = sec.get("content", "") if isinstance(sec, dict) else str(sec)
                if content and len(content) < 100:
                    expanded = self._expand_section(section_id, content)
                    if isinstance(sec, dict):
                        sec["content"] = expanded
                    else:
                        sections[section_id] = {"title": section_id, "content": expanded, "word_count": 0}

        plan["sections"] = sections
        return plan

    def optimize_section(self, section_id: str, content: str, issues: List[Dict]) -> str:
        """Optimize a single section based on its issues."""
        if not content.strip():
            return self._generate_placeholder_text(section_id)

        if any("too short" in i.get("message", "") for i in issues):
            return self._expand_section(section_id, content)

        return content

    def _generate_placeholder(self, section_id: str, sec) -> Dict:
        """Generate a placeholder for empty sections."""
        title = sec.get("title", section_id) if isinstance(sec, dict) else section_id
        return {
            "title": title,
            "content": self._generate_placeholder_text(section_id),
            "word_count": 0,
        }

    def _generate_placeholder_text(self, section_id: str) -> str:
        """Generate minimal placeholder text."""
        templates = {
            "executive_summary": "This project addresses a significant market need through innovative technology solutions. The team brings strong expertise and the business model demonstrates clear revenue potential.",
            "project_overview": "The project aims to solve real-world problems by leveraging cutting-edge technology. Our solution provides unique value to the target market with a clear competitive advantage.",
            "market_analysis": "The target market shows strong growth potential with increasing demand for technology-driven solutions. Our analysis identifies key market segments and competitive positioning opportunities.",
            "business_model": "The business model is built on sustainable revenue streams with clear cost structures. Multiple income sources ensure financial resilience and growth potential.",
            "financial_analysis": "Financial projections show a clear path to profitability with manageable cost structures. The funding plan supports key milestones and growth objectives.",
        }
        return templates.get(section_id, "Content to be developed.")

    def _expand_section(self, section_id: str, content: str) -> str:
        """Try to expand a short section using LLM, or add template content."""
        if self.llm_client:
            try:
                import os, json
                model_name = self.config.model.name or os.environ.get("AURORA_MODEL", "glm-4.7-flash")
                resp = self.llm_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "Expand the following business plan section to at least 200 characters. Keep the same language. Return only the expanded text."},
                        {"role": "user", "content": f"Section: {section_id}\nCurrent content: {content}"},
                    ],
                    temperature=0.7,
                    max_tokens=1024,
                )
                expanded = resp.choices[0].message.content or ""
                if not expanded.strip():
                    rc = getattr(resp.choices[0].message, 'reasoning_content', None)
                    if rc and rc.strip():
                        expanded = rc
                if len(expanded) > len(content):
                    return expanded
            except Exception as e:
                logger.debug(f"LLM expansion failed: {e}")

        # Fallback: append template
        return content + "\n\n" + self._generate_placeholder_text(section_id)
