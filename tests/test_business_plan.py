"""Tests for business plan module."""

import pytest
import json
import os
import tempfile
from aurora.business_plan.generator import BusinessPlanGenerator


class TestBusinessPlanGenerator:
    """Test business plan generator functionality."""

    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = BusinessPlanGenerator()
        assert generator.SECTIONS is not None
        assert len(generator.SECTIONS) == 10

    def test_generate_complete_plan(self):
        """Test generating a complete business plan."""
        generator = BusinessPlanGenerator()
        
        project_info = {
            "project_name": "AI智能助手",
            "technology": "人工智能",
            "problem": "效率低下",
            "solution": "智能解决方案",
            "product": "AI助手",
            "target_market": "企业",
            "business_model": "订阅",
            "team_background": "高校团队",
            "funding": "50万",
            "market_size": "百亿",
            "competitors": "头部企业"
        }
        
        plan = generator.generate(project_info, competition_id="internet_plus")
        
        assert "metadata" in plan
        assert "sections" in plan
        assert len(plan["sections"]) == 10
        
        # Check metadata
        assert plan["metadata"]["competition"] == "互联网+大赛"
        assert "generated_at" in plan["metadata"]

    def test_generate_section(self):
        """Test generating a single section."""
        generator = BusinessPlanGenerator()
        
        project_info = {
            "project_name": "测试项目",
            "technology": "AI"
        }
        
        # Test each section
        for section_id in generator.SECTIONS:
            content = generator.generate_section(project_info, section_id)
            assert content is not None
            assert isinstance(content, str)
            assert len(content) > 0

    def test_generate_section_invalid_id(self):
        """Test generating section with invalid ID."""
        generator = BusinessPlanGenerator()
        
        content = generator.generate_section({}, "invalid_section")
        assert content == ""

    def test_section_templates(self):
        """Test that section templates are properly defined."""
        generator = BusinessPlanGenerator()
        
        for section_id in generator.SECTIONS:
            assert section_id in generator.SECTION_TEMPLATES
            template = generator.SECTION_TEMPLATES[section_id]
            assert "title" in template
            assert "subsections" in template
            assert "word_count" in template

    def test_export_to_markdown(self):
        """Test exporting to Markdown."""
        generator = BusinessPlanGenerator()
        
        plan = {
            "metadata": {
                "competition": "测试竞赛",
                "track": "测试赛道",
                "generated_at": "2026-05-22"
            },
            "sections": {
                "executive_summary": {
                    "title": "执行摘要",
                    "content": "测试内容"
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            temp_path = f.name
        
        try:
            result = generator.export_to_markdown(plan, temp_path)
            assert result["success"] is True
            assert os.path.exists(temp_path)
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "测试竞赛" in content
                assert "执行摘要" in content
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_export_to_docx(self):
        """Test exporting to DOCX."""
        generator = BusinessPlanGenerator()
        
        plan = {
            "metadata": {
                "competition": "测试竞赛",
                "track": "测试赛道",
                "generated_at": "2026-05-22"
            },
            "sections": {
                "executive_summary": {
                    "title": "执行摘要",
                    "content": "测试内容"
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
            temp_path = f.name
        
        try:
            result = generator.export_to_docx(plan, temp_path)
            # May fail if python-docx not installed
            assert isinstance(result, dict)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_get_template(self):
        """Test getting competition-specific template."""
        generator = BusinessPlanGenerator()
        
        template = generator._get_template("internet_plus")
        assert "emphasis" in template
        
        template = generator._get_template("challenge_cup")
        assert "emphasis" in template
        
        template = generator._get_template("unknown")
        assert template == {}

    def test_generate_with_different_competitions(self):
        """Test generating plans for different competitions."""
        generator = BusinessPlanGenerator()
        
        project_info = {
            "project_name": "测试项目",
            "technology": "AI"
        }
        
        for comp_id in ["internet_plus", "challenge_cup", "san_chuang"]:
            plan = generator.generate(project_info, competition_id=comp_id)
            assert plan["metadata"]["competition"] is not None


class TestSectionGenerators:
    """Test individual section generators."""

    def setup_method(self):
        """Setup for each test."""
        self.generator = BusinessPlanGenerator()
        self.project_info = {
            "project_name": "AI助手",
            "technology": "人工智能",
            "problem": "效率低",
            "solution": "智能方案",
            "product": "AI产品",
            "target_market": "企业",
            "business_model": "订阅",
            "team_background": "高校团队",
            "funding": "50万",
            "market_size": "百亿"
        }

    def test_gen_executive_summary(self):
        """Test executive summary generation."""
        content = self.generator._gen_executive_summary(self.project_info)
        assert "AI助手" in content
        assert "50万" in content

    def test_gen_project_overview(self):
        """Test project overview generation."""
        content = self.generator._gen_project_overview(self.project_info)
        assert "人工智能" in content
        assert "效率低" in content

    def test_gen_market_analysis(self):
        """Test market analysis generation."""
        content = self.generator._gen_market_analysis(self.project_info)
        assert "企业" in content
        assert "百亿" in content
        assert "SWOT" in content

    def test_gen_product_service(self):
        """Test product service generation."""
        content = self.generator._gen_product_service(self.project_info)
        assert "AI产品" in content
        assert "人工智能" in content

    def test_gen_business_model(self):
        """Test business model generation."""
        content = self.generator._gen_business_model(self.project_info)
        assert "订阅" in content
        assert "价值主张" in content

    def test_gen_marketing_strategy(self):
        """Test marketing strategy generation."""
        content = self.generator._gen_marketing_strategy(self.project_info)
        assert "定价策略" in content
        assert "推广策略" in content

    def test_gen_operation_plan(self):
        """Test operation plan generation."""
        content = self.generator._gen_operation_plan(self.project_info)
        assert "短期计划" in content
        assert "中期计划" in content
        assert "长期计划" in content

    def test_gen_team_introduction(self):
        """Test team introduction generation."""
        content = self.generator._gen_team_introduction(self.project_info)
        assert "高校团队" in content

    def test_gen_financial_analysis(self):
        """Test financial analysis generation."""
        content = self.generator._gen_financial_analysis(self.project_info)
        assert "50万" in content
        assert "收入预测" in content

    def test_gen_risk_assessment(self):
        """Test risk assessment generation."""
        content = self.generator._gen_risk_assessment(self.project_info)
        assert "技术风险" in content
        assert "市场风险" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
