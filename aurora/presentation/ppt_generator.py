"""PPT generator for AuroraAgent."""

from typing import Dict, List, Optional


def export_to_pptx(ppt_content: Dict, filepath: str, theme: str = "business_blue") -> Dict:
    """Export PPT JSON to .pptx file."""
    from aurora.presentation.pptx_exporter import PPTXExporter
    exporter = PPTXExporter(theme=theme)
    return exporter.export(ppt_content, filepath)


class PPTGenerator:
    """Generate presentation content for competitions."""

    SLIDE_STRUCTURE = [
        {"id": "cover", "title": "封面", "content_type": "title"},
        {"id": "problem", "title": "痛点分析", "content_type": "bullet"},
        {"id": "solution", "title": "解决方案", "content_type": "bullet"},
        {"id": "product", "title": "产品介绍", "content_type": "bullet"},
        {"id": "technology", "title": "核心技术", "content_type": "bullet"},
        {"id": "market", "title": "市场分析", "content_type": "bullet"},
        {"id": "business", "title": "商业模式", "content_type": "bullet"},
        {"id": "data", "title": "运营数据", "content_type": "data"},
        {"id": "team", "title": "团队介绍", "content_type": "bullet"},
        {"id": "plan", "title": "发展规划", "content_type": "timeline"},
        {"id": "funding", "title": "融资需求", "content_type": "bullet"},
        {"id": "closing", "title": "结束页", "content_type": "title"},
    ]

    def __init__(self):
        pass

    def generate(self, project_info: Dict, competition_id: str = "internet_plus") -> Dict:
        """
        Generate PPT content.

        Args:
            project_info: Project details
            competition_id: Target competition

        Returns:
            PPT structure with slides
        """
        slides = []

        for slide_def in self.SLIDE_STRUCTURE:
            slide = {
                "id": slide_def["id"],
                "title": slide_def["title"],
                "content": self._generate_slide_content(slide_def["id"], project_info),
                "content_type": slide_def["content_type"],
            }
            slides.append(slide)

        return {
            "competition": competition_id,
            "slide_count": len(slides),
            "slides": slides,
        }

    def _generate_slide_content(self, slide_id: str, info: Dict) -> List[Dict]:
        """Generate content for a specific slide."""
        generators = {
            "cover": lambda: self._gen_cover(info),
            "problem": lambda: self._gen_problem(info),
            "solution": lambda: self._gen_solution(info),
            "product": lambda: self._gen_product(info),
            "technology": lambda: self._gen_technology(info),
            "market": lambda: self._gen_market(info),
            "business": lambda: self._gen_business(info),
            "data": lambda: self._gen_data(info),
            "team": lambda: self._gen_team(info),
            "plan": lambda: self._gen_plan(info),
            "funding": lambda: self._gen_funding(info),
            "closing": lambda: self._gen_closing(info),
        }

        generator = generators.get(slide_id)
        if generator:
            return generator()
        return []

    def _gen_cover(self, info: Dict) -> List[Dict]:
        return [
            {"type": "title", "text": info.get("project_name", "创新创业项目")},
            {"type": "subtitle", "text": f"团队：{info.get('team_name', '创新团队')}"},
            {"type": "tagline", "text": info.get("tagline", "用创新改变世界")},
        ]

    def _gen_problem(self, info: Dict) -> List[Dict]:
        problem = info.get("problem", "行业痛点")
        return [
            {"type": "title", "text": "行业痛点"},
            {"type": "bullet", "text": f"{problem}"},
            {"type": "bullet", "text": "传统解决方案存在不足"},
            {"type": "bullet", "text": "用户需求未被充分满足"},
        ]

    def _gen_solution(self, info: Dict) -> List[Dict]:
        solution = info.get("solution", "创新解决方案")
        return [
            {"type": "title", "text": "解决方案"},
            {"type": "bullet", "text": f"{solution}"},
            {"type": "bullet", "text": "核心价值主张"},
            {"type": "bullet", "text": "差异化竞争优势"},
        ]

    def _gen_product(self, info: Dict) -> List[Dict]:
        product = info.get("product", "核心产品")
        features = info.get("features", ["功能1", "功能2", "功能3"])
        items = [{"type": "title", "text": "产品介绍"}, {"type": "bullet", "text": product}]
        for i, feature in enumerate(features[:3], 1):
            items.append({"type": "bullet", "text": f"功能{i}：{feature}"})
        return items

    def _gen_technology(self, info: Dict) -> List[Dict]:
        tech = info.get("technology", "核心技术")
        return [
            {"type": "title", "text": "核心技术"},
            {"type": "bullet", "text": f"{tech}"},
            {"type": "bullet", "text": "技术壁垒分析"},
            {"type": "bullet", "text": "知识产权保护"},
        ]

    def _gen_market(self, info: Dict) -> List[Dict]:
        market = info.get("target_market", "目标市场")
        size = info.get("market_size", "百亿级")
        return [
            {"type": "title", "text": "市场分析"},
            {"type": "bullet", "text": f"目标市场：{market}"},
            {"type": "bullet", "text": f"市场规模：{size}"},
            {"type": "bullet", "text": "增长趋势：持续增长"},
        ]

    def _gen_business(self, info: Dict) -> List[Dict]:
        model = info.get("business_model", "商业模式")
        revenue = info.get("revenue_model", "多元收入")
        return [
            {"type": "title", "text": "商业模式"},
            {"type": "bullet", "text": f"{model}"},
            {"type": "bullet", "text": f"收入来源：{revenue}"},
            {"type": "bullet", "text": "盈利预期：良好"},
        ]

    def _gen_data(self, info: Dict) -> List[Dict]:
        return [
            {"type": "title", "text": "运营数据"},
            {"type": "data", "label": "用户增长", "value": "10万+"},
            {"type": "data", "label": "月活用户", "value": "5万+"},
            {"type": "data", "label": "增长率", "value": "30%+"},
        ]

    def _gen_team(self, info: Dict) -> List[Dict]:
        team = info.get("team_background", "优秀团队")
        members = info.get("team_members", ["成员1", "成员2", "成员3"])
        items = [{"type": "title", "text": "团队介绍"}, {"type": "bullet", "text": team}]
        for member in members[:3]:
            items.append({"type": "bullet", "text": member})
        return items

    def _gen_plan(self, info: Dict) -> List[Dict]:
        return [
            {"type": "title", "text": "发展规划"},
            {"type": "timeline", "phase": "短期", "text": "产品打磨与验证"},
            {"type": "timeline", "phase": "中期", "text": "市场拓展与增长"},
            {"type": "timeline", "phase": "长期", "text": "生态构建与领先"},
        ]

    def _gen_funding(self, info: Dict) -> List[Dict]:
        amount = info.get("funding", "50万")
        equity = info.get("equity", "10%")
        return [
            {"type": "title", "text": "融资需求"},
            {"type": "bullet", "text": f"融资金额：{amount}"},
            {"type": "bullet", "text": f"出让股权：{equity}"},
            {"type": "bullet", "text": "资金用途：研发、市场、团队"},
        ]

    def _gen_closing(self, info: Dict) -> List[Dict]:
        return [
            {"type": "title", "text": "谢谢观看"},
            {"type": "subtitle", "text": f"团队：{info.get('team_name', '创新团队')}"},
            {"type": "contact", "text": "联系方式"},
        ]

    def generate_script(self, ppt_content: Dict) -> str:
        """Generate presentation script."""
        script = ""
        for slide in ppt_content["slides"]:
            script += f"【{slide['title']}】\n"

            if slide["id"] == "cover":
                script += "尊敬的评委老师，大家好！我是来自XX大学的XX，很高兴向大家介绍我们的项目。\n\n"
            elif slide["id"] == "problem":
                script += "首先，让我们来看一下当前行业存在的痛点...\n\n"
            elif slide["id"] == "solution":
                script += "针对这些问题，我们提出了创新的解决方案...\n\n"
            elif slide["id"] == "closing":
                script += "以上就是我们项目的全部内容，感谢您的聆听！欢迎提问！\n\n"
            else:
                script += f"接下来，我将为大家介绍{slide['title']}...\n\n"

        return script
