"""Business plan generator for AuroraAgent."""

from typing import Dict

from aurora.competition.database import CompetitionDatabase


class BusinessPlanGenerator:
    """Generate business plans for competitions."""

    SECTIONS = [
        "executive_summary",
        "project_overview",
        "market_analysis",
        "product_service",
        "business_model",
        "marketing_strategy",
        "operation_plan",
        "team_introduction",
        "financial_analysis",
        "risk_assessment",
    ]

    SECTION_TEMPLATES = {
        "executive_summary": {
            "title": "执行摘要",
            "subsections": ["项目一句话介绍", "核心亮点", "团队优势", "融资需求"],
            "word_count": 300,
        },
        "project_overview": {
            "title": "项目概述",
            "subsections": ["项目背景", "行业痛点", "解决方案", "核心价值"],
            "word_count": 500,
        },
        "market_analysis": {
            "title": "市场分析",
            "subsections": ["目标市场", "市场规模", "用户画像", "竞争分析", "SWOT分析"],
            "word_count": 600,
        },
        "product_service": {
            "title": "产品与服务",
            "subsections": ["产品介绍", "核心技术", "创新点", "发展阶段", "知识产权"],
            "word_count": 500,
        },
        "business_model": {
            "title": "商业模式",
            "subsections": ["价值主张", "收入模型", "成本结构", "渠道通路", "客户关系"],
            "word_count": 500,
        },
        "marketing_strategy": {
            "title": "营销策略",
            "subsections": ["定价策略", "推广策略", "渠道策略", "用户获取"],
            "word_count": 400,
        },
        "operation_plan": {
            "title": "运营计划",
            "subsections": ["短期计划", "中期计划", "长期计划"],
            "word_count": 400,
        },
        "team_introduction": {
            "title": "团队介绍",
            "subsections": ["团队成员", "组织架构", "股权结构"],
            "word_count": 400,
        },
        "financial_analysis": {
            "title": "财务分析",
            "subsections": ["收入预测", "成本预算", "利润预测", "现金流", "融资计划"],
            "word_count": 500,
        },
        "risk_assessment": {
            "title": "风险评估",
            "subsections": ["技术风险", "市场风险", "运营风险", "政策风险"],
            "word_count": 300,
        },
    }

    def __init__(self):
        self._comp_db = CompetitionDatabase()

    def generate(self, project_info: Dict, competition_id: str = "internet_plus") -> Dict:
        """
        Generate a complete business plan.

        Args:
            project_info: Project details
            competition_id: Competition ID for template selection

        Returns:
            Complete business plan structure
        """
        comp = self._comp_db.get_competition(competition_id)
        template = self._get_template(competition_id)

        plan = {
            "metadata": {
                "competition": comp.name if comp else "通用",
                "track": project_info.get("track", ""),
                "generated_at": "2026-05-22",
            },
            "sections": {},
        }

        for section_id in self.SECTIONS:
            section = self.SECTION_TEMPLATES[section_id]
            plan["sections"][section_id] = {
                "title": section["title"],
                "content": self._generate_section(project_info, section_id, template),
                "word_count": section["word_count"],
            }

        return plan

    def generate_section(self, project_info: Dict, section_id: str) -> str:
        """Generate a single section."""
        if section_id not in self.SECTION_TEMPLATES:
            return ""

        self.SECTION_TEMPLATES[section_id]
        return self._generate_section(project_info, section_id, {})

    def _generate_section(self, project_info: Dict, section_id: str, template: Dict) -> str:
        """Generate section content."""
        project_info.get("technology", "")
        project_info.get("target_market", "")
        project_info.get("team_background", "")

        section_generators = {
            "executive_summary": lambda: self._gen_executive_summary(project_info),
            "project_overview": lambda: self._gen_project_overview(project_info),
            "market_analysis": lambda: self._gen_market_analysis(project_info),
            "product_service": lambda: self._gen_product_service(project_info),
            "business_model": lambda: self._gen_business_model(project_info),
            "marketing_strategy": lambda: self._gen_marketing_strategy(project_info),
            "operation_plan": lambda: self._gen_operation_plan(project_info),
            "team_introduction": lambda: self._gen_team_introduction(project_info),
            "financial_analysis": lambda: self._gen_financial_analysis(project_info),
            "risk_assessment": lambda: self._gen_risk_assessment(project_info),
        }

        generator = section_generators.get(section_id)
        if generator:
            return generator()
        return ""

    def _gen_executive_summary(self, info: Dict) -> str:
        return f"""【项目概述】
本项目致力于{info.get('technology', '')}领域的创新应用，旨在解决{info.get('problem', '')}的痛点。

【核心亮点】
1. 创新性：{info.get('technology', '')}技术创新，具备独特竞争优势
2. 市场潜力：面向{info.get('target_market', '')}市场，需求旺盛
3. 团队实力：{info.get('team_background', '')}背景，执行力强

【融资需求】
计划融资{info.get('funding', '50万')}元，主要用于产品研发、市场推广和团队建设。"""

    def _gen_project_overview(self, info: Dict) -> str:
        return f"""【项目背景】
当前{info.get('technology', '')}行业面临{info.get('problem', '')}的挑战，传统解决方案存在诸多不足。

【行业痛点】
- 痛点1：现有产品功能单一，无法满足多元化需求
- 痛点2：成本高昂，中小企业难以承受
- 痛点3：用户体验不佳，缺乏创新交互方式

【解决方案】
本项目提出基于{info.get('technology', '')}的创新解决方案，通过{info.get('solution', '')}实现突破。

【核心价值】
为{info.get('target_market', '')}提供高效、便捷、低成本的{info.get('product', '')}服务。"""

    def _gen_market_analysis(self, info: Dict) -> str:
        return f"""【目标市场】
目标客户群体为{info.get('target_market', '')}，主要包括企业用户和个人用户。

【市场规模】
根据行业报告，{info.get('technology', '')}市场规模预计达{info.get('market_size', '百亿')}级，年增长率超过{info.get('growth_rate', '30%')}。

【用户画像】
- 年龄分布：25-45岁为主
- 职业特征：企业管理者、创业者、技术从业者
- 需求特点：注重效率、关注成本、追求创新

【竞争分析】
目前市场主要竞争者包括{info.get('competitors', '头部企业')}，本项目通过差异化定位和技术创新形成竞争优势。

【SWOT分析】
- 优势：技术领先、团队专业、模式创新
- 劣势：品牌认知度较低、资金有限
- 机会：政策支持、市场增长、技术变革
- 威胁：竞争加剧、技术迭代快"""

    def _gen_product_service(self, info: Dict) -> str:
        return f"""【产品介绍】
{info.get('product', '')}是一款基于{info.get('technology', '')}的创新产品，具备{info.get('features', '多项核心功能')}。

【核心技术】
采用{info.get('technology', '')}核心技术，拥有自主知识产权，技术壁垒高。

【创新点】
1. 技术创新：{info.get('innovation_tech', '独特算法')}
2. 模式创新：{info.get('innovation_business', '全新商业模式')}
3. 体验创新：{info.get('innovation_experience', '用户体验优化')}

【发展阶段】
目前处于{info.get('stage', '创意/初创/成长')}阶段，已完成{info.get('milestones', '核心功能开发')}。

【知识产权】
已申请{info.get('patents', '多项专利')}，拥有完整知识产权保护。"""

    def _gen_business_model(self, info: Dict) -> str:
        return f"""【价值主张】
为{info.get('target_market', '')}提供{info.get('value_proposition', '高效、便捷')}的{info.get('product', '')}解决方案。

【收入模型】
- 主要收入：{info.get('revenue_main', '订阅服务')}
- 其他收入：{info.get('revenue_other', '定制开发、技术咨询')}

【成本结构】
- 研发成本：人员薪酬、技术投入
- 运营成本：服务器、营销推广
- 管理成本：办公场地、日常开支

【渠道通路】
- 线上渠道：官网、社交媒体、行业平台
- 线下渠道：展会、合作伙伴、直销团队

【客户关系】
采用{info.get('customer_relation', '会员制')}模式，提供{info.get('service_level', '7x24小时')}服务支持。"""

    def _gen_marketing_strategy(self, info: Dict) -> str:
        return f"""【定价策略】
采用{info.get('pricing_model', '分层定价')}策略，满足不同客户需求。

【推广策略】
- 内容营销：行业分析、案例分享、技术干货
- 社群运营：建立用户社区、举办线上活动
- 合作伙伴：与{info.get('partners', '行业龙头')}建立战略合作

【渠道策略】
- 线上：SEO优化、SEM投放、社交媒体运营
- 线下：行业展会、路演活动、客户拜访

【用户获取】
通过{info.get('acquisition', '产品试用、推荐奖励')}等方式获取首批种子用户。"""

    def _gen_operation_plan(self, info: Dict) -> str:
        return f"""【短期计划（0-1年）】
- 完成核心功能开发和测试
- 上线MVP版本，获取种子用户
- 建立运营体系和服务流程

【中期计划（1-3年）】
- 完善产品功能，拓展市场覆盖
- 建立销售团队，扩大营收规模
- 完成A轮融资，加速发展

【长期计划（3-5年）】
- 成为{info.get('technology', '')}领域领先企业
- 拓展国际市场，实现全球化布局
- 打造生态体系，构建竞争壁垒"""

    def _gen_team_introduction(self, info: Dict) -> str:
        return f"""【团队成员】
{info.get('team_background', '团队成员来自知名高校和企业')}，具备丰富的行业经验和专业能力。

【组织架构】
- 核心团队：{info.get('team_size', '5人')}
- 顾问团队：行业专家和投资顾问

【股权结构】
创始人占比{info.get('founder_share', '60%')}，团队期权{info.get('option_pool', '20%')}，预留{info.get('reserve', '20%')}用于融资。"""

    def _gen_financial_analysis(self, info: Dict) -> str:
        return f"""【收入预测】
- 第1年：{info.get('year1_revenue', '100万')}
- 第2年：{info.get('year2_revenue', '500万')}
- 第3年：{info.get('year3_revenue', '2000万')}

【成本预算】
- 人力成本：{info.get('labor_cost', '每年200万')}
- 运营成本：{info.get('op_cost', '每年50万')}
- 营销成本：{info.get('marketing_cost', '每年100万')}

【利润预测】
预计{info.get('break_even', '第18个月')}实现盈利，净利润率达{info.get('profit_margin', '25%')}。

【现金流】
保持健康现金流，确保业务持续运营。

【融资计划】
本轮融资{info.get('funding', '50万')}，出让{info.get('equity', '10%')}股权。"""

    def _gen_risk_assessment(self, info: Dict) -> str:
        return """【技术风险】
- 风险：技术迭代快，可能被超越
- 应对：持续研发投入，保持技术领先

【市场风险】
- 风险：市场竞争加剧，用户获取成本上升
- 应对：差异化定位，提升产品竞争力

【运营风险】
- 风险：人才流失、管理不善
- 应对：完善激励机制，优化管理流程

【政策风险】
- 风险：政策变化影响业务
- 应对：关注政策动态，合规经营"""

    def _get_template(self, competition_id: str) -> Dict:
        """Get competition-specific template."""
        templates = {
            "internet_plus": {"emphasis": ["创新性", "商业模式", "团队"]},
            "challenge_cup": {"emphasis": ["社会价值", "科技创新", "团队"]},
            "san_chuang": {"emphasis": ["创新性", "可行性", "商业价值"]},
        }
        return templates.get(competition_id, {})

    def export_to_docx(self, plan: Dict, filepath: str):
        """Export business plan to DOCX."""
        try:
            from docx import Document
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            from docx.shared import Pt

            doc = Document()

            title = doc.add_heading(plan['metadata']['competition'] + '商业计划书', 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER

            for section_id in self.SECTIONS:
                section = plan['sections'][section_id]
                doc.add_heading(section['title'], level=1)
                doc.add_paragraph(section['content'])
                doc.add_page_break()

            doc.save(filepath)
            return {"success": True, "message": f"已导出到 {filepath}"}
        except ImportError:
            return {"success": False, "message": "需要安装 python-docx 库"}

    def export_to_markdown(self, plan: Dict, filepath: str):
        """Export business plan to Markdown."""
        content = f"# {plan['metadata']['competition']}商业计划书\n\n"
        content += f"**生成时间**: {plan['metadata']['generated_at']}\n"
        content += f"**目标赛道**: {plan['metadata']['track']}\n\n"

        for section_id in self.SECTIONS:
            section = plan['sections'][section_id]
            content += f"## {section['title']}\n\n"
            content += section['content'] + "\n\n---\n\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return {"success": True, "message": f"已导出到 {filepath}"}
