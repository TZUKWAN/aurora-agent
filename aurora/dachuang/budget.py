"""Budget generator and validator for Dachuang applications."""

import logging
from typing import Dict, List, Optional

from aurora.models.dachuang import BudgetItem

logger = logging.getLogger(__name__)

INNOVATION_CATEGORIES = ["资料费", "调研差旅费", "实验材料费", "论文版面费", "会议费", "其他"]

ENTREPRENEURSHIP_CATEGORIES = [
    "市场调研费",
    "产品开发费",
    "营销推广费",
    "差旅交通费",
    "办公费用",
    "其他",
]

# Default allocation ratios for each category
INNOVATION_ALLOCATION = {
    "资料费": 0.15,
    "调研差旅费": 0.25,
    "实验材料费": 0.30,
    "论文版面费": 0.15,
    "会议费": 0.10,
    "其他": 0.05,
}

ENTREPRENEURSHIP_ALLOCATION = {
    "市场调研费": 0.20,
    "产品开发费": 0.35,
    "营销推广费": 0.20,
    "差旅交通费": 0.10,
    "办公费用": 0.10,
    "其他": 0.05,
}

# Default justification templates for each category
JUSTIFICATION_TEMPLATES = {
    "资料费": "用于购买图书、文献检索、打印复印等资料费用",
    "调研差旅费": "用于外出调研、走访、参加学术活动等差旅费用",
    "实验材料费": "用于购买实验耗材、试剂、器件等实验材料",
    "论文版面费": "用于学术论文的版面费、出版费",
    "会议费": "用于参加学术会议、研讨会等会议费用",
    "其他": "用于项目执行过程中的其他必要支出",
    "市场调研费": "用于目标市场调研、用户访谈、问卷调查等费用",
    "产品开发费": "用于产品原型开发、技术验证、测试设备等费用",
    "营销推广费": "用于产品推广、品牌建设、渠道拓展等费用",
    "差旅交通费": "用于商务洽谈、客户拜访、市场考察等差旅费用",
    "办公费用": "用于办公场地、设备租赁、日常运营等费用",
}


class BudgetGenerator:
    """Generate and validate budgets for Dachuang applications."""

    def _get_categories(self, project_type: str) -> list:
        if project_type == "entrepreneurship":
            return ENTREPRENEURSHIP_CATEGORIES
        return INNOVATION_CATEGORIES

    def _get_allocation(self, project_type: str) -> dict:
        if project_type == "entrepreneurship":
            return ENTREPRENEURSHIP_ALLOCATION
        return INNOVATION_ALLOCATION

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_budget(
        self,
        project_info: dict,
        total_amount: float,
        project_type: str = "innovation",
    ) -> list:
        """Generate budget items with suggested allocation.

        Args:
            project_info: Project details dictionary.
            total_amount: Total budget amount in CNY.
            project_type: "innovation" or "entrepreneurship".

        Returns:
            List of budget item dictionaries with category, amount, and justification.
        """
        if total_amount <= 0:
            total_amount = 10000.0

        allocation = self._get_allocation(project_type)
        categories = self._get_categories(project_type)

        items = []

        for i, category in enumerate(categories):
            ratio = allocation.get(category, 0.05)
            amount = round(total_amount * ratio, 2)

            # For the last category, assign remaining to avoid rounding errors
            if i == len(categories) - 1:
                allocated_so_far = sum(item.amount for item in items)
                amount = round(total_amount - allocated_so_far, 2)

            justification = JUSTIFICATION_TEMPLATES.get(
                category, "项目相关支出"
            )

            # Customize justification with project info
            tech = project_info.get("technology", "")
            if tech and category in ("实验材料费", "产品开发费"):
                justification = f"用于{tech}相关的实验材料和技术开发"

            items.append(BudgetItem(
                category=category,
                amount=amount,
                justification=justification,
            ))

        return items

    def validate_budget(
        self,
        items: list,
        max_amount: Optional[float] = None,
    ) -> dict:
        """Validate a list of budget items.

        Checks:
        - Total amount is within max_amount limit (if provided)
        - No negative amounts
        - All categories are valid

        Args:
            items: List of budget item dictionaries with 'category' and 'amount'.
            max_amount: Maximum allowed total (optional).

        Returns:
            Validation result with valid flag, total, and list of issues.
        """
        def _get_field(obj, field, default=""):
            if hasattr(obj, field):
                return getattr(obj, field)
            if isinstance(obj, dict):
                return obj.get(field, default)
            return default

        issues = []
        total = 0.0
        valid_categories = set(INNOVATION_CATEGORIES) | set(ENTREPRENEURSHIP_CATEGORIES)

        for i, item in enumerate(items):
            category = _get_field(item, "category", "")
            amount = _get_field(item, "amount", 0)

            if category not in valid_categories:
                issues.append(f"第{i + 1}项：类别'{category}'不在有效类别列表中")

            if not isinstance(amount, (int, float)):
                issues.append(f"第{i + 1}项：金额必须为数字")
                continue

            if amount < 0:
                issues.append(f"第{i + 1}项：金额不能为负数")

            total += float(amount)

        total = round(total, 2)

        if max_amount is not None and total > max_amount:
            issues.append(
                f"总预算{total:,.2f}元超出限额{max_amount:,.2f}元"
            )

        return {
            "valid": len(issues) == 0,
            "total": total,
            "issues": issues,
        }

    def format_budget_table(self, items: list) -> str:
        """Format budget items into a readable table string.

        Args:
            items: List of budget item dictionaries or BudgetItem objects.

        Returns:
            Formatted table string.
        """
        def _get_field(obj, field, default=""):
            if hasattr(obj, field):
                return getattr(obj, field)
            if isinstance(obj, dict):
                return obj.get(field, default)
            return default

        if not items:
            return "暂无预算数据"

        total = sum(_get_field(item, "amount", 0) for item in items)
        lines = []
        lines.append(f"{'类别':<12}{'金额（元）':>12}{'占比':>8}{'用途说明'}")
        lines.append("-" * 60)

        for item in items:
            category = _get_field(item, "category", "")
            amount = _get_field(item, "amount", 0)
            justification = _get_field(item, "justification", "")
            pct = (amount / total * 100) if total > 0 else 0
            lines.append(f"{category:<12}{amount:>12,.2f}{pct:>7.1f}%  {justification}")

        lines.append("-" * 60)
        lines.append(f"{'合计':<12}{total:>12,.2f}{'100.0%':>8}")

        return "\n".join(lines)
