"""Tests for Dachuang (大学生创新创业训练计划) module."""

import json

import pytest

from aurora.dachuang.generator import DachuangGenerator, INNOVATION_SECTIONS
from aurora.dachuang.evaluator import DachuangEvaluator
from aurora.dachuang.budget import BudgetGenerator
from aurora.models.dachuang import BudgetItem
from aurora.dachuang.exporter import DachuangDocxExporter, DachuangPDFExporter
from aurora.models.dachuang import DachuangProjectInfo, BudgetItem
from aurora.tools.registry import ToolRegistry
from aurora.tools.dachuang_tools import _register_tools


def _make_project_info():
    return {
        "project_name": "基于深度学习的智能垃圾分类系统",
        "technology": "深度学习/计算机视觉",
        "problem": "传统垃圾分类效率低、错误率高",
        "solution": "基于卷积神经网络(CNN)的图像识别分类系统",
        "target_market": "社区/学校/企业",
        "innovation": "自主研发的轻量化CNN模型，准确率95%以上；结合边缘计算实现本地推理",
        "social_impact": "促进环保，减少 landfill 压力",
        "expected_outcomes": "发表SCI论文1篇，申请发明专利2项，开发原型系统",
        "team_background": "计算机学院本科生，指导老师为AI方向副教授",
        "advisor": "王教授",
        "department": "计算机学院",
        "leader": "张三",
    }


class TestDachuangGenerator:
    def test_generate_innovation(self):
        generator = DachuangGenerator()
        app = generator.generate(_make_project_info(), "innovation")
        assert "metadata" in app
        assert "sections" in app
        sections = app["sections"]
        assert "abstract" in sections
        assert "background" in sections
        assert "methodology" in sections
        assert "innovation_points" in sections
        assert "budget" in sections
        assert len(sections) == 9

    def test_generate_entrepreneurship(self):
        generator = DachuangGenerator()
        app = generator.generate(_make_project_info(), "entrepreneurship")
        sections = app["sections"]
        assert "abstract" in sections
        assert "market_analysis" in sections
        assert "business_model" in sections
        assert "finance" in sections
        assert "budget" in sections
        assert len(sections) == 12

    def test_generate_section_innovation(self):
        generator = DachuangGenerator()
        content = generator.generate_section(_make_project_info(), "abstract", "innovation")
        assert isinstance(content, str)
        assert len(content) > 0

    def test_generate_section_entrepreneurship(self):
        generator = DachuangGenerator()
        content = generator.generate_section(_make_project_info(), "market_analysis", "entrepreneurship")
        assert isinstance(content, str)
        assert len(content) > 0

    def test_fallback_content_framework_style(self):
        generator = DachuangGenerator()
        # Force fallback by passing empty dict
        generator.llm_client = None
        content = generator._generate_section_content(
            {"technology": "AI"}, "background", INNOVATION_SECTIONS["background"], "innovation"
        )
        assert "需要补充" in content
        assert "国内外研究现状" in content

    def test_generate_invalid_type(self):
        generator = DachuangGenerator()
        app = generator.generate(_make_project_info(), "unknown_type")
        assert app["metadata"]["project_type"] == "innovation"  # default fallback


class TestDachuangEvaluator:
    def test_evaluate_innovation(self):
        evaluator = DachuangEvaluator()
        application = {
            "sections": {
                "abstract": {"title": "摘要", "content": "测试"},
                "innovation_points": {"title": "创新点", "content": "创新"},
            }
        }
        result = evaluator.evaluate(_make_project_info(), application, "innovation")
        assert "overall_score" in result
        assert "dimensions" in result
        assert 0 <= result["overall_score"] <= 100
        assert len(result["dimensions"]) == 5

    def test_evaluate_entrepreneurship(self):
        evaluator = DachuangEvaluator()
        application = {
            "sections": {
                "business_model": {"title": "商业模式", "content": "SaaS订阅"},
                "competition": {"title": "竞争分析", "content": "差异化"},
            }
        }
        result = evaluator.evaluate(_make_project_info(), application, "entrepreneurship")
        assert "overall_score" in result
        assert len(result["dimensions"]) == 4

    def test_evaluate_dimension_coverage(self):
        evaluator = DachuangEvaluator()
        result = evaluator.evaluate(_make_project_info(), {}, "innovation")
        dim_names = [d["name"] for d in result["dimensions"]]
        assert "选题价值" in dim_names
        assert "创新性" in dim_names


