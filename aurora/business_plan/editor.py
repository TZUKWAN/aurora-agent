"""Business plan outline editor."""

import difflib
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PlanEditor:
    """Manage editing state of a business plan."""

    def __init__(self, plan: Dict, config=None):
        self.original_plan = plan
        self.plan = {
            "metadata": dict(plan.get("metadata", {})),
            "sections": {
                k: dict(v) if isinstance(v, dict) else {"title": k, "content": str(v)}
                for k, v in plan.get("sections", {}).items()
            },
        }
        self.config = config

    def update_section(self, section_id: str, new_content: str) -> bool:
        """Update content of a section."""
        if section_id not in self.plan["sections"]:
            return False
        self.plan["sections"][section_id]["content"] = new_content
        return True

    def regenerate_section(self, section_id: str, instructions: str = "") -> Optional[str]:
        """Regenerate a section using LLM with optional instructions."""
        if section_id not in self.plan["sections"]:
            return None

        current = self.plan["sections"][section_id].get("content", "")

        if self.config:
            try:
                import os, json
                from openai import OpenAI
                api_key = self.config.model.api_key or os.environ.get("AURORA_API_KEY")
                base_url = self.config.model.base_url or os.environ.get("AURORA_BASE_URL")
                if not api_key:
                    return current

                client = OpenAI(api_key=api_key, base_url=base_url)
                model_name = self.config.model.name or os.environ.get("AURORA_MODEL", "glm-4.7-flash")

                prompt = f"Rewrite this business plan section. Instructions: {instructions}\n\nCurrent content:\n{current}"
                resp = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "You are a business plan writer. Rewrite based on instructions."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                    max_tokens=2048,
                )
                content = resp.choices[0].message.content or ""
                if not content.strip():
                    rc = getattr(resp.choices[0].message, 'reasoning_content', None)
                    if rc and rc.strip():
                        content = rc

                self.plan["sections"][section_id]["content"] = content
                return content
            except Exception as e:
                logger.debug(f"LLM regeneration failed: {e}")

        return current

    def reorder_sections(self, new_order: List[str]) -> bool:
        """Reorder sections by providing a new key order."""
        old_sections = self.plan["sections"]
        new_sections = {}
        for sid in new_order:
            if sid in old_sections:
                new_sections[sid] = old_sections[sid]
        # Add remaining sections not in new_order
        for sid, sec in old_sections.items():
            if sid not in new_sections:
                new_sections[sid] = sec
        self.plan["sections"] = new_sections
        return True

    def merge_sections(self, section_ids: List[str], new_title: str = "") -> bool:
        """Merge multiple sections into one."""
        if len(section_ids) < 2:
            return False

        merged_content = []
        for sid in section_ids:
            sec = self.plan["sections"].get(sid)
            if not sec:
                continue
            title = sec.get("title", sid) if isinstance(sec, dict) else sid
            content = sec.get("content", "") if isinstance(sec, dict) else str(sec)
            merged_content.append(f"### {title}\n{content}")

            # Remove from plan
            del self.plan["sections"][sid]

        merged_id = "_".join(section_ids)
        self.plan["sections"][merged_id] = {
            "title": new_title or " & ".join(section_ids),
            "content": "\n\n".join(merged_content),
        }
        return True

    def split_section(self, section_id: str, split_points: List[int]) -> bool:
        """Split a section at given character positions."""
        if section_id not in self.plan["sections"]:
            return False

        content = self.plan["sections"][section_id].get("content", "")
        if not content or not split_points:
            return False

        # Split content at positions
        parts = []
        prev = 0
        for pos in sorted(split_points):
            if 0 < pos < len(content):
                parts.append(content[prev:pos])
                prev = pos
        parts.append(content[prev:])

        if len(parts) < 2:
            return False

        # Remove original, add splits
        del self.plan["sections"][section_id]
        for i, part in enumerate(parts):
            self.plan["sections"][f"{section_id}_{i+1}"] = {
                "title": f"{section_id} (Part {i+1})",
                "content": part.strip(),
            }
        return True

    def get_diff(self) -> str:
        """Show diff between original and current plan."""
        orig_lines = []
        for sid, sec in self.original_plan.get("sections", {}).items():
            content = sec.get("content", "") if isinstance(sec, dict) else str(sec)
            orig_lines.extend(content.split("\n"))

        curr_lines = []
        for sid, sec in self.plan["sections"].items():
            content = sec.get("content", "") if isinstance(sec, dict) else str(sec)
            curr_lines.extend(content.split("\n"))

        diff = difflib.unified_diff(orig_lines, curr_lines, lineterm="")
        return "\n".join(diff)

    def validate_plan(self) -> Dict:
        """Validate plan completeness."""
        issues = []
        required = [
            "executive_summary", "project_overview", "market_analysis",
            "business_model", "financial_analysis",
        ]

        for sid in required:
            sec = self.plan["sections"].get(sid)
            if not sec:
                issues.append({"section": sid, "issue": "missing"})
                continue
            content = sec.get("content", "") if isinstance(sec, dict) else str(sec)
            if not content.strip():
                issues.append({"section": sid, "issue": "empty"})
            elif len(content) < 100:
                issues.append({"section": sid, "issue": "too_short", "length": len(content)})

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "section_count": len(self.plan["sections"]),
            "total_chars": sum(
                len(sec.get("content", "")) if isinstance(sec, dict) else len(str(sec))
                for sec in self.plan["sections"].values()
            ),
        }

    def to_dict(self) -> Dict:
        """Return current plan as dict."""
        return dict(self.plan)
