"""Business plan generator for AuroraAgent."""

import os
from datetime import datetime
from typing import Dict, Optional
import json
from aurora.config import load_config, Config

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

    def __init__(self, config: Optional[Config] = None):
        self._comp_db = CompetitionDatabase()
        self.config = config or load_config()
        self.llm_client = self._init_llm()

        try:
            from aurora.business_plan.outline_parser import SecretOutlineParser
            self.outline_parser = SecretOutlineParser()
        except Exception:
            self.outline_parser = None

    
    def _init_llm(self):
        try:
            import os
            from openai import OpenAI
            return OpenAI(
                api_key=self.config.model.api_key or os.environ.get("AURORA_API_KEY"),
                base_url=self.config.model.base_url or os.environ.get("AURORA_BASE_URL")
            )
        except Exception:
            return None

    def generate(self, project_info: Dict, competition_id: str = "internet_plus", session_id: str = None) -> Dict:
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
                "generated_at": datetime.now().strftime("%Y-%m-%d"),
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

        return self._generate_section(project_info, section_id, {})

    def _generate_section(self, project_info: Dict, section_id: str, template: Dict) -> str:
        """Generate section content using LLM and Proprietary Prompts."""
        custom_prompts = {}
        if self.outline_parser is not None:
            custom_prompts = self.outline_parser.get_section_prompts()
        constraints = custom_prompts.get(section_id, "")

        # If we have an LLM configured, use it instead of static templates
        if self.llm_client:
            model_name = self.config.model.name or os.environ.get("AURORA_MODEL", "glm-4.7-flash")

            system_msg = "你是顶级商业计划书主笔。必须严格遵守以下段落行文规范。绝不使用模板套话。"
            if constraints:
                system_msg += f"\n\n【最高写作铁律与结构要求】：\n{constraints}"

            prompt = (
                f"项目信息：\n{json.dumps(project_info, ensure_ascii=False, indent=2)}\n\n"
                f"请为你撰写【{section_id}】章节的全部正文文本。直接输出不排版。"
            )

            try:
                resp = self.llm_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=8192
                )
                msg = resp.choices[0].message
                content = msg.content or ""
                if not content.strip():
                    rc = getattr(msg, 'reasoning_content', None)
                    if rc and rc.strip():
                        content = rc
                return content
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"LLM fail: {e}")

        # Fallback to static generators if no API
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
        tech = info.get('technology', '相关技术')
        market = info.get('target_market', '目标市场')
        problem = info.get('problem', '行业痛点')
        product = info.get('product', '产品')
        return f"""【项目概述】
{product}基于{tech}，面向{market}，解决{problem}。

【核心亮点】
1. 技术创新：基于{tech}的差异化技术方案
2. 市场机会：{market}存在明确未被满足的需求
3. 商业闭环：清晰的盈利模式与增长路径

【融资需求】
计划融资{info.get('funding', '50万')}元，主要用于产品研发、市场验证和团队扩充。

注意：以上内容为模板框架，需要根据实际项目数据补充具体数字和案例。"""

    def _gen_project_overview(self, info: Dict) -> str:
        tech = info.get('technology', '相关技术')
        problem = info.get('problem', '行业痛点')
        solution = info.get('solution', '解决方案')
        market = info.get('target_market', '目标市场')
        return f"""【项目背景】
{market}领域长期面临{problem}。现有方案存在效率低、成本高、覆盖不足等问题。

【行业痛点】
[需要补充具体数据：市场规模、用户调研数据、行业报告引用]
- 痛点1：[具体痛点 + 数据支撑]
- 痛点2：[具体痛点 + 用户反馈]
- 痛点3：[具体痛点 + 竞品缺陷]

【解决方案】
基于{tech}，通过{solution}解决上述痛点。

【核心价值】
为{market}用户提供[具体可量化的价值，如"效率提升X%"、"成本降低Y%"]。

注意：需要补充真实市场数据和用户调研支撑。"""

    def _gen_market_analysis(self, info: Dict) -> str:
        tech = info.get('technology', '相关技术')
        market = info.get('target_market', '目标市场')
        return f"""【目标市场】
{market}，需要细分到具体客户群体和场景。

【市场规模】
[需要补充：TAM/SAM/SOM分析，引用权威数据源]
- TAM（总可用市场）：[数据 + 来源]
- SAM（可服务市场）：[数据 + 来源]
- SOM（可获得市场）：[数据 + 来源]

【用户画像】
[需要补充真实用户调研]
- 核心用户群：[具体特征]
- 使用场景：[具体场景描述]
- 付费意愿：[调研数据]

【竞争分析】
[需要补充竞品对比矩阵表格，列出3-5个核心竞品的参数对比]

【SWOT分析】
- 优势(S)：[基于项目实际情况，需要具体]
- 劣势(W)：[诚实评估]
- 机会(O)：[市场趋势数据支撑]
- 威胁(T)：[竞争对手动态]

注意：所有数据需引用权威来源，避免"百亿市场"等空洞表述。"""

    def _gen_product_service(self, info: Dict) -> str:
        tech = info.get('technology', '相关技术')
        product = info.get('product', '产品')
        return f"""【产品介绍】
{product}基于{tech}构建，核心功能包括[需要补充功能清单]。

【核心技术】
[需要补充：技术架构图、核心技术指标、与传统方案的定量对比]

【创新点】
1. [具体技术创新，附技术指标对比]
2. [模式创新，附用户验证数据]
3. [体验创新，附用户测试反馈]

【发展阶段】
当前状态：[需要补充已完成的里程碑]
下一步计划：[需要补充开发路线图]

【知识产权】
[需要补充：已申请/获批的专利、软著清单]

注意：技术指标需要用数据说话，避免笼统描述。"""

    def _gen_business_model(self, info: Dict) -> str:
        product = info.get('product', '产品')
        market = info.get('target_market', '目标市场')
        return f"""【价值主张】
为{market}提供[具体价值，需量化]的{product}服务。

【收入模型】
[需要补充具体的定价和收入预测]
- 主要收入来源：[定价 + 预期客户数]
- 客单价：[具体数字]
- 复购率/续费率：[预期数据]

【成本结构】
[需要补充具体数字]
- 固定成本：[人力、场地等，具体金额]
- 变动成本：[服务器、获客成本等，具体金额]
- 盈亏平衡点(BEP)：[预计第X个月]

【渠道通路】
[需要补充具体的获客渠道和转化率预估]

【客户关系】
[需要补充客户留存策略和具体运营指标]

注意：所有财务预测必须有推导逻辑，禁止"一年回本三年上市"式吹嘘。"""

    def _gen_marketing_strategy(self, info: Dict) -> str:
        market = info.get('target_market', '目标市场')
        return f"""【定价策略】
[需要补充具体定价方案和定价逻辑]

【推广策略】
- 获客渠道1：[渠道名 + 预计获客成本CAC]
- 获客渠道2：[渠道名 + 预计转化率]
- 内容营销：[具体内容形式和发布计划]

【渠道策略】
[需要补充具体的合作渠道和谈判进展]

【用户获取】
冷启动方案：[首批种子用户获取的具体执行方案]
增长模型：[需要提供用户增长公式和关键假设]

注意：营销策略需要有预算分配和ROI预估。"""

    def _gen_operation_plan(self, info: Dict) -> str:
        return """【短期计划（0-6个月）】
[需要补充具体的里程碑节点和时间表]
- 里程碑1：[具体目标 + 完成时间]
- 里程碑2：[具体目标 + 完成时间]

【中期计划（6-18个月）】
[需要补充具体的业务目标和资源需求]
- 目标1：[可量化的目标]
- 目标2：[可量化的目标]

【长期计划（18-36个月）】
[需要补充具体的扩张计划和战略目标]

注意：每个里程碑需要有明确的负责人、时间节点和验收标准。"""

    def _gen_team_introduction(self, info: Dict) -> str:
        return f"""【团队成员】
[需要补充每位核心成员的具体信息]
- 姓名 | 职位 | 背景 | 核心贡献
[格式化的团队表格]

【组织架构】
[需要补充组织架构图和汇报关系]

【股权结构】
[需要补充合理的股权分配方案]
注意：互联网+等赛事要求体现"师生共创"，需说明导师的技术贡献和利益绑定。

注意：团队介绍需要突出成员与项目的匹配度，而非空泛的背景描述。"""

    def _gen_financial_analysis(self, info: Dict) -> str:
        sandbox_result = self._run_financial_sandbox(info)
        if sandbox_result:
            return self._format_sandbox_result(info, sandbox_result)
        return self._gen_financial_fallback(info)

    def _run_financial_sandbox(self, info: Dict):
        try:
            from aurora.financial.engine import FinancialSandbox
            unit_price = info.get("unit_price")
            initial_vol = info.get("initial_monthly_vol")
            if unit_price is not None and initial_vol is not None:
                return FinancialSandbox.calculate_projection(
                    unit_price=float(unit_price),
                    initial_monthly_vol=int(initial_vol),
                    monthly_growth_rate=float(info.get("monthly_growth_rate", 0.05)),
                    fixed_monthly_cost=float(info.get("fixed_monthly_cost", 50000)),
                    unit_variable_cost=float(info.get("unit_variable_cost", 0)),
                )
        except Exception:
            pass
        return None

    def _format_sandbox_result(self, info: Dict, result: dict) -> str:
        proj = result["projections"]
        lines = ["【财务沙盘预测（基于确定性模型）】", ""]
        for p in proj:
            lines.append(f"  第{p['year']}年：收入 {p['revenue']:,.0f}元 / 成本 {p['total_cost']:,.0f}元 / 净利润 {p['net_profit']:,.0f}元 / 毛利率 {p['gross_margin']*100:.1f}%")
        lines.append(f"\n  盈亏平衡点：第{result['break_even_month']}个月")
        lines.append(f"  3年总营收：{result['total_3yr_revenue']:,.0f}元")
        lines.append(f"  3年总利润：{result['total_3yr_profit']:,.0f}元")
        lines.append("")
        lines.append(f"【融资计划】")
        lines.append(f"本轮融资{info.get('funding', '50万')}，出让{info.get('equity', '10%')}股权。")
        return "\n".join(lines)

    def _gen_financial_fallback(self, info: Dict) -> str:
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
        """Export business plan to DOCX using DocxBuilder."""
        try:
            from aurora.business_plan.docx_builder import DocxBuilder
            builder = DocxBuilder()
            comp_name = plan.get("metadata", {}).get("competition", "")
            return builder.build(plan, filepath, competition_name=comp_name)
        except ImportError:
            return {"success": False, "message": "python-docx is required"}
        except Exception as e:
            return {"success": False, "message": f"Export failed: {str(e)}"}

    def export_to_markdown(self, plan: Dict, filepath: str):
        """Export business plan to Markdown."""
        content = f"# {plan['metadata']['competition']}商业计划书\n\n"
        content += f"**生成时间**: {plan['metadata']['generated_at']}\n"
        content += f"**目标赛道**: {plan['metadata']['track']}\n\n"

        for section_id in self.SECTIONS:
            section = plan['sections'].get(section_id)
            if not section:
                continue
            content += f"## {section['title']}\n\n"
            content += section['content'] + "\n\n---\n\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return {"success": True, "message": f"已导出到 {filepath}"}
