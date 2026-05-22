"""Tests for presentation module."""

import pytest
from aurora.presentation.ppt_generator import PPTGenerator


class TestPPTGenerator:
    """Test PPT generator functionality."""

    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = PPTGenerator()
        assert generator.SLIDE_STRUCTURE is not None
        assert len(generator.SLIDE_STRUCTURE) == 12

    def test_generate_ppt(self):
        """Test generating PPT content."""
        generator = PPTGenerator()
        
        project_info = {
            "project_name": "创新项目",
            "team_name": "创新团队",
            "technology": "AI",
            "problem": "痛点",
            "solution": "方案",
            "product": "产品",
            "target_market": "市场",
            "business_model": "模式",
            "revenue_model": "收入",
            "funding": "50万",
            "equity": "10%"
        }
        
        ppt = generator.generate(project_info)
        
        assert "slides" in ppt
        assert ppt["slide_count"] == 12
        assert len(ppt["slides"]) == 12

    def test_ppt_structure(self):
        """Test PPT has correct structure."""
        generator = PPTGenerator()
        
        project_info = {"project_name": "测试"}
        ppt = generator.generate(project_info)
        
        expected_slides = [
            "封面", "痛点分析", "解决方案", "产品介绍",
            "核心技术", "市场分析", "商业模式", "运营数据",
            "团队介绍", "发展规划", "融资需求", "结束页"
        ]
        
        for i, expected_title in enumerate(expected_slides):
            assert ppt["slides"][i]["title"] == expected_title

    def test_cover_slide(self):
        """Test cover slide generation."""
        generator = PPTGenerator()
        
        project_info = {
            "project_name": "AI项目",
            "team_name": "AI团队",
            "tagline": "用AI改变世界"
        }
        
        content = generator._gen_cover(project_info)
        
        assert any(item["type"] == "title" and "AI项目" in item["text"] for item in content)
        assert any(item["type"] == "subtitle" and "AI团队" in item["text"] for item in content)

    def test_problem_slide(self):
        """Test problem slide generation."""
        generator = PPTGenerator()
        
        project_info = {"problem": "效率低下"}
        content = generator._gen_problem(project_info)
        
        assert any(item["type"] == "title" and "痛点" in item["text"] for item in content)
        assert any(item["type"] == "bullet" and "效率低下" in item["text"] for item in content)

    def test_solution_slide(self):
        """Test solution slide generation."""
        generator = PPTGenerator()
        
        project_info = {"solution": "智能方案"}
        content = generator._gen_solution(project_info)
        
        assert any(item["type"] == "title" and "解决方案" in item["text"] for item in content)
        assert any(item["type"] == "bullet" and "智能方案" in item["text"] for item in content)

    def test_product_slide(self):
        """Test product slide generation."""
        generator = PPTGenerator()
        
        project_info = {
            "product": "AI助手",
            "features": ["功能1", "功能2", "功能3"]
        }
        
        content = generator._gen_product(project_info)
        
        assert any(item["type"] == "title" and "产品" in item["text"] for item in content)
        assert any(item["type"] == "bullet" and "AI助手" in item["text"] for item in content)

    def test_market_slide(self):
        """Test market slide generation."""
        generator = PPTGenerator()
        
        project_info = {
            "target_market": "企业市场",
            "market_size": "百亿级"
        }
        
        content = generator._gen_market(project_info)
        
        assert any(item["type"] == "title" and "市场" in item["text"] for item in content)
        assert any(item["type"] == "bullet" and "企业市场" in item["text"] for item in content)

    def test_business_slide(self):
        """Test business model slide generation."""
        generator = PPTGenerator()
        
        project_info = {
            "business_model": "订阅模式",
            "revenue_model": "多元收入"
        }
        
        content = generator._gen_business(project_info)
        
        assert any(item["type"] == "title" and "商业模式" in item["text"] for item in content)

    def test_team_slide(self):
        """Test team slide generation."""
        generator = PPTGenerator()
        
        project_info = {
            "team_background": "优秀团队",
            "team_members": ["成员A", "成员B", "成员C"]
        }
        
        content = generator._gen_team(project_info)
        
        assert any(item["type"] == "title" and "团队" in item["text"] for item in content)
        assert any(item["type"] == "bullet" and "优秀团队" in item["text"] for item in content)

    def test_funding_slide(self):
        """Test funding slide generation."""
        generator = PPTGenerator()
        
        project_info = {
            "funding": "100万",
            "equity": "15%"
        }
        
        content = generator._gen_funding(project_info)
        
        assert any(item["type"] == "title" and "融资" in item["text"] for item in content)
        assert any(item["type"] == "bullet" and "100万" in item["text"] for item in content)

    def test_closing_slide(self):
        """Test closing slide generation."""
        generator = PPTGenerator()
        
        project_info = {"team_name": "创新团队"}
        content = generator._gen_closing(project_info)
        
        assert any(item["type"] == "title" and "谢谢" in item["text"] for item in content)

    def test_generate_script(self):
        """Test generating presentation script."""
        generator = PPTGenerator()
        
        ppt_content = {
            "slides": [
                {"id": "cover", "title": "封面"},
                {"id": "problem", "title": "痛点"},
                {"id": "closing", "title": "结束页"}
            ]
        }
        
        script = generator.generate_script(ppt_content)
        
        assert "封面" in script
        assert "痛点" in script
        assert "结束页" in script
        assert "评委老师" in script

    def test_generate_script_with_content(self):
        """Test script generation with full content."""
        generator = PPTGenerator()
        
        project_info = {"project_name": "测试项目"}
        ppt = generator.generate(project_info)
        script = generator.generate_script(ppt)
        
        assert len(script) > 0
        assert "封面" in script
        assert "结束页" in script

    def test_different_competitions(self):
        """Test generating for different competitions."""
        generator = PPTGenerator()
        
        project_info = {"project_name": "测试"}
        
        for comp_id in ["internet_plus", "challenge_cup", "san_chuang"]:
            ppt = generator.generate(project_info, competition_id=comp_id)
            assert ppt["competition"] == comp_id
            assert len(ppt["slides"]) == 12


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
