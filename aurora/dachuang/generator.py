"""Dachuang (Undergraduate Innovation Training Program) application generator."""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Optional

from aurora.config import load_config, Config

logger = logging.getLogger(__name__)

LLM_SYSTEM_PROMPT = (
    "你是大学生创新创业训练计划申报书的专业学术写作顾问，"
    "具有国家级科研项目申报书的撰写经验。"
    "\n\n## 写作风格要求"
    "\n1. **学术语体**：全文使用正式、严谨的学术语言，杜绝口语化、网络化表达。"
    "禁止使用\"很\"\"非常\"\"特别\"等模糊修饰词。"
    "\n2. **段落化表达**：正文必须为连贯的自然段落，每段围绕一个中心论点展开。"
    "段首为主题句，段内为论证句，段末为小结句。"
    "严禁使用条目罗列（1. 2. 3.）替代段落论述。"
    "\n3. **逻辑严密**：段落之间须有过渡句衔接，体现\"提出问题—分析问题—解决问题\""
    "的学术论证链条。"
    "\n4. **精准有力**：所有论述需具体到技术路径、实验参数、数据来源或理论框架，"
    "禁止空泛套话。"
    "\n5. **专业术语**：正确使用学科领域内的标准术语和概念，"
    "首次出现的重要术语需加以界定。"
    "\n6. **数据支撑**：涉及市场规模、技术指标、实验结果等，"
    "须使用\"据XX统计\"\"实验数据显示\"等引用格式，"
    "即使为框架文本也应保留数据占位格式。"
    "\n7. **对比论证**：阐述创新性时，须与现有研究或竞品进行具体对比，"
    "说明\"现有方案不足—本方案改进—改进后的优势\"。"
    "\n\n## 格式规范"
    "\n- 不使用Markdown标题（# ## ###）"
    "\n- 不使用【】标记小节"
    "\n- 不使用项目符号列表（- *）替代段落"
    "\n- 纯段落文本，可适当使用（1）（2）（3）等编号进行分述，"
    "但每个编号后须为完整句子构成的段落，而非短语"
    "\n- 字数严格控制在要求范围内"
)

INNOVATION_SECTIONS = {
    "abstract": {
        "title": "项目摘要",
        "word_count": 300,
        "subsections": ["研究背景与问题", "研究目标与方法", "预期成果与意义"],
    },
    "background": {
        "title": "立项依据",
        "word_count": 800,
        "subsections": ["研究背景", "研究意义", "国内外研究现状"],
    },
    "objectives": {
        "title": "研究目标与内容",
        "word_count": 600,
        "subsections": ["研究目标", "研究内容", "拟解决的关键问题"],
    },
    "methodology": {
        "title": "研究方案与技术路线",
        "word_count": 800,
        "subsections": ["研究方法", "技术路线", "实验方案", "数据分析方法"],
    },
    "innovation_points": {
        "title": "项目特色与创新点",
        "word_count": 400,
        "subsections": ["理论创新", "方法创新", "应用创新"],
    },
    "schedule": {
        "title": "研究进度安排",
        "word_count": 300,
        "subsections": ["阶段一", "阶段二", "阶段三", "阶段四"],
    },
    "expected_outcomes": {
        "title": "预期成果",
        "word_count": 300,
        "subsections": ["成果形式", "量化指标"],
    },
    "budget": {
        "title": "经费预算",
        "word_count": 200,
        "subsections": ["预算明细"],
    },
    "research_conditions": {
        "title": "研究基础与条件",
        "word_count": 300,
        "subsections": ["已有研究基础", "实验条件", "团队优势"],
    },
}

ENTREPRENEURSHIP_SECTIONS = {
    "abstract": {
        "title": "项目摘要",
        "word_count": 300,
        "subsections": ["项目简介", "市场机会", "核心优势"],
    },
    "overview": {
        "title": "项目概述",
        "word_count": 500,
        "subsections": ["项目背景", "行业痛点", "解决方案"],
    },
    "market_analysis": {
        "title": "市场分析与定位",
        "word_count": 600,
        "subsections": ["目标市场", "市场规模", "用户画像", "市场需求"],
    },
    "product_service": {
        "title": "产品/服务设计",
        "word_count": 500,
        "subsections": ["产品介绍", "核心功能", "技术方案"],
    },
    "business_model": {
        "title": "商业模式",
        "word_count": 500,
        "subsections": ["价值主张", "收入模型", "成本结构"],
    },
    "competition": {
        "title": "竞争分析",
        "word_count": 400,
        "subsections": ["竞品对比", "SWOT分析", "核心竞争力"],
    },
    "marketing": {
        "title": "营销策略",
        "word_count": 400,
        "subsections": ["推广策略", "渠道策略", "用户获取"],
    },
    "team": {
        "title": "团队与组织",
        "word_count": 300,
        "subsections": ["团队成员", "组织架构", "分工安排"],
    },
    "finance": {
        "title": "财务预测",
        "word_count": 400,
        "subsections": ["收入预测", "成本预算", "盈亏平衡"],
    },
    "risk": {
        "title": "风险评估",
        "word_count": 300,
        "subsections": ["市场风险", "技术风险", "应对策略"],
    },
    "implementation": {
        "title": "实施计划",
        "word_count": 300,
        "subsections": ["短期计划", "中期计划", "里程碑"],
    },
    "budget": {
        "title": "经费预算",
        "word_count": 200,
        "subsections": ["预算明细"],
    },
}