class TestBudgetGenerator:
    def test_generate_innovation_budget(self):
        gen = BudgetGenerator()
        items = gen.generate_budget(_make_project_info(), 10000, "innovation")
        assert len(items) > 0
        total = sum(i.amount for i in items)
        assert abs(total - 10000) < 0.01
        categories = [i.category for i in items]
        assert "资料费" in categories
        assert "实验材料费" in categories

    def test_generate_entrepreneurship_budget(self):
        gen = BudgetGenerator()
        items = gen.generate_budget(_make_project_info(), 20000, "entrepreneurship")
        assert len(items) > 0
        categories = [i.category for i in items]
        assert "产品开发费" in categories
        assert "市场调研费" in categories

    def test_validate_budget_valid(self):
        gen = BudgetGenerator()
        items = [
            BudgetItem(category="资料费", amount=5000, justification="购买文献"),
            BudgetItem(category="调研差旅费", amount=3000, justification="调研"),
        ]
        result = gen.validate_budget(items, max_amount=10000)
        assert result["valid"] is True
        assert result["total"] == 8000
        assert len(result["issues"]) == 0

    def test_validate_budget_exceeds(self):
        gen = BudgetGenerator()
        items = [
            BudgetItem(category="资料费", amount=8000, justification="文献"),
            BudgetItem(category="调研差旅费", amount=5000, justification="调研"),
        ]
        result = gen.validate_budget(items, max_amount=10000)
        assert result["valid"] is False
        assert any("超出" in issue for issue in result["issues"])

    def test_validate_budget_negative(self):
        gen = BudgetGenerator()
        items = [BudgetItem(category="资料费", amount=-500, justification="")]
        result = gen.validate_budget(items)
        assert result["valid"] is False
        assert any("负数" in issue for issue in result["issues"])


class TestDachuangModels:
    def test_project_info(self):
        info = DachuangProjectInfo(project_name="测试", project_type="innovation")
        assert info.project_name == "测试"
        assert info.project_type == "innovation"
        d = info.to_dict()
        assert "project_name" in d

    def test_budget_item(self):
        item = BudgetItem(category="资料费", amount=1000, justification="购买书籍")
        assert item.category == "资料费"
        assert item.amount == 1000


class TestDachuangTools:
    def test_tools_registered(self):
        tools = ToolRegistry()
        _register_tools(tools)
        names = tools.list_tools()
        assert "dachuang_generate" in names
        assert "dachuang_generate_section" in names
        assert "dachuang_evaluate" in names
        assert "dachuang_generate_budget" in names
        assert "dachuang_validate_budget" in names
        assert "dachuang_export" in names

    def test_generate_tool(self):
        tools = ToolRegistry()
        _register_tools(tools)
        result = json.loads(tools.dispatch("dachuang_generate", {
            "project_name": "测试项目",
            "project_type": "innovation",
            "technology": "AI",
        }))
        assert "application" in result
        assert result["section_count"] == 9

    def test_generate_budget_tool(self):
        tools = ToolRegistry()
        _register_tools(tools)
        result = json.loads(tools.dispatch("dachuang_generate_budget", {
            "total_amount": 10000,
            "project_type": "innovation",
        }))
        assert "items" in result
        assert len(result["items"]) > 0

    def test_validate_budget_tool(self):
        tools = ToolRegistry()
        _register_tools(tools)
        result = json.loads(tools.dispatch("dachuang_validate_budget", {
            "items": [
                {"category": "资料费", "amount": 5000},
                {"category": "调研差旅费", "amount": 3000},
            ],
            "max_amount": 10000,
        }))
        assert result["valid"] is True

    def test_evaluate_tool(self):
        tools = ToolRegistry()
        _register_tools(tools)
        result = json.loads(tools.dispatch("dachuang_evaluate", {
            "project_info": _make_project_info(),
            "application": {"sections": {"abstract": {"title": "摘要", "content": "测试"}}},
            "project_type": "innovation",
        }))
        assert "evaluation" in result
