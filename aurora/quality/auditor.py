"""Quality auditor for business plans."""

import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

WEAK_PHRASES = [
    "将不断优化", "持续提升", "进一步完善", "不断改进",
    "will continue to improve", "constantly optimize",
    "不断提升", "逐步完善", "进一步加强", "积极推进",
]


class PlanAuditor:
    """Audit business plan quality."""

    def __init__(self, config=None):
        self.config = config

    def audit(self, plan: Dict) -> Dict:
        """Audit a complete plan. Returns audit report."""
        sections = plan.get("sections", {})
        issues = []

        # 1. Word count checks
        issues.extend(self._check_word_counts(sections))

        # 2. Empty content checks
        issues.extend(self._check_empty_sections(sections))

        # 3. Weak phrase detection
        issues.extend(self._check_weak_phrases(sections))

        # 4. Duplicate content detection
        issues.extend(self._check_duplicates(sections))

        # 5. Consistency checks
        issues.extend(self._check_consistency(sections))

        score = self._calculate_score(issues, len(sections))

        return {
            "score": score,
            "total_issues": len(issues),
            "critical": [i for i in issues if i["severity"] == "critical"],
            "warnings": [i for i in issues if i["severity"] == "warning"],
            "info": [i for i in issues if i["severity"] == "info"],
            "issues": issues,
        }

    def audit_section(self, section_id: str, content: str, project_info: Dict = None) -> Dict:
        """Audit a single section."""
        issues = []

        if not content or not content.strip():
            issues.append({"section": section_id, "severity": "critical",
                           "message": f"Section {section_id} is empty"})
        else:
            char_count = len(content)
            if char_count < 100:
                issues.append({"section": section_id, "severity": "warning",
                               "message": f"Section {section_id} too short ({char_count} chars)"})

            for phrase in WEAK_PHRASES:
                if phrase in content:
                    issues.append({"section": section_id, "severity": "info",
                                   "message": f"Vague phrase '{phrase}' in {section_id}"})

        return {"section_id": section_id, "issues": issues}

    def _check_word_counts(self, sections: Dict) -> List[Dict]:
        issues = []
        min_chars = 100
        for sid, sec in sections.items():
            content = sec.get("content", "") if isinstance(sec, dict) else str(sec)
            if content and len(content) < min_chars:
                issues.append({
                    "section": sid, "severity": "warning",
                    "message": f"Section {sid} is too short ({len(content)} chars, min {min_chars})"
                })
        return issues

    def _check_empty_sections(self, sections: Dict) -> List[Dict]:
        issues = []
        required = ["executive_summary", "project_overview", "market_analysis",
                     "business_model", "financial_analysis"]
        for sid in required:
            if sid not in sections:
                issues.append({"section": sid, "severity": "critical",
                               "message": f"Missing required section: {sid}"})
                continue
            sec = sections[sid]
            content = sec.get("content", "") if isinstance(sec, dict) else str(sec)
            if not content.strip():
                issues.append({"section": sid, "severity": "critical",
                               "message": f"Section {sid} is empty"})
        return issues

    def _check_weak_phrases(self, sections: Dict) -> List[Dict]:
        issues = []
        for sid, sec in sections.items():
            content = sec.get("content", "") if isinstance(sec, dict) else str(sec)
            for phrase in WEAK_PHRASES:
                if phrase in content:
                    issues.append({"section": sid, "severity": "info",
                                   "message": f"Vague phrase '{phrase}' found"})
        return issues

    def _check_duplicates(self, sections: Dict) -> List[Dict]:
        issues = []
        contents = {}
        for sid, sec in sections.items():
            content = sec.get("content", "") if isinstance(sec, dict) else str(sec)
            # Normalize for comparison
            normalized = re.sub(r'\s+', '', content.lower())
            contents[sid] = normalized

        sids = list(contents.keys())
        for i in range(len(sids)):
            for j in range(i + 1, len(sids)):
                if not contents[sids[i]] or not contents[sids[j]]:
                    continue
                # Check if one is a substring of the other (>50% overlap)
                shorter = min(len(contents[sids[i]]), len(contents[sids[j]]))
                if shorter == 0:
                    continue
                if contents[sids[i]] in contents[sids[j]] or contents[sids[j]] in contents[sids[i]]:
                    if shorter > 50:
                        issues.append({"section": f"{sids[i]},{sids[j]}", "severity": "warning",
                                       "message": f"Duplicate content between {sids[i]} and {sids[j]}"})
        return issues

    def _check_consistency(self, sections: Dict) -> List[Dict]:
        issues = []
        # Basic consistency: check if financial numbers appear in both financial section and exec summary
        financial = sections.get("financial_analysis", {})
        fin_content = financial.get("content", "") if isinstance(financial, dict) else str(financial)
        exec_summary = sections.get("executive_summary", {})
        exec_content = exec_summary.get("content", "") if isinstance(exec_summary, dict) else str(exec_summary)

        # Extract numbers from both
        fin_nums = set(re.findall(r'\d+\.?\d*[万亿]?', fin_content))
        exec_nums = set(re.findall(r'\d+\.?\d*[万亿]?', exec_content))

        # This is a basic check - just flag if financial section has numbers but exec summary doesn't mention any
        if fin_nums and not exec_nums:
            issues.append({"section": "executive_summary", "severity": "info",
                           "message": "Financial summary may be missing from executive summary"})

        return issues

    def _calculate_score(self, issues: List[Dict], section_count: int) -> float:
        base = 100.0
        for issue in issues:
            if issue["severity"] == "critical":
                base -= 15
            elif issue["severity"] == "warning":
                base -= 5
            elif issue["severity"] == "info":
                base -= 2
        return max(0.0, round(base, 1))