class DachuangGenerator:
    """Generate Dachuang (Undergraduate Innovation Training Program) applications."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or load_config()
        self.llm_client = self._init_llm()

    def _init_llm(self):
        try:
            from openai import OpenAI

            return OpenAI(
                api_key=self.config.model.api_key or os.environ.get("AURORA_API_KEY"),
                base_url=self.config.model.base_url or os.environ.get("AURORA_BASE_URL"),
            )
        except Exception:
            return None

    def _get_sections_template(self, project_type: str) -> dict:
        if project_type == "entrepreneurship":
            return ENTREPRENEURSHIP_SECTIONS
        return INNOVATION_SECTIONS

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, project_info: dict, project_type: str = "innovation") -> dict:
        """Generate a complete Dachuang application.

        Args:
            project_info: Project details dictionary.
            project_type: "innovation" or "entrepreneurship".

        Returns:
            Complete application structure with metadata and sections.
        """
        if project_type not in ("innovation", "entrepreneurship"):
            project_type = "innovation"
        sections_template = self._get_sections_template(project_type)

        application = {
            "metadata": {
                "project_name": project_info.get("project_name", ""),
                "project_type": project_type,
                "level": project_info.get("level", "school"),
                "leader": project_info.get("leader", ""),
                "department": project_info.get("department", ""),
                "generated_at": datetime.now().strftime("%Y-%m-%d"),
            },
            "sections": {},
        }

        for section_id, section_template in sections_template.items():
            application["sections"][section_id] = {
                "title": section_template["title"],
                "content": self._generate_section_content(
                    project_info, section_id, section_template, project_type
                ),
                "word_count": section_template["word_count"],
            }

        return application

    def generate_section(
        self, project_info: dict, section_id: str, project_type: str = "innovation"
    ) -> str:
        """Generate a single section of the application.

        Args:
            project_info: Project details dictionary.
            section_id: Section identifier key.
            project_type: "innovation" or "entrepreneurship".

        Returns:
            Generated section content as string.
        """
        if project_type not in ("innovation", "entrepreneurship"):
            project_type = "innovation"
        sections_template = self._get_sections_template(project_type)
        section_template = sections_template.get(section_id)
        if not section_template:
            return ""

        return self._generate_section_content(
            project_info, section_id, section_template, project_type
        )

    # ------------------------------------------------------------------
    # Internal generation
    # ------------------------------------------------------------------

    def _generate_section_content(
        self, project_info: dict, section_id: str, section_template: dict, project_type: str
    ) -> str:
        """Generate section content via LLM, with structured fallback."""
        if self.llm_client:
            content = self._llm_generate(project_info, section_id, section_template, project_type)
            if content:
                return content

        # Fallback to framework templates
        return self._fallback_generate(project_info, section_id, section_template, project_type)

    def _llm_generate(
        self, project_info: dict, section_id: str, section_template: dict, project_type: str
    ) -> Optional[str]:
        """Attempt to generate content via LLM."""
        try:
            model_name = self.config.model.name or os.environ.get("AURORA_MODEL", "glm-4.7-flash")
            subsections = "、".join(section_template.get("subsections", []))
            word_count = section_template.get("word_count", 400)
            title = section_template.get("title", section_id)
            type_label = "创新训练" if project_type == "innovation" else "创业训练"

            prompt = (
                f"项目信息：\n{json.dumps(project_info, ensure_ascii=False, indent=2)}\n\n"
                f"请为大创申报书撰写【{title}】章节。"
                f"项目类型为{type_label}。"
                f"\n\n## 写作要求"
                f"\n- 字数约{word_count}字"
                f"\n- 需涵盖以下维度：{subsections}"
                f"\n- 必须使用连贯的自然段落撰写，每段为一个完整的论证单元"
                f"\n- 段首为主题句，段内展开论证，段末作小结"
                f"\n- 段落之间须有过渡句衔接"
                f"\n- 禁止以条目罗列（1. 2. 3.）替代段落论述"
                f"\n- 禁止使用【】标记"
                f"\n- 禁止使用Markdown标题符号"
                f"\n- 学术语体，精准有力，具体而非空泛"
                f"\n\n直接输出正文内容，不需要章节标题。"
            )

            resp = self.llm_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": LLM_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=4096,
            )

            msg = resp.choices[0].message
            content = msg.content or ""
            if not content.strip():
                rc = getattr(msg, "reasoning_content", None)
                if rc and rc.strip():
                    content = rc
            return content if content.strip() else None

        except Exception as e:
            logger.error(f"LLM generation failed for section {section_id}: {e}")
            return None

    # ------------------------------------------------------------------
    # Fallback generators - academic paragraph templates with placeholders
    # ------------------------------------------------------------------

    def _fallback_generate(
        self, project_info: dict, section_id: str, section_template: dict, project_type: str
    ) -> str:
        """Generate fallback content using framework templates."""
        generators = {
            "innovation": {
                "abstract": self._gen_innovation_abstract,
                "background": self._gen_innovation_background,
                "objectives": self._gen_innovation_objectives,
                "methodology": self._gen_innovation_methodology,
                "innovation_points": self._gen_innovation_innovation_points,
                "schedule": self._gen_innovation_schedule,
                "expected_outcomes": self._gen_innovation_expected_outcomes,
                "budget": lambda info: self._gen_budget(info, "innovation"),
                "research_conditions": self._gen_innovation_research_conditions,
            },
            "entrepreneurship": {
                "abstract": self._gen_entrepreneurship_abstract,
                "overview": self._gen_entrepreneurship_overview,
                "market_analysis": self._gen_entrepreneurship_market_analysis,
                "product_service": self._gen_entrepreneurship_product_service,
                "business_model": self._gen_entrepreneurship_business_model,
                "competition": self._gen_entrepreneurship_competition,
                "marketing": self._gen_entrepreneurship_marketing,
                "team": self._gen_entrepreneurship_team,
                "finance": self._gen_entrepreneurship_finance,
                "risk": self._gen_entrepreneurship_risk,
                "implementation": self._gen_entrepreneurship_implementation,
                "budget": lambda info: self._gen_budget(info, "entrepreneurship"),
            },
        }

        type_generators = generators.get(project_type, generators["innovation"])
        generator = type_generators.get(section_id)
        if generator:
            return generator(project_info)

        return self._gen_generic(section_template, project_info)

    # -- Innovation fallback generators --

    def _gen_innovation_abstract(self, info: dict) -> str:
        tech = info.get("technology", "相关技术")
        problem = info.get("problem", "研究领域的关键问题")
        solution = info.get("solution", "解决方案")
        outcomes = info.get("expected_outcomes", "预期成果")
        return (
            f"在{tech}领域，{problem}已成为制约该领域发展的核心瓶颈。"
            f"现有研究虽然在基础理论层面取得了一定进展，"
            f"但在实际工程应用中存在精度不足、泛化能力弱等显著缺陷。"
            f"针对上述问题，本项目拟以{solution}为核心技术路径，"
            f"系统性地开展理论与实验研究。"
            f"研究方法上，本项目采用文献调研与实验验证相结合的策略，"
            f"首先通过系统性文献综述厘清该领域的发展脉络与研究空白，"
            f"继而设计并实施系列对比实验以验证所提方法的有效性。"
            f"预期成果方面，本项目计划{outcomes}。"
            f"[需要补充：具体可量化的性能指标，如准确率提升至XX%、误差降低至XX等。]"
            f"该研究对于推动{tech}的理论发展及工程应用均具有重要的学术价值与实践意义。"
        )

    def _gen_innovation_background(self, info: dict) -> str:
        tech = info.get("technology", "相关技术")
        problem = info.get("problem", "研究问题")
        return (
            f"近年来，{tech}领域经历了快速的技术迭代与理论深化。"
            f"随着相关基础理论的逐步成熟，{problem}日益凸显，"
            f"已成为学术界与工业界共同关注的前沿课题。"
            f"据相关统计，[需要补充：权威数据来源及具体数据，"
            f"如\"据《中国XX产业发展报告（20XX）》统计，该领域市场规模已达XX亿元，"
            f"年复合增长率达XX%\"]。"
            f"从理论层面审视，现有研究体系在[需要补充：具体理论缺陷]方面存在明显不足，"
            f"尚未形成统一的分析框架与评价标准。"
            f"从实践层面审视，现有技术方案在[需要补充：具体工程瓶颈]方面面临严峻挑战，"
            f"难以满足实际应用场景对[需要补充：性能指标]的严格要求。"
            f"因此，深入开展{problem}的研究，"
            f"不仅有助于完善{tech}的理论体系，"
            f"更能够为[需要补充：具体应用场景]提供可靠的技术支撑。"
            f"\n\n"
            f"在国内外研究现状方面，国外学者较早关注该领域的理论奠基工作。"
            f"[需要补充：3至5篇代表性外文文献综述，含作者、年份、发表期刊及核心结论，"
            f"例如\"Smith等（20XX）在《Nature XX》上提出...\"]。"
            f"国内研究起步相对较晚，但近年来进展迅速。"
            f"[需要补充：3至5篇代表性中文文献综述，含作者、年份、发表期刊及核心结论]。"
            f"综合现有文献可见，当前研究在[需要补充：具体研究空白]方面尚缺乏系统性探讨，"
            f"而这正是本项目拟填补的关键空白。"
        )

    def _gen_innovation_objectives(self, info: dict) -> str:
        tech = info.get("technology", "相关技术")
        problem = info.get("problem", "关键问题")
        return (
            f"本项目的总体研究目标为："
            f"基于{tech}的理论框架，围绕{problem}这一核心科学问题，"
            f"提出具有原创性的解决方案，并通过严格的实验验证其有效性与优越性。"
            f"具体而言，本项目设定以下三项递进式研究目标："
            f"其一，[需要补充：具体目标1，须包含可量化的性能指标，"
            f"如\"构建XX模型，在XX数据集上达到XX%的准确率\"]；"
            f"其二，[需要补充：具体目标2，须阐明理论贡献，"
            f"如\"揭示XX机制的作用机理，建立XX与XX之间的定量关系\"]；"
            f"其三，[需要补充：具体目标3，须体现实践价值，"
            f"如\"开发XX原型系统，在XX场景下完成验证性实验\"]。"
            f"\n\n"
            f"围绕上述目标，本项目的研究内容涵盖以下三个维度。"
            f"第一，[需要补充：研究内容1的具体阐述，"
            f"说明\"研究什么\"\"为什么研究\"以及\"如何研究\"]。"
            f"第二，[需要补充：研究内容2的具体阐述]。"
            f"第三，[需要补充：研究内容3的具体阐述]。"
            f"\n\n"
            f"本项目拟解决的关键科学问题包括："
            f"（1）{problem}的内在机理尚不明确，"
            f"现有理论模型无法准确描述[需要补充：具体物理或数学过程]，"
            f"需建立新的理论框架以揭示其本质规律；"
            f"（2）现有方法在[需要补充：具体技术瓶颈]方面存在原理性局限，"
            f"需提出突破性的算法设计以克服上述约束；"
            f"（3）实验验证体系的缺失导致理论成果难以向工程实践转化，"
            f"需构建系统的实验平台以支撑全链条验证。"
        )

    def _gen_innovation_methodology(self, info: dict) -> str:
        tech = info.get("technology", "相关技术")
        solution = info.get("solution", "解决方案")
        return (
            f"本项目在研究方法上采用理论分析与实验验证并重的复合研究范式。"
            f"在理论研究层面，首先运用文献计量学方法对{tech}领域的核心文献进行系统性梳理，"
            f"通过知识图谱构建识别研究热点与演进趋势，"
            f"从而为后续研究奠定坚实的理论基础。"
            f"在实验研究层面，本项目设计并实施三组递进式实验："
            f"实验一旨在验证[需要补充：实验名称与目的]，"
            f"通过控制[需要补充：自变量]观测[需要补充：因变量]的变化规律，"
            f"数据采集频率为[需要补充：具体参数]，"
            f"样本量不少于[需要补充：具体数字]；"
            f"实验二旨在探究[需要补充：实验目的]，"
            f"采用[需要补充：实验设计方法，如单因素方差分析或多因素正交设计]，"
            f"重点考察[需要补充：关键影响因素]对实验结果的作用机制；"
            f"实验三为验证性实验，"
            f"旨在检验前述实验结论的稳健性与可重复性。"
            f"\n\n"
            f"技术路线方面，本项目以{tech}为基础，"
            f"通过{solution}实现核心研究目标。"
            f"具体技术路线可概括为以下阶段："
            f"首先，[需要补充：技术路线第一步，如\"数据采集与预处理\"，"
            f"并说明所使用的工具与标准]；"
            f"其次，[需要补充：技术路线第二步，如\"模型构建与参数优化\"，"
            f"并说明核心算法原理]；"
            f"再次，[需要补充：技术路线第三步，如\"实验验证与性能评估\"，"
            f"并说明评价指标体系]；"
            f"最后，[需要补充：技术路线第四步，如\"结果分析与理论提炼\"]。"
            f"[需要补充：建议在此处插入技术路线图，以流程图形式呈现研究步骤与逻辑关系]。"
            f"\n\n"
            f"数据分析方法上，本项目采用[需要补充：具体统计方法，"
            f"如\"描述性统计、独立样本t检验、多元回归分析\"等]，"
            f"使用[需要补充：具体软件工具，如Python 3.10配合SciPy 1.11及statsmodels 0.14]"
            f"进行数据处理与建模，"
            f"显著性检验标准设定为p<0.05。"
            f"对于实验过程中产生的异常数据，"
            f"采用[需要补充：具体处理方法，如Grubbs检验或箱线图法]进行识别与处理，"
            f"以确保分析结果的可靠性与有效性。"
        )

    def _gen_innovation_innovation_points(self, info: dict) -> str:
        tech = info.get("technology", "相关技术")
        innovation = info.get("innovation", "")
        return (
            f"本项目在理论层面提出了一套新的分析框架，"
            f"其核心创新在于[需要补充：理论创新的具体阐述，"
            f"如\"首次将XX理论引入XX领域，建立了XX与XX之间的映射关系\"]。"
            f"与现有理论相比，该框架在[需要补充：具体对比维度，如解释力、适用范围或预测精度]"
            f"方面具有显著优势，"
            f"能够有效解释[需要补充：现有理论无法解释的实验现象或工程问题]。"
            f"\n\n"
            f"在方法层面，本项目基于{tech}提出了一种改进的算法设计。"
            f"现有方法在[需要补充：现有方法的具体缺陷，如\"计算复杂度过高\"或\"对噪声敏感\"]"
            f"方面存在原理性不足，"
            f"导致其在[需要补充：具体应用场景]中的表现难以达到工程实用标准。"
            f"本项目所提方法通过[需要补充：核心改进策略]"
            f"有效克服了上述局限，"
            f"实验结果表明[需要补充：与基准方法的对比数据，如\"相较XX方法，"
            f"精度提升XX%，运行时间缩短XX%\"]。"
            f"{innovation if innovation else '[需要补充：方法创新点的进一步阐述]' }"
            f"\n\n"
            f"在应用层面，本项目首次将{tech}系统性地应用于[需要补充：具体应用领域]，"
            f"填补了该交叉领域的研究空白。"
            f"现有应用研究多集中于[需要补充：已有应用领域]，"
            f"而对于[需要补充：本项目关注的应用方向]缺乏深入探索。"
            f"本项目的应用创新不仅拓展了{tech}的理论边界，"
            f"更为[需要补充：具体行业或场景]提供了可行的技术路径与实施参考。"
        )

    def _gen_innovation_schedule(self, info: dict) -> str:
        duration = info.get("duration_months", 12)
        q1 = duration // 4 or 3
        q2 = duration // 2 or 6
        q3 = q2 + q1
        return (
            f"本项目的研究周期为{duration}个月，"
            f"划分为四个相互衔接的研究阶段，"
            f"每个阶段均设有明确的任务目标与可交付成果。"
            f"第一阶段为文献调研与方案设计期，"
            f"时间跨度为第1至第{q1}个月。"
            f"该阶段的核心任务为系统梳理国内外研究现状，"
            f"明确研究边界与技术路线，"
            f"完成开题报告与实验方案设计。"
            f"预期可交付成果包括文献综述报告1份及实验方案1套。"
            f"[需要补充：具体里程碑及验收标准]。"
            f"\n\n"
            f"第二阶段为核心研究与实验实施期，"
            f"时间跨度为第{q1 + 1}至第{q2}个月。"
            f"该阶段将依据既定技术路线开展核心实验，"
            f"完成[需要补充：具体实验内容]的数据采集与初步分析。"
            f"预期可交付成果包括实验原始数据1套及中期研究报告1份。"
            f"[需要补充：阶段性目标及质量控制措施]。"
            f"\n\n"
            f"第三阶段为数据分析与成果整理期，"
            f"时间跨度为第{q2 + 1}至第{q3}个月。"
            f"该阶段将对前期实验数据进行深入的统计分析，"
            f"提炼研究发现，完成论文初稿撰写。"
            f"预期可交付成果包括学术论文初稿1篇及数据处理报告1份。"
            f"[需要补充：数据分析计划及投稿目标期刊]。"
            f"\n\n"
            f"第四阶段为总结撰写与结题答辩期，"
            f"时间跨度为第{q3 + 1}至第{duration}个月。"
            f"该阶段的主要任务为完善研究报告与学术论文，"
            f"准备结题答辩材料，完成项目验收。"
            f"预期可交付成果包括结题报告1份及答辩PPT1套。"
            f"[需要补充：结题验收标准及后续研究计划]。"
        )

    def _gen_innovation_expected_outcomes(self, info: dict) -> str:
        outcomes = info.get("expected_outcomes", "")
        return (
            f"本项目的预期成果涵盖学术论文、研究报告及技术原型三个维度。"
            f"在学术论文方面，计划在国内外核心期刊发表[需要补充：目标期刊级别与数量，"
            f"如\"SCI/SSCI检索论文1至2篇，或中文核心期刊论文2至3篇\"]，"
            f"论文将围绕[需要补充：具体研究主题]展开，"
            f"系统阐述本项目的理论贡献与实验发现。"
            f"在研究报告方面，计划撰写不少于[需要补充：具体页数，如50页]的系统性研究报告1份，"
            f"内容涵盖研究背景、方法设计、实验过程、数据分析及结论展望等完整章节。"
            f"{outcomes if outcomes else '[需要补充：其他成果形式，如专利、软件著作权或技术原型]' }"
            f"\n\n"
            f"量化指标方面，本项目设定以下可考核目标："
            f"（1）学术成果指标：[需要补充：论文发表数量、影响因子要求或他引预期]；"
            f"（2）技术指标：[需要补充：核心算法在标准测试集上的性能指标，"
            f"如\"准确率达到XX%以上，F1值达到XX以上\"]；"
            f"（3）人才培养指标：[需要补充：本科生参与科研训练的人数及产出]。"
            f"上述指标均与项目研究目标严格对应，"
            f"确保项目执行过程可监控、成果可量化、验收可操作。"
        )

    def _gen_budget(self, info: dict, _project_type: str = "innovation") -> str:
        total = info.get("total_budget", 10000.0)
        project_type = info.get("project_type", _project_type)
        if project_type == "entrepreneurship":
            categories = [
                ("市场调研费", 0.20),
                ("产品开发费", 0.35),
                ("营销推广费", 0.20),
                ("差旅交通费", 0.10),
                ("办公费用", 0.10),
                ("其他", 0.05),
            ]
        else:
            categories = [
                ("资料费", 0.15),
                ("调研差旅费", 0.25),
                ("实验材料费", 0.30),
                ("论文版面费", 0.15),
                ("会议费", 0.10),
                ("其他", 0.05),
            ]

        lines = [
            f"本项目总预算为{total:,.0f}元，"
            f"经费分配遵循\"重点突出、结构合理、厉行节约\"的基本原则，"
            f"各项支出均与项目研究内容直接关联。"
        ]
        for cat, pct in categories:
            amount = total * pct
            lines.append(
                f"{cat}预算为{amount:,.0f}元，占总预算的{pct * 100:.0f}%，"
                f"主要用于[需要补充：{cat}的具体用途说明及必要性论证]。"
            )
        lines.append(
            "上述预算编制严格遵循学校财务管理规定，"
            "每项支出均附有明确的用途说明与合理性论证，"
            "确保经费使用规范、透明、高效。"
        )
        return "\n\n".join(lines)

    def _gen_innovation_research_conditions(self, info: dict) -> str:
        tech = info.get("technology", "相关技术")
        advisor = info.get("advisor", "")
        dept = info.get("department", "")
        return (
            f"项目组在{tech}领域已具备一定的理论与实验基础。"
            f"在前期学习中，团队成员系统修读了[需要补充：相关课程名称]等核心课程，"
            f"掌握了[需要补充：具体技能或理论知识]等必要的基础能力。"
            f"此外，团队成员曾参与[需要补充：已参与的科研项目或实验训练名称]，"
            f"积累了[需要补充：具体的科研经验或技术能力]等实践经验。"
            f"\n\n"
            f"实验条件方面，本项目依托{dept}的科研平台，"
            f"可使用[需要补充：实验室名称及主要设备清单，"
            f"如\"高性能计算集群（XX核/XX GB内存）\"\"XX型号实验仪器\"等]。"
            f"软件资源方面，可使用[需要补充：具体软件平台，"
            f"如Python 3.10、MATLAB R2023b、ANSYS等]进行建模与仿真。"
            f"数据资源方面，可获取[需要补充：公开数据集或自建数据资源]。"
            f"{f'指导教师{advisor}在相关领域具有丰富的研究积累，' if advisor else ''}"
            f"[需要补充：导师学术背景及可为项目提供的具体资源支持]。"
            f"\n\n"
            f"团队构成方面，项目组成员来自[需要补充：相关专业背景]，"
            f"专业结构合理，具备[需要补充：技能互补性说明]。"
            f"团队分工明确，负责人统筹项目全局，"
            f"成员分别负责[需要补充：具体分工内容]。"
            f"上述研究基础与条件为本项目的顺利实施提供了坚实保障。"
        )

    # -- Entrepreneurship fallback generators --

    def _gen_entrepreneurship_abstract(self, info: dict) -> str:
        tech = info.get("technology", "相关技术")
        market = info.get("target_market", "目标市场")
        solution = info.get("solution", "解决方案")
        return (
            f"本项目基于{tech}，面向{market}，"
            f"致力于提供{solution}。"
            f"当前，{market}领域存在[需要补充：具体未被满足的市场需求]，"
            f"现有产品或服务在[需要补充：具体维度，如效率、成本或用户体验]"
            f"方面难以达到用户预期。"
            f"据[需要补充：权威数据来源]统计，"
            f"该细分市场规模已达[需要补充：具体数值]亿元，"
            f"年复合增长率保持在[需要补充：具体百分比]以上，"
            f"市场增长潜力巨大。"
            f"\n\n"
            f"本项目的核心竞争优势体现在三个层面。"
            f"技术层面，项目基于{tech}构建了差异化的技术方案，"
            f"在[需要补充：核心技术指标]方面较现有方案具有显著优势。"
            f"团队层面，项目组成员具备[需要补充：团队核心能力的具体描述]，"
            f"且已获得[需要补充：已有资源或合作意向]。"
            f"市场层面，项目通过[需要补充：市场进入策略]"
            f"建立了先发优势，形成了一定的竞争壁垒。"
        )

    def _gen_entrepreneurship_overview(self, info: dict) -> str:
        tech = info.get("technology", "相关技术")
        problem = info.get("problem", "行业痛点")
        solution = info.get("solution", "解决方案")
        market = info.get("target_market", "目标市场")
        return (
            f"{market}行业近年来经历了快速的技术变革与市场扩容，"
            f"但在高速发展的背后，{problem}已成为制约行业进一步升级的关键瓶颈。"
            f"现有解决方案主要依赖[需要补充：现有技术路径]，"
            f"其在[需要补充：具体性能或功能维度]方面存在明显短板，"
            f"导致用户在实际使用过程中面临[需要补充：具体使用障碍]。"
            f"据[需要补充：行业报告或调研数据来源]数据显示，"
            f"[需要补充：具体痛点数据，如\"超过XX%的用户反映现有方案无法满足XX需求\"]。"
            f"\n\n"
            f"针对上述行业痛点，本项目提出基于{tech}的差异化解决方案。"
            f"该方案的核心思路为[需要补充：技术原理或商业模式的简要阐述]，"
            f"相较于现有方案，在[需要补充：核心对比维度]方面实现了突破。"
            f"目前，项目已完成[需要补充：产品开发阶段，如\"概念验证\"\"原型开发\"或\"小批量试产\"]，"
            f"初步测试结果表明[需要补充：MVP验证数据，如\"用户满意度达XX%\"\"转化率达XX%\"]。"
            f"[需要补充：建议在此处插入产品原型示意图或功能架构图]。"
        )

    def _gen_entrepreneurship_market_analysis(self, info: dict) -> str:
        market = info.get("target_market", "目标市场")
        return (
            f"本项目的目标市场为{market}，"
            f"需进一步细分为[需要补充：具体细分市场及划分依据]。"
            f"从市场边界界定来看，"
            f"本项目所聚焦的细分领域在产业链中处于[需要补充：产业链位置]环节，"
            f"其上游为[需要补充：上游供应商类型]，"
            f"下游为[需要补充：下游客户类型]，"
            f"市场边界清晰，目标客户群体明确。"
            f"\n\n"
            f"市场规模方面，本项目采用TAM、SAM、SOM三级分析法进行测算。"
            f"TAM（总可用市场）方面，据[需要补充：权威数据来源]统计，"
            f"{market}领域的全球市场规模约为[需要补充：具体数值]亿元。"
            f"SAM（可服务市场）方面，"
            f"考虑到[需要补充：地域或业务范围的限制条件]，"
            f"本项目可触达的市场规模约为[需要补充：具体数值]亿元。"
            f"SOM（可获得市场）方面，"
            f"基于项目初期的资源约束与运营能力，"
            f"预计首年可获取的市场份额约为[需要补充：具体数值]万元。"
            f"\n\n"
            f"用户画像方面，本项目的核心用户群体具有以下特征："
            f"[需要补充：具体的人口统计学特征、行为特征及需求特征]。"
            f"用户调研结果显示，"
            f"该群体对[需要补充：核心需求点]的付费意愿较强，"
            f"可接受的客单价区间为[需要补充：具体价格区间]。"
            f"市场需求方面，"
            f"[需要补充：用户访谈或问卷调研的核心发现，"
            f"如\"在对XX名目标用户的问卷调研中，XX%的受访者表示存在XX痛点\"]。"
        )

    def _gen_entrepreneurship_product_service(self, info: dict) -> str:
        tech = info.get("technology", "相关技术")
        solution = info.get("solution", "解决方案")
        return (
            f"本项目基于{tech}，提供{solution}。"
            f"产品整体架构可分为[需要补充：具体层级数，如\"三层\"或\"四层\"]，"
            f"分别为[需要补充：各层级的名称及功能概述，如\"数据采集层、算法处理层、应用展示层\"]。"
            f"[需要补充：建议在此处插入产品架构图或功能模块图]。"
            f"\n\n"
            f"核心功能方面，产品主要具备以下三项功能模块。"
            f"第一，[需要补充：功能1的名称与详细描述，"
            f"说明该功能解决的用户问题及用户价值，如\"智能诊断模块："
            f"基于深度学习算法对用户上传的数据进行实时分析，"
            f"诊断准确率达到XX%以上，响应时间低于XX秒\"]。"
            f"第二，[需要补充：功能2的名称与详细描述]。"
            f"第三，[需要补充：功能3的名称与详细描述]。"
            f"\n\n"
            f"技术方案方面，本项目采用[需要补充：核心技术栈，如\"前后端分离架构，"
            f"前端基于React 18，后端基于Python FastAPI，"
            f"算法层基于PyTorch 2.0\"]。"
            f"核心算法的实现原理为[需要补充：技术原理的简要阐述，"
            f"需兼顾专业性与可读性，使非技术背景的评审专家亦能理解]。"
            f"数据处理流程方面，"
            f"[需要补充：数据采集、清洗、存储、分析的全流程说明]。"
        )

    def _gen_entrepreneurship_business_model(self, info: dict) -> str:
        market = info.get("target_market", "目标市场")
        return (
            f"本项目的价值主张可概括为："
            f"为{market}提供[需要补充：具体价值描述，须量化，"
            f"如\"将XX效率提升XX%、将XX成本降低XX%\"]。"
            f"该价值主张建立在[需要补充：价值创造的核心逻辑]基础之上，"
            f"通过[需要补充：价值传递路径]触达目标用户，"
            f"最终形成可持续的价值捕获机制。"
            f"\n\n"
            f"收入模型方面，本项目采用[需要补充：收入模式类型，"
            f"如\"订阅制+增值服务费\"\"一次性销售+后续维护费\"或\"平台佣金制\"]。"
            f"主要收入来源包括："
            f"（1）[需要补充：收入来源1，如\"基础版订阅费用，"
            f"定价为XX元/月/用户，预期首年签约XX个企业客户\"]；"
            f"（2）[需要补充：收入来源2，如\"高级功能模块的增值服务费，"
            f"定价为XX元/次或XX元/年\"]；"
            f"（3）[需要补充：收入来源3]。"
            f"客单价预计为[需要补充：具体数字]元，"
            f"基于用户调研数据，预期复购率或续费率可达[需要补充：具体百分比]。"
            f"\n\n"
            f"成本结构方面，本项目的主要成本包括固定成本与变动成本两类。"
            f"固定成本主要包括[需要补充：具体项目及金额，"
            f"如\"服务器租赁费用XX元/月、办公场地费用XX元/月\"]。"
            f"变动成本主要包括[需要补充：具体项目及金额，"
            f"如\"单次交付的服务成本XX元、获客成本CAC约XX元\"]。"
            f"经测算，本项目的盈亏平衡点预计出现在[需要补充：具体时间，如\"运营第X季度\"]，"
            f"届时月度收入需达到[需要补充：具体金额]元以覆盖全部成本。"
        )

    def _gen_entrepreneurship_competition(self, info: dict) -> str:
        market = info.get("target_market", "目标市场")
        return (
            f"在竞品分析层面，本项目选取了市场中具有代表性的3至5款产品进行多维度对比分析。"
            f"[需要补充：竞品对比表格，包含竞品名称、定价策略、核心功能、"
            f"用户规模、技术优势、主要劣势等维度]。"
            f"对比分析表明，现有竞品在[需要补充：具体维度]方面表现较好，"
            f"但在[需要补充：本项目所聚焦的差异化维度]方面存在明显不足。"
            f"本项目的差异化定位正是基于对上述竞争空白的精准识别。"
            f"\n\n"
            f"SWOT分析方面，本项目的优势（Strengths）在于[需要补充：具体优势，"
            f"如\"技术壁垒：拥有自主知识产权的核心算法；"
            f"团队优势：成员具备XX领域的复合背景\"]。"
            f"劣势（Weaknesses）在于[需要补充：诚实评估，"
            f"如\"品牌知名度较低、初始资金有限、市场渠道尚在建设中\"]。"
            f"机会（Opportunities）在于[需要补充：市场趋势与政策红利，"
            f"如\"国家XX政策的出台为行业发展提供了制度保障；"
            f"{market}市场规模持续扩大\"]。"
            f"威胁（Threats）在于[需要补充：外部竞争与市场风险，"
            f"如\"行业巨头可能通过价格战挤压初创企业生存空间；"
            f"技术迭代速度较快，需持续研发投入\"]。"
            f"\n\n"
            f"核心竞争力方面，本项目构建了以[需要补充：核心壁垒]"
            f"为基础的竞争护城河。"
            f"该壁垒难以在短期内被竞争对手复制，"
            f"原因在于[需要补充：壁垒的不可复制性分析，"
            f"如\"技术壁垒来源于长期的算法积累与数据沉淀；"
            f"团队壁垒来源于核心成员的行业资源与专业背景\"]。"
        )

    def _gen_entrepreneurship_marketing(self, info: dict) -> str:
        market = info.get("target_market", "目标市场")
        return (
            f"面向{market}，本项目制定了以精准获客为核心的推广策略。"
            f"推广渠道方面，采取线上线下相结合的复合推广模式。"
            f"线上渠道主要包括[需要补充：具体平台及策略，"
            f"如\"搜索引擎营销（SEM）、社交媒体内容营销、行业垂直社区运营\"]，"
            f"预计线上获客成本（CAC）控制在[需要补充：具体金额]元以内。"
            f"线下渠道主要包括[需要补充：具体活动类型，"
            f"如\"行业展会参展、高校宣讲、B端客户定向拜访\"]，"
            f"预计线下转化率为[需要补充：具体百分比]。"
            f"\n\n"
            f"渠道策略方面，本项目优先选择与[需要补充：渠道合作方类型]"
            f"建立战略合作关系，通过[需要补充：合作模式，如\"联合推广、渠道分成或资源置换\"]"
            f"实现快速市场渗透。"
            f"目前，已初步接触[需要补充：具体合作方或渠道名称]，"
            f"合作意向正在洽谈中。"
            f"\n\n"
            f"用户获取方面，冷启动阶段拟采用[需要补充：冷启动策略，"
            f"如\"种子用户招募计划：面向XX高校/社群招募XX名免费体验用户，"
            f"收集使用反馈并迭代产品\"]。"
            f"增长模型方面，预期用户增长遵循[需要补充：增长模型类型，"
            f"如\"病毒系数K=X的病毒式增长模型\"或\"线性增长+阶段性爆发模型\"]，"
            f"关键假设包括[需要补充：增长假设的具体参数，"
            f"如\"月均新增用户XX人、用户留存率XX%、付费转化率XX%\"]。"
            f"上述策略的预算分配与ROI预估已在财务预测章节中详细阐述。"
        )

    def _gen_entrepreneurship_team(self, info: dict) -> str:
        members = info.get("members", [])
        advisor_info = info.get("advisor", "")
        members_text = ""
        if members and isinstance(members, list):
            for m in members:
                if isinstance(m, dict):
                    members_text += (
                        f"{m.get('name', '[姓名]')}，"
                        f"{m.get('major', '[专业]')}专业{m.get('grade', '[年级]')}年级，"
                        f"在团队中担任{m.get('role', '[角色]')}，"
                        f"主要负责[需要补充：该成员的具体职责及能力匹配说明]。"
                    )
                else:
                    members_text += f"{m}，[需要补充：该成员的具体职责及能力匹配说明]。"
        else:
            members_text = (
                "[需要补充：每位成员的姓名、专业、年级、角色及具体职责，"
                "并说明其专业背景与项目的匹配度]。"
            )

        advisor_str = ""
        if advisor_info:
            advisor_str = (
                f"指导教师{advisor_info}在相关领域具有丰富的研究积累与行业资源，"
                f"[需要补充：导师的具体学术背景、研究成果及可为项目提供的指导方向]。"
            )
        else:
            advisor_str = (
                "[需要补充：指导教师的学术背景、研究成果及可为项目提供的资源支持]。"
            )

        return (
            f"本项目团队由[需要补充：团队总人数]名成员组成，"
            f"专业背景涵盖[需要补充：具体专业领域]，"
            f"形成了良好的学科交叉与能力互补格局。"
            f"团队成员的具体构成如下：{members_text}"
            f"\n\n"
            f"组织架构方面，本项目采用扁平化的项目制管理模式。"
            f"项目负责人负责统筹全局、协调资源及对外沟通；"
            f"技术负责人负责产品架构设计与核心算法开发；"
            f"市场负责人负责用户调研、推广执行及商务拓展。"
            f"各成员分工明确、权责清晰，"
            f"通过[需要补充：协作工具或管理机制，如\"周例会+在线协作平台\"]"
            f"保持高效的信息同步与任务协同。"
            f"\n\n"
            f"{advisor_str}"
            f"团队的专业结构、分工安排及导师资源共同构成了本项目的人力资本优势，"
            f"为项目的顺利实施与成果转化提供了坚实保障。"
        )

    def _gen_entrepreneurship_finance(self, info: dict) -> str:
        budget = info.get("total_budget", 10000.0)
        return (
            f"收入预测方面，基于市场分析与商业模式设计，"
            f"本项目对未来三年的营业收入进行了审慎预测。"
            f"第一年（运营启动期），预计实现营业收入[需要补充：具体金额]元，"
            f"主要来源于[需要补充：首批收入来源，如\"种子客户的签约收入\"]。"
            f"第二年（市场拓展期），随着用户规模的扩大与品牌知名度的提升，"
            f"预计实现营业收入[需要补充：具体金额]元，"
            f"同比增长[需要补充：增长率]。"
            f"第三年（规模盈利期），"
            f"预计实现营业收入[需要补充：具体金额]元，"
            f"主要增长驱动因素为[需要补充：具体驱动因素，如\"复购率提升、客单价增长及新渠道拓展\"]。"
            f"上述预测建立在[需要补充：关键假设，如\"月均新增用户XX人、客单价XX元、毛利率XX%\"]"
            f"基础之上，具有明确的推导逻辑。"
            f"\n\n"
            f"成本预算方面，启动资金为{budget:,.0f}元，"
            f"主要用于[需要补充：资金的具体用途分配]。"
            f"固定成本方面，年度固定支出约为[需要补充：具体金额]元，"
            f"主要包括[需要补充：具体项目]。"
            f"变动成本方面，单位变动成本约为[需要补充：具体金额]元，"
            f"随业务量增长呈线性增长趋势。"
            f"\n\n"
            f"盈亏平衡分析方面，经测算，"
            f"本项目的盈亏平衡点为月度营业收入[需要补充：具体金额]元，"
            f"对应月度活跃用户数约为[需要补充：具体数字]人。"
            f"按照当前的市场拓展计划，"
            f"预计在运营第[需要补充：具体季度或月份]实现盈亏平衡。"
            f"投资回报期预计为[需要补充：具体时间]，"
            f"内部收益率（IRR）预计为[需要补充：具体百分比]。"
            f"上述财务指标表明本项目在财务层面具有可行性。"
        )

    def _gen_entrepreneurship_risk(self, info: dict) -> str:
        return (
            f"市场风险方面，本项目面临的主要市场风险包括市场接受度不确定及竞争对手反应两个方面。"
            f"市场接受度不确定的风险表现为："
            f"目标用户对本项目的[需要补充：具体产品或服务]"
            f"可能存在认知不足或付费意愿低于预期的情形。"
            f"针对该风险，本项目拟采取[需要补充：具体应对措施，"
            f"如\"通过免费试用降低用户决策门槛、建立用户反馈闭环加速产品迭代\"]。"
            f"竞争对手反应的风险表现为："
            f"现有市场参与者可能通过价格战、功能模仿或渠道封锁等方式挤压本项目的生存空间。"
            f"针对该风险，本项目拟采取[需要补充：具体应对措施，"
            f"如\"加速技术壁垒构建、申请核心专利保护、建立用户数据护城河\"]。"
            f"\n\n"
            f"技术风险方面，本项目面临的主要技术风险包括技术实现难度超预期及技术路线调整两个方面。"
            f"技术实现难度超预期的风险表现为："
            f"[需要补充：具体技术难点]可能在实际开发过程中遇到未预见的技术障碍，"
            f"导致开发周期延长或性能指标无法达标。"
            f"针对该风险，本项目拟采取[需要补充：具体应对措施，"
            f"如\"设置技术预研阶段、建立技术备选方案、引入外部技术顾问\"]。"
            f"技术路线调整的风险表现为："
            f"行业技术标准的更新或颠覆性技术的出现可能使现有技术路线面临淘汰风险。"
            f"针对该风险，本项目拟采取[需要补充：具体应对措施，"
            f"如\"保持技术敏感性、预留技术架构的可扩展性、建立技术趋势监测机制\"]。"
            f"\n\n"
            f"综合上述风险评估，本项目已建立了覆盖风险识别、评估、应对与监控的全流程风险管理机制，"
            f"确保在风险事件发生时能够快速响应、有效处置。"
        )

    def _gen_entrepreneurship_implementation(self, info: dict) -> str:
        duration = info.get("duration_months", 12)
        return (
            f"短期计划方面，项目启动后的前{duration // 3}个月为核心产品开发期。"
            f"该阶段的主要任务包括完成[需要补充：具体任务，"
            f"如\"产品MVP开发、核心功能测试、种子用户招募\"]。"
            f"里程碑一设定为[需要补充：具体里程碑名称及验收标准，"
            f"如\"完成产品MVP上线，获得不少于XX名种子用户的有效反馈\"]，"
            f"预计完成时间为第[需要补充：具体月份]个月。"
            f"\n\n"
            f"中期计划方面，第{duration // 3 + 1}至第{duration * 2 // 3}个月为市场推广与运营优化期。"
            f"该阶段的主要任务包括[需要补充：具体任务，"
            f"如\"正式市场推广、渠道合作洽谈、产品迭代优化、商业模式验证\"]。"
            f"里程碑二设定为[需要补充：具体里程碑名称及验收标准，"
            f"如\"实现月度活跃用户突破XX人，月度经常性收入（MRR）达到XX元\"]，"
            f"预计完成时间为第[需要补充：具体月份]个月。"
            f"\n\n"
            f"长期发展方面，项目完成后将进入规模化运营阶段，"
            f"重点推进[需要补充：长期战略方向，如\"区域市场扩张、产品线延伸或战略融资\"]。"
            f"为确保项目各阶段目标的有效达成，"
            f"本项目建立了以时间节点、量化指标与验收标准为核心的里程碑管理体系。"
            f"关键里程碑节点可概括为[需要补充：里程碑表格，"
            f"含时间、里程碑名称、验收标准及负责人信息]。"
        )

    # -- Generic fallback --

    def _gen_generic(self, section_template: dict, info: dict) -> str:
        title = section_template.get("title", "")
        subsections = section_template.get("subsections", [])
        word_count = section_template.get("word_count", 400)

        paragraphs = []
        for sub in subsections:
            paragraphs.append(
                f"关于{sub}，[需要补充：该部分的具体内容，"
                f"须以连贯的学术段落形式撰写，"
                f"字数约{word_count // len(subsections) if subsections else word_count}字，"
                f"段首为主题句，段内展开论证，段末作小结]。"
            )

        return "\n\n".join(paragraphs)
