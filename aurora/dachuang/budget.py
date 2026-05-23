"""大创项目经费预算表生成器.

本模块提供中国大学生创新创业训练计划项目经费预算表的生成、
校验与导出功能。支持设备费、材料费、测试费、差旅费、会议费、
出版费、劳务费等标准经费类别，可导出为 Excel 格式。

典型用法:
    generator = BudgetGenerator()
    budget = generator.generate_budget_table(budget_items)
    validation = generator.validate_budget(budget, max_amount=10000)
    generator.export_budget_excel(budget, "经费预算表.xlsx")
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter


class BudgetGenerator:
    """大创项目经费预算表生成器.

    根据教育部《国家级大学生创新创业训练计划管理办法》中关于
    经费管理的规定，提供标准的经费预算类别和校验规则。

    Attributes:
        default_categories: 默认经费类别列表，符合教育部标准。
        max_budget_default: 默认经费上限（元）。
    """

    # 教育部标准经费类别
    DEFAULT_CATEGORIES = [
        "设备费",
        "材料费",
        "测试化验加工费",
        "差旅费",
        "会议费",
        "出版/文献/信息传播费",
        "劳务费",
        "专家咨询费",
        "其他",
    ]

    # 各类别默认预算上限比例（相对于总额）
    CATEGORY_LIMITS: dict[str, float] = {
        "设备费": 0.40,
        "材料费": 0.30,
        "测试化验加工费": 0.20,
        "差旅费": 0.30,
        "会议费": 0.15,
        "出版/文献/信息传播费": 0.20,
        "劳务费": 0.25,
        "专家咨询费": 0.15,
        "其他": 0.10,
    }

    def __init__(self, max_budget_default: float = 10000.0) -> None:
        """初始化经费预算生成器.

        Args:
            max_budget_default: 默认经费上限金额（元），默认为 10000。
        """
        self.max_budget_default = max_budget_default

    def generate_budget_table(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        """生成结构化的经费预算表.

        将原始预算明细列表整理为标准格式的预算表字典，包含明细、
        分类汇总、总金额等信息。

        Args:
            items: 预算明细列表，每项为字典，包含以下字段:
                - category (str): 费用类别，必须是 DEFAULT_CATEGORIES 中的值
                - item_name (str): 具体项目名称
                - amount (float): 金额（元）
                - description (str, optional): 用途说明
                - quantity (int, optional): 数量，默认为 1
                - unit_price (float, optional): 单价（元），若提供则 amount 应等于 quantity * unit_price

        Returns:
            包含完整预算表信息的字典，结构如下:
                - meta: 元数据（生成时间、版本等）
                - items: 处理后的预算明细列表
                - category_summary: 按类别汇总的金额字典
                - total_amount: 总金额（元）
                - item_count: 预算条目数量

        Raises:
            ValueError: 类别不合法、金额为负数或单价与数量不匹配。
            TypeError: 字段类型不匹配。
        """
        if not isinstance(items, list):
            raise TypeError("items 必须是列表类型")

        processed_items: list[dict[str, Any]] = []
        category_summary: dict[str, float] = {}
        total_amount = 0.0

        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                raise TypeError(f"预算项第 {idx + 1} 项必须是字典类型")

            category = item.get("category", "")
            if category and category not in self.DEFAULT_CATEGORIES:
                raise ValueError(
                    f"第 {idx + 1} 项类别 '{category}' 不合法，"
                    f"必须是以下之一: {', '.join(self.DEFAULT_CATEGORIES)}"
                )

            amount = float(item.get("amount", 0))
            if amount < 0:
                raise ValueError(f"第 {idx + 1} 项金额不能为负数")

            quantity = int(item.get("quantity", 1))
            unit_price = float(item.get("unit_price", amount))

            # 校验单价与数量
            if "quantity" in item and "unit_price" in item:
                expected = round(quantity * unit_price, 2)
                if abs(expected - amount) > 0.01:
                    raise ValueError(
                        f"第 {idx + 1} 项金额 ({amount}) 与 数量×单价 ({expected}) 不匹配"
                    )

            processed_item = {
                "category": category or "其他",
                "item_name": item.get("item_name", ""),
                "amount": round(amount, 2),
                "description": item.get("description", ""),
                "quantity": quantity,
                "unit_price": round(unit_price, 2),
            }
            processed_items.append(processed_item)

            category_summary[processed_item["category"]] = (
                category_summary.get(processed_item["category"], 0.0) + amount
            )
            total_amount += amount

        # 确保所有类别都在汇总中（即使金额为0）
        for cat in self.DEFAULT_CATEGORIES:
            if cat not in category_summary:
                category_summary[cat] = 0.0

        return {
            "meta": {
                "generator": "BudgetGenerator",
                "version": "1.0.0",
                "generated_at": datetime.now().isoformat(),
                "document_type": "大创项目经费预算表",
            },
            "items": processed_items,
            "category_summary": {k: round(v, 2) for k, v in category_summary.items()},
            "total_amount": round(total_amount, 2),
            "item_count": len(processed_items),
        }

    def validate_budget(self, budget: dict[str, Any], max_amount: float = 10000.0) -> dict[str, Any]:
        """校验经费预算的合法性与合理性.

        检查预算是否超过总额上限、各类别是否超限、必填项是否完整等。

        Args:
            budget: generate_budget_table() 生成的预算字典。
            max_amount: 经费上限金额（元），默认为 10000。

        Returns:
            校验结果字典，结构如下:
                - is_valid (bool): 是否通过所有校验
                - total_amount (float): 预算总金额
                - max_amount (float): 设定的上限金额
                - total_check (dict): 总额校验结果
                - category_checks (list[dict]): 各类别校验结果
                - warnings (list[str]): 警告信息列表
                - errors (list[str]): 错误信息列表

        Raises:
            ValueError: budget 格式不正确或缺少必要字段。
            TypeError: 字段类型不匹配。
        """
        if not isinstance(budget, dict):
            raise TypeError("budget 必须是字典类型")

        if "total_amount" not in budget:
            raise ValueError("budget 字典缺少 total_amount 字段")

        total = float(budget["total_amount"])
        errors: list[str] = []
        warnings: list[str] = []
        category_checks: list[dict[str, Any]] = []

        # 总额校验
        total_check = {
            "check": "总额上限",
            "limit": max_amount,
            "actual": total,
            "passed": total <= max_amount,
        }
        if not total_check["passed"]:
            errors.append(f"预算总额 {total} 元超过上限 {max_amount} 元")

        if total <= 0:
            errors.append("预算总额必须大于0")

        # 各类别校验
        category_summary = budget.get("category_summary", {})
        for category, limit_ratio in self.CATEGORY_LIMITS.items():
            category_amount = float(category_summary.get(category, 0))
            limit = round(max_amount * limit_ratio, 2)
            passed = category_amount <= limit

            check_result = {
                "category": category,
                "limit": limit,
                "actual": category_amount,
                "limit_ratio": limit_ratio,
                "passed": passed,
            }
            category_checks.append(check_result)

            if not passed:
                errors.append(
                    f"{category} 预算 {category_amount} 元超过类别上限 {limit} 元"
                )

        # 检查是否有未分类项目
        items = budget.get("items", [])
        for idx, item in enumerate(items):
            if not item.get("item_name"):
                warnings.append(f"第 {idx + 1} 项缺少项目名称")
            if not item.get("description"):
                warnings.append(f"第 {idx + 1} 项缺少用途说明")

        is_valid = len(errors) == 0

        return {
            "is_valid": is_valid,
            "total_amount": total,
            "max_amount": max_amount,
            "total_check": total_check,
            "category_checks": category_checks,
            "warnings": warnings,
            "errors": errors,
        }

    def export_budget_excel(self, budget: dict[str, Any], filepath: str) -> None:
        """将经费预算表导出为 Excel 文件.

        使用 openpyxl 生成格式化的 Excel 文件，包含预算明细表、
        分类汇总表和校验结果表三个工作表。

        Args:
            budget: generate_budget_table() 生成的预算字典。
            filepath: 输出文件路径，必须以 .xlsx 结尾。

        Raises:
            ValueError: filepath 不以 .xlsx 结尾或 budget 格式不正确。
            OSError: 文件写入失败。
        """
        if not filepath.lower().endswith(".xlsx"):
            raise ValueError("输出文件路径必须以 .xlsx 结尾")

        if not isinstance(budget, dict) or "items" not in budget:
            raise ValueError("budget 格式不正确，缺少 items 字段")

        wb = Workbook()

        # 样式定义
        header_font = Font(name="微软雅黑", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        title_font = Font(name="微软雅黑", size=14, bold=True)
        title_alignment = Alignment(horizontal="center", vertical="center")

        body_font = Font(name="微软雅黑", size=10)
        body_alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        number_alignment = Alignment(horizontal="right", vertical="center")

        thin_border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin"),
        )

        # ========== 工作表1: 预算明细 ==========
        ws1 = wb.active
        ws1.title = "预算明细"

        # 标题
        ws1.merge_cells("A1:F1")
        title_cell = ws1["A1"]
        title_cell.value = "大学生创新创业训练计划项目经费预算表"
        title_cell.font = title_font
        title_cell.alignment = title_alignment
        ws1.row_dimensions[1].height = 30

        # 元信息
        ws1["A2"] = "生成时间"
        ws1["B2"] = budget["meta"]["generated_at"]
        ws1["A3"] = "预算条目数"
        ws1["B3"] = budget["item_count"]
        ws1["A4"] = "预算总金额"
        ws1["B4"] = budget["total_amount"]

        # 表头
        headers = ["序号", "费用类别", "具体项目", "数量", "单价（元）", "金额（元）", "用途说明"]
        for col_idx, header in enumerate(headers, 1):
            cell = ws1.cell(row=6, column=col_idx)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border

        # 数据行
        for row_idx, item in enumerate(budget["items"], start=7):
            ws1.cell(row=row_idx, column=1, value=row_idx - 6)
            ws1.cell(row=row_idx, column=2, value=item["category"])
            ws1.cell(row=row_idx, column=3, value=item["item_name"])
            ws1.cell(row=row_idx, column=4, value=item["quantity"])
            ws1.cell(row=row_idx, column=5, value=item["unit_price"])
            ws1.cell(row=row_idx, column=6, value=item["amount"])
            ws1.cell(row=row_idx, column=7, value=item["description"])

            for col_idx in range(1, 8):
                cell = ws1.cell(row=row_idx, column=col_idx)
                cell.font = body_font
                cell.border = thin_border
                if col_idx in (4, 5, 6):
                    cell.alignment = number_alignment
                else:
                    cell.alignment = body_alignment

        # 合计行
        total_row = 7 + len(budget["items"])
        ws1.merge_cells(start_row=total_row, start_column=1, end_row=total_row, end_column=5)
        ws1.cell(row=total_row, column=1, value="合计")
        ws1.cell(row=total_row, column=1).font = Font(name="微软雅黑", size=10, bold=True)
        ws1.cell(row=total_row, column=1).alignment = Alignment(horizontal="center", vertical="center")
        ws1.cell(row=total_row, column=6, value=budget["total_amount"])
        ws1.cell(row=total_row, column=6).font = Font(name="微软雅黑", size=10, bold=True)
        ws1.cell(row=total_row, column=6).alignment = number_alignment

        for col_idx in range(1, 8):
            ws1.cell(row=total_row, column=col_idx).border = thin_border

        # 列宽
        ws1.column_dimensions["A"].width = 8
        ws1.column_dimensions["B"].width = 18
        ws1.column_dimensions["C"].width = 25
        ws1.column_dimensions["D"].width = 10
        ws1.column_dimensions["E"].width = 12
        ws1.column_dimensions["F"].width = 12
        ws1.column_dimensions["G"].width = 35

        # ========== 工作表2: 分类汇总 ==========
        ws2 = wb.create_sheet(title="分类汇总")

        ws2.merge_cells("A1:D1")
        ws2["A1"] = "经费预算分类汇总"
        ws2["A1"].font = title_font
        ws2["A1"].alignment = title_alignment
        ws2.row_dimensions[1].height = 30

        summary_headers = ["费用类别", "金额（元）", "占比（%）", "备注"]
        for col_idx, header in enumerate(summary_headers, 1):
            cell = ws2.cell(row=3, column=col_idx)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border

        total = budget["total_amount"]
        row_idx = 4
        for category, amount in budget["category_summary"].items():
            if amount > 0:
                ws2.cell(row=row_idx, column=1, value=category)
                ws2.cell(row=row_idx, column=2, value=amount)
                ws2.cell(row=row_idx, column=3, value=round(amount / total * 100, 2) if total > 0 else 0)
                limit = round(self.max_budget_default * self.CATEGORY_LIMITS.get(category, 0), 2)
                ws2.cell(row=row_idx, column=4, value=f"上限: {limit} 元")

                for col_idx in range(1, 5):
                    cell = ws2.cell(row=row_idx, column=col_idx)
                    cell.font = body_font
                    cell.border = thin_border
                    if col_idx == 3:
                        cell.alignment = number_alignment
                    else:
                        cell.alignment = body_alignment
                row_idx += 1

        # 合计
        ws2.cell(row=row_idx, column=1, value="合计")
        ws2.cell(row=row_idx, column=1).font = Font(name="微软雅黑", size=10, bold=True)
        ws2.cell(row=row_idx, column=2, value=total)
        ws2.cell(row=row_idx, column=2).font = Font(name="微软雅黑", size=10, bold=True)
        ws2.cell(row=row_idx, column=2).alignment = number_alignment
        ws2.cell(row=row_idx, column=3, value=100.0)
        ws2.cell(row=row_idx, column=3).font = Font(name="微软雅黑", size=10, bold=True)
        ws2.cell(row=row_idx, column=3).alignment = number_alignment

        for col_idx in range(1, 5):
            ws2.cell(row=row_idx, column=col_idx).border = thin_border

        ws2.column_dimensions["A"].width = 25
        ws2.column_dimensions["B"].width = 15
        ws2.column_dimensions["C"].width = 12
        ws2.column_dimensions["D"].width = 20

        # ========== 工作表3: 校验结果 ==========
        ws3 = wb.create_sheet(title="校验结果")

        ws3.merge_cells("A1:C1")
        ws3["A1"] = "经费预算校验结果"
        ws3["A1"].font = title_font
        ws3["A1"].alignment = title_alignment
        ws3.row_dimensions[1].height = 30

        validation = self.validate_budget(budget, self.max_budget_default)

        ws3["A3"] = "校验项目"
        ws3["B3"] = "结果"
        ws3["C3"] = "说明"
        for col_idx in range(1, 4):
            cell = ws3.cell(row=3, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border

        # 总额
        ws3["A4"] = "总额校验"
        ws3["B4"] = "通过" if validation["total_check"]["passed"] else "未通过"
        ws3["C4"] = f"预算 {validation['total_amount']} 元 / 上限 {validation['max_amount']} 元"

        # 各类别
        row_idx = 5
        for check in validation["category_checks"]:
            if check["actual"] > 0:
                ws3.cell(row=row_idx, column=1, value=f"{check['category']} 校验")
                ws3.cell(row=row_idx, column=2, value="通过" if check["passed"] else "未通过")
                ws3.cell(row=row_idx, column=3, value=f"{check['actual']} 元 / 上限 {check['limit']} 元")
                row_idx += 1

        for r in range(4, row_idx):
            for col_idx in range(1, 4):
                cell = ws3.cell(row=r, column=col_idx)
                cell.font = body_font
                cell.border = thin_border
                cell.alignment = body_alignment

        # 错误与警告
        if validation["errors"]:
            row_idx += 1
            ws3.cell(row=row_idx, column=1, value="错误信息")
            ws3.cell(row=row_idx, column=1).font = Font(name="微软雅黑", size=10, bold=True, color="FF0000")
            for error in validation["errors"]:
                row_idx += 1
                ws3.merge_cells(start_row=row_idx, start_column=1, end_row=row_idx, end_column=3)
                ws3.cell(row=row_idx, column=1, value=error)
                ws3.cell(row=row_idx, column=1).font = Font(name="微软雅黑", size=10, color="FF0000")

        if validation["warnings"]:
            row_idx += 1
            ws3.cell(row=row_idx, column=1, value="警告信息")
            ws3.cell(row=row_idx, column=1).font = Font(name="微软雅黑", size=10, bold=True, color="FFA500")
            for warning in validation["warnings"]:
                row_idx += 1
                ws3.merge_cells(start_row=row_idx, start_column=1, end_row=row_idx, end_column=3)
                ws3.cell(row=row_idx, column=1, value=warning)
                ws3.cell(row=row_idx, column=1).font = Font(name="微软雅黑", size=10, color="FFA500")

        ws3.column_dimensions["A"].width = 25
        ws3.column_dimensions["B"].width = 12
        ws3.column_dimensions["C"].width = 40

        # 保存
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        wb.save(filepath)

    def export_to_json(self, budget: dict[str, Any], filepath: str) -> None:
        """将经费预算表导出为 JSON 文件.

        Args:
            budget: generate_budget_table() 生成的预算字典。
            filepath: 输出文件路径，必须以 .json 结尾。

        Raises:
            ValueError: filepath 不以 .json 结尾。
            OSError: 文件写入失败。
        """
        if not filepath.lower().endswith(".json"):
            raise ValueError("输出文件路径必须以 .json 结尾")

        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(budget, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# 示例用法
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample_items = [
        {
            "category": "设备费",
            "item_name": "GPU服务器租赁（12个月）",
            "amount": 3000.0,
            "description": "模型训练所需算力资源，租用云服务器",
            "quantity": 12,
            "unit_price": 250.0,
        },
        {
            "category": "材料费",
            "item_name": "古籍扫描图像数据集",
            "amount": 1500.0,
            "description": "从国家图书馆采购的5000页高清古籍扫描图像",
            "quantity": 1,
            "unit_price": 1500.0,
        },
        {
            "category": "测试化验加工费",
            "item_name": "模型第三方评测服务",
            "amount": 800.0,
            "description": "委托专业机构进行模型性能评测",
            "quantity": 1,
            "unit_price": 800.0,
        },
        {
            "category": "差旅费",
            "item_name": "古籍馆实地调研",
            "amount": 1200.0,
            "description": "赴国家图书馆、故宫博物院进行数据采集与调研",
            "quantity": 3,
            "unit_price": 400.0,
        },
        {
            "category": "出版/文献/信息传播费",
            "item_name": "核心期刊论文版面费",
            "amount": 2000.0,
            "description": "《计算机学报》论文发表版面费",
            "quantity": 1,
            "unit_price": 2000.0,
        },
        {
            "category": "劳务费",
            "item_name": "数据标注外包服务",
            "amount": 1500.0,
            "description": "外包10万字符的古籍文字标注工作",
            "quantity": 1,
            "unit_price": 1500.0,
        },
    ]

    generator = BudgetGenerator()

    # 生成预算表
    budget = generator.generate_budget_table(sample_items)
    print(f"预算表生成成功，共 {budget['item_count']} 项，总金额: {budget['total_amount']} 元")

    # 校验预算
    validation = generator.validate_budget(budget, max_amount=10000)
    print(f"预算校验结果: {'通过' if validation['is_valid'] else '未通过'}")
    if validation["errors"]:
        print("错误:")
        for error in validation["errors"]:
            print(f"  - {error}")
    if validation["warnings"]:
        print("警告:")
        for warning in validation["warnings"]:
            print(f"  - {warning}")

    # 导出 Excel（需要安装 openpyxl）
    # generator.export_budget_excel(budget, "经费预算表.xlsx")
    # generator.export_to_json(budget, "经费预算表.json")
