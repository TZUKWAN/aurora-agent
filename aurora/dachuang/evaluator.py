"""Dachuang application evaluator with multi-factor keyword analysis."""

import json
import logging
import os
from typing import Dict, List, Optional

from aurora.config import load_config, Config

logger = logging.getLogger(__name__)

LLM_SYSTEM_PROMPT = (
    "你是大学生创新创业训练计划评审专家。"
    "严格按照评审标准对各维度打分（0-100），给出具体反馈和改进建议。"
    "返回JSON格式。"
)

INNOVATION_DIMS = [
    {"name": "选题价值", "weight": 0.25, "description": "选题的理论意义和实际应用价值"},
    {"name": "研究方案可行性", "weight": 0.25, "description": "技术路线清晰、方法得当"},
    {"name": "创新性", "weight": 0.30, "description": "思路新颖、方法创新、有独到见解"},
    {"name": "团队能力", "weight": 0.10, "description": "专业背景匹配、分工明确"},
    {"name": "预期成果", "weight": 0.10, "description": "成果形式明确、可量化"},
]

ENTREPRENEURSHIP_DIMS = [
    {"name": "创新性", "weight": 0.40, "description": "原始创意价值、突破性"},
    {"name": "团队情况", "weight": 0.30, "description": "成员背景、分工互补"},
    {"name": "商业性", "weight": 0.25, "description": "商业模式完整性与可行性"},
    {"name": "带动就业", "weight": 0.05, "description": "发展战略和规模扩张合理性"},
]


class DachuangEvaluator:
    """Evaluate Dachuang applications using keyword-based multi-factor analysis."""

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

    def _get_dimensions(self, project_type: str) -> list:
        if project_type == "entrepreneurship":
            return ENTREPRENEURSHIP_DIMS
        return INNOVATION_DIMS

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(
        self,
        project_info: dict,
        application: dict,
        project_type: str = "innovation",
    ) -> dict:
        """Evaluate a complete Dachuang application.

        Args:
            project_info: Project details dictionary.
            application: Generated application with sections.
            project_type: "innovation" or "entrepreneurship".

        Returns:
            Evaluation result with scores per dimension and overall score.
        """
        dimensions = self._get_dimensions(project_type)

        # Try LLM evaluation first
        if self.llm_client:
            llm_result = self._llm_evaluate(project_info, application, dimensions, project_type)
            if llm_result:
                return llm_result

        # Fallback to keyword analysis
        return self._keyword_evaluate(project_info, application, dimensions, project_type)

    # ------------------------------------------------------------------
    # LLM evaluation
    # ------------------------------------------------------------------

    def _llm_evaluate(
        self,
        project_info: dict,
        application: dict,
        dimensions: list,
        project_type: str,
    ) -> Optional[dict]:
        """Attempt LLM-based evaluation."""
        try:
            model_name = self.config.model.name or os.environ.get("AURORA_MODEL", "glm-4.7-flash")

            dim_descriptions = "\n".join(
                f"- {d['name']}（权重{d['weight']:.0%}）：{d['description']}"
                for d in dimensions
            )

            sections_text = ""
            for section_id, section_data in application.get("sections", {}).items():
                if isinstance(section_data, dict):
                    sections_text += f"\n【{section_data.get('title', section_id)}】\n"
                    sections_text += section_data.get("content", "")[:500] + "\n"

            prompt = (
                f"项目信息：\n{json.dumps(project_info, ensure_ascii=False, indent=2)}\n\n"
                f"申报书内容摘要：\n{sections_text}\n\n"
                f"评估维度：\n{dim_descriptions}\n\n"
                f"项目类型：{'创新训练' if project_type == 'innovation' else '创业训练'}\n\n"
                f"请对每个维度打分（0-100），给出具体反馈和改进建议。\n"
                f"严格返回以下JSON格式：\n"
                f'{{"dimensions": [{{"name": "维度名", "score": 85, "feedback": "具体反馈", "suggestions": ["建议1", "建议2"]}}]}}'
            )

            resp = self.llm_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": LLM_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=2048,
            )

            content = resp.choices[0].message.content or ""
            if not content.strip():
                rc = getattr(resp.choices[0].message, "reasoning_content", None)
                if rc and rc.strip():
                    content = rc

            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            data = json.loads(content)
            llm_dims = data.get("dimensions", [])

            results = {
                "project_type": project_type,
                "dimensions": [],
                "overall_score": 0.0,
                "feedback": "",
                "suggestions": [],
            }

            dim_map = {d["name"]: d for d in dimensions}
            total_weight = 0.0
            weighted_score = 0.0

            for dim_data in llm_dims:
                name = dim_data.get("name", "")
                dim_config = dim_map.get(name)
                if not dim_config:
                    continue

                score = min(max(float(dim_data.get("score", 60)), 0), 100)
                weight = dim_config["weight"]

                results["dimensions"].append({
                    "name": name,
                    "weight": weight,
                    "score": score,
                    "feedback": dim_data.get("feedback", ""),
                    "suggestions": dim_data.get("suggestions", []),
                })

                weighted_score += score * weight
                total_weight += weight

            if total_weight > 0:
                results["overall_score"] = round(weighted_score / total_weight, 2)

            results["feedback"] = self._generate_summary_feedback(results)
            results["suggestions"] = self._generate_summary_suggestions(results)

            return results

        except Exception as e:
            logger.debug(f"LLM evaluation failed, falling back to keyword analysis: {e}")
            return None

    # ------------------------------------------------------------------
    # Keyword-based evaluation
    # ------------------------------------------------------------------

    def _keyword_evaluate(
        self,
        project_info: dict,
        application: dict,
        dimensions: list,
        project_type: str,
    ) -> dict:
        """Evaluate using multi-factor keyword analysis."""
        results = {
            "project_type": project_type,
            "dimensions": [],
            "overall_score": 0.0,
            "feedback": "",
            "suggestions": [],
        }

        # Merge project info and application content for analysis
        combined_text = self._build_combined_text(project_info, application)

        total_weight = 0.0
        weighted_score = 0.0

        for dim in dimensions:
            score, feedback, suggestions = self._evaluate_dimension(
                dim, project_info, combined_text, project_type
            )
            results["dimensions"].append({
                "name": dim["name"],
                "weight": dim["weight"],
                "score": score,
                "feedback": feedback,
                "suggestions": suggestions,
            })
            weighted_score += score * dim["weight"]
            total_weight += dim["weight"]

        if total_weight > 0:
            results["overall_score"] = round(weighted_score / total_weight, 2)

        results["feedback"] = self._generate_summary_feedback(results)
        results["suggestions"] = self._generate_summary_suggestions(results)

        return results

    def _build_combined_text(self, project_info: dict, application: dict) -> str:
        """Build a combined text string from project info and application sections."""
        parts = []
        for value in project_info.values():
            if isinstance(value, str) and value:
                parts.append(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        parts.extend(str(v) for v in item.values() if v)
                    else:
                        parts.append(str(item))

        sections = application.get("sections", {})
        for section_data in sections.values():
            if isinstance(section_data, dict):
                content = section_data.get("content", "")
                if content:
                    parts.append(content)

        return " ".join(parts)

    def _evaluate_dimension(
        self, dim: dict, project_info: dict, combined_text: str, project_type: str
    ) -> tuple:
        """Evaluate a single dimension. Returns (score, feedback, suggestions)."""
        evaluators = {
            "选题价值": self._evaluate_topic_value,
            "研究方案可行性": self._evaluate_methodology_feasibility,
            "创新性": self._evaluate_innovation,
            "团队能力": self._evaluate_team_capability,
            "预期成果": self._evaluate_expected_outcomes,
            "团队情况": self._evaluate_team_background,
            "商业性": self._evaluate_business_viability,
            "带动就业": self._evaluate_employment,
        }

        evaluator = evaluators.get(dim["name"])
        if evaluator:
            return evaluator(project_info, combined_text)
        return self._evaluate_generic(combined_text)

    # -- Dimension evaluators --

    def _evaluate_topic_value(self, info: dict, text: str) -> tuple:
        score = 50.0
        feedback_parts = []
        suggestions = []

        problem = info.get("problem", "")
        technology = info.get("technology", "")
        target_market = info.get("target_market", "")

        if problem and len(problem) > 10:
            score += 10
            feedback_parts.append("问题描述较为具体")
        else:
            suggestions.append("建议细化研究问题的表述，明确问题的具体表现和影响范围")

        if technology and len(technology) > 3:
            score += 8
            feedback_parts.append("技术方向明确")

        high_value_keywords = ["国家战略", "社会需求", "产业升级", "卡脖子", "前沿", "交叉学科"]
        hits = sum(1 for kw in high_value_keywords if kw in text)
        if hits >= 2:
            score += 12
            feedback_parts.append("选题具有较高的现实意义")
        elif hits == 1:
            score += 6

        reference_keywords = ["文献", "研究现状", "国内外", "综述", "前沿"]
        ref_hits = sum(1 for kw in reference_keywords if kw in text)
        if ref_hits >= 2:
            score += 10
            feedback_parts.append("研究现状调研充分")
        elif ref_hits == 0:
            suggestions.append("建议补充国内外研究现状的文献综述")

        if target_market:
            score += 5
            feedback_parts.append("应用场景有明确方向")

        if score < 70:
            suggestions.append("建议明确选题的理论意义和实际应用价值")
            suggestions.append("补充行业数据和政策背景支撑选题的必要性")

        return min(score, 100), "，".join(feedback_parts) or "选题价值需进一步论证", suggestions

    def _evaluate_methodology_feasibility(self, info: dict, text: str) -> tuple:
        score = 50.0
        feedback_parts = []
        suggestions = []

        method_keywords = ["实验", "调研", "分析", "设计", "模型", "仿真", "验证", "测试", "对比"]
        method_hits = sum(1 for kw in method_keywords if kw in text)
        if method_hits >= 4:
            score += 15
            feedback_parts.append("研究方法描述详细")
        elif method_hits >= 2:
            score += 8
            feedback_parts.append("研究方法有一定描述")

        roadmap_keywords = ["技术路线", "步骤", "阶段", "流程", "方案", "路径"]
        roadmap_hits = sum(1 for kw in roadmap_keywords if kw in text)
        if roadmap_hits >= 2:
            score += 12
            feedback_parts.append("技术路线有规划")
        elif roadmap_hits == 0:
            suggestions.append("建议补充清晰的技术路线图")

        schedule_keywords = ["进度", "时间", "阶段", "里程碑", "节点"]
        schedule_hits = sum(1 for kw in schedule_keywords if kw in text)
        if schedule_hits >= 2:
            score += 8
            feedback_parts.append("进度安排合理")

        budget = info.get("total_budget", 0)
        if budget and budget > 0:
            score += 5
            feedback_parts.append("经费预算有规划")

        data_keywords = ["数据", "样本", "采集", "统计", "指标"]
        data_hits = sum(1 for kw in data_keywords if kw in text)
        if data_hits >= 2:
            score += 8
            feedback_parts.append("数据方案有考虑")

        if score < 70:
            suggestions.append("建议细化技术路线，明确每阶段的研究方法和预期产出")
            suggestions.append("补充实验设计的具体参数和变量控制方案")

        return min(score, 100), "，".join(feedback_parts) or "研究方案可行性需完善", suggestions

    def _evaluate_innovation(self, info: dict, text: str) -> tuple:
        score = 50.0
        feedback_parts = []
        suggestions = []

        innovation = info.get("innovation", "")
        technology = info.get("technology", "")

        tech_keywords = {
            "ai": 5, "人工智能": 5, "大模型": 8, "llm": 6,
            "区块链": 5, "物联网": 5, "大数据": 4, "云计算": 3,
            "5g": 4, "量子": 8, "深度学习": 7, "机器学习": 5,
            "计算机视觉": 5, "nlp": 5, "边缘计算": 5, "数字孪生": 6,
        }
        tech_lower = technology.lower()
        tech_score = sum(v for k, v in tech_keywords.items() if k in tech_lower)
        if tech_score > 0:
            score += min(tech_score, 15)
            feedback_parts.append("技术领域具有创新潜力")

        innovation_indicators = ["原创", "自主研发", "首创", "突破", "独创", "专利", "发明", "填补"]
        innovation_hits = sum(1 for kw in innovation_indicators if kw in innovation or kw in text)
        if innovation_hits >= 3:
            score += 15
            feedback_parts.append("创新点表述充实")
        elif innovation_hits >= 1:
            score += 7
            feedback_parts.append("有创新点但论证不够充分")

        novel_keywords = ["交叉", "融合", "新方法", "新思路", "新机制", "新模型", "新框架"]
        novel_hits = sum(1 for kw in novel_keywords if kw in text)
        if novel_hits >= 2:
            score += 10
            feedback_parts.append("具有新颖性表述")

        ip_keywords = ["专利", "软著", "知识产权", "论文", "成果"]
        ip_hits = sum(1 for kw in ip_keywords if kw in text)
        if ip_hits >= 2:
            score += 8
            feedback_parts.append("知识产权规划合理")

        if not innovation:
            suggestions.append("必须补充具体的创新点描述")
        if score < 75:
            suggestions.append("需要用具体技术指标或对比数据证明创新性")
        if ip_hits == 0:
            suggestions.append("建议说明知识产权布局计划")

        return min(score, 100), "，".join(feedback_parts) or "创新性待深入论证", suggestions

    def _evaluate_team_capability(self, info: dict, text: str) -> tuple:
        score = 50.0
        feedback_parts = []
        suggestions = []

        members = info.get("members", [])
        if isinstance(members, list) and len(members) >= 2:
            score += 10
            feedback_parts.append("团队规模合理")
            if len(members) >= 4:
                score += 5
                feedback_parts.append("团队配置完善")

        advisor = info.get("advisor", "")
        if advisor:
            score += 10
            feedback_parts.append("有指导教师参与")
        else:
            suggestions.append("建议明确指导教师及其学术背景")

        major_keywords = ["专业", "学科", "背景", "研究方向", "技能"]
        major_hits = sum(1 for kw in major_keywords if kw in text)
        if major_hits >= 2:
            score += 8
            feedback_parts.append("成员专业背景有说明")

        division_keywords = ["分工", "负责", "职责", "协作", "配合"]
        div_hits = sum(1 for kw in division_keywords if kw in text)
        if div_hits >= 2:
            score += 8
            feedback_parts.append("团队分工明确")

        dept = info.get("department", "")
        if dept:
            score += 5
            feedback_parts.append("依托院系明确")

        if score < 65:
            suggestions.append("建议详细说明团队成员的专业背景与项目的匹配度")
            suggestions.append("补充团队成员的分工安排和职责说明")

        return min(score, 100), "，".join(feedback_parts) or "团队能力信息不足", suggestions

    def _evaluate_expected_outcomes(self, info: dict, text: str) -> tuple:
        score = 50.0
        feedback_parts = []
        suggestions = []

        outcomes = info.get("expected_outcomes", "")

        outcome_keywords = ["论文", "报告", "专利", "软著", "成果", "系统", "平台", "模型"]
        outcome_hits = sum(1 for kw in outcome_keywords if kw in outcomes or kw in text)
        if outcome_hits >= 3:
            score += 15
            feedback_parts.append("预期成果形式丰富")
        elif outcome_hits >= 1:
            score += 7
            feedback_parts.append("有初步的成果规划")

        quant_keywords = ["篇", "项", "个", "%", "倍", "次", "用户", "数据集"]
        quant_hits = sum(1 for kw in quant_keywords if kw in text)
        if quant_hits >= 2:
            score += 10
            feedback_parts.append("成果指标有量化")

        schedule_keywords = ["时间", "阶段", "计划", "进度"]
        if any(kw in text for kw in schedule_keywords):
            score += 5
            feedback_parts.append("成果时间有规划")

        if not outcomes:
            suggestions.append("必须补充具体的预期成果描述")
        if quant_hits == 0:
            suggestions.append("建议用具体数字量化预期成果（如论文X篇、专利X项）")
        if score < 70:
            suggestions.append("建议明确成果形式和可量化的考核指标")

        return min(score, 100), "，".join(feedback_parts) or "预期成果需具体化", suggestions

    def _evaluate_team_background(self, info: dict, text: str) -> tuple:
        """Entrepreneurship dimension: team background."""
        score = 50.0
        feedback_parts = []
        suggestions = []

        members = info.get("members", [])
        if isinstance(members, list) and len(members) >= 3:
            score += 12
            feedback_parts.append("创业团队规模充实")
        elif isinstance(members, list) and len(members) >= 2:
            score += 6

        complement_keywords = ["互补", "跨学科", "多元化", "不同专业"]
        if any(kw in text for kw in complement_keywords):
            score += 12
            feedback_parts.append("团队具备互补性")

        exp_keywords = ["创业", "实习", "竞赛", "项目经验", "获奖"]
        exp_hits = sum(1 for kw in exp_keywords if kw in text)
        if exp_hits >= 2:
            score += 10
            feedback_parts.append("团队有相关实践经验")

        advisor = info.get("advisor", "")
        if advisor:
            score += 8
            feedback_parts.append("有导师指导")

        if score < 65:
            suggestions.append("建议突出团队成员的创业经历和相关能力")
            suggestions.append("补充团队成员之间的专业互补性说明")

        return min(score, 100), "，".join(feedback_parts) or "团队信息需补充", suggestions

    def _evaluate_business_viability(self, info: dict, text: str) -> tuple:
        """Entrepreneurship dimension: business model viability."""
        score = 45.0
        feedback_parts = []
        suggestions = []

        model_keywords = ["商业模式", "收入", "盈利", "定价", "订阅", "SaaS", "平台", "佣金"]
        model_hits = sum(1 for kw in model_keywords if kw in text)
        if model_hits >= 3:
            score += 15
            feedback_parts.append("商业模式描述完整")
        elif model_hits >= 1:
            score += 7

        market_keywords = ["市场规模", "目标市场", "用户画像", "市场份额", "TAM"]
        market_hits = sum(1 for kw in market_keywords if kw in text)
        if market_hits >= 2:
            score += 10
            feedback_parts.append("市场分析有数据支撑")

        finance_keywords = ["成本", "预算", "盈亏平衡", "利润", "现金流", "ROI"]
        finance_hits = sum(1 for kw in finance_keywords if kw in text)
        if finance_hits >= 2:
            score += 10
            feedback_parts.append("财务分析有规划")

        competitor_keywords = ["竞品", "竞争", "SWOT", "壁垒", "优势", "差异化"]
        comp_hits = sum(1 for kw in competitor_keywords if kw in text)
        if comp_hits >= 2:
            score += 8
            feedback_parts.append("竞争分析有考虑")

        if model_hits == 0:
            suggestions.append("必须明确商业模式和盈利路径")
        if market_hits == 0:
            suggestions.append("建议补充目标市场规模和用户画像分析")
        if finance_hits == 0:
            suggestions.append("需要提供财务预测和盈亏平衡分析")
        if score < 70:
            suggestions.append("商业计划需要更多数据支撑和逻辑论证")

        return min(score, 100), "，".join(feedback_parts) or "商业性分析需加强", suggestions

    def _evaluate_employment(self, info: dict, text: str) -> tuple:
        """Entrepreneurship dimension: employment driving."""
        score = 40.0
        feedback_parts = []
        suggestions = []

        employment_keywords = ["就业", "岗位", "招聘", "带动", "吸纳", "人才"]
        emp_hits = sum(1 for kw in employment_keywords if kw in text)
        if emp_hits >= 2:
            score += 15
            feedback_parts.append("具备带动就业规划")
        elif emp_hits >= 1:
            score += 7

        social_keywords = ["社会", "公益", "乡村振兴", "扶贫", "区域发展"]
        social_hits = sum(1 for kw in social_keywords if kw in text)
        if social_hits >= 1:
            score += 10
            feedback_parts.append("具有社会价值")

        scale_keywords = ["规模", "扩张", "复制", "连锁", "发展"]
        scale_hits = sum(1 for kw in scale_keywords if kw in text)
        if scale_hits >= 2:
            score += 8
            feedback_parts.append("有规模扩张思路")

        if emp_hits == 0:
            suggestions.append("建议量化带动就业的具体人数和时间表")
        if score < 60:
            suggestions.append("结合国家战略阐述项目的社会价值和就业带动能力")

        return min(score, 100), "，".join(feedback_parts) or "带动就业方面需要补充", suggestions

    def _evaluate_generic(self, text: str) -> tuple:
        return 60.0, "综合表现一般", ["建议进一步完善相关内容"]

    # ------------------------------------------------------------------
    # Summary generation
    # ------------------------------------------------------------------

    def _generate_summary_feedback(self, results: dict) -> str:
        feedback = "综合评价：\n"
        high_scores = [d for d in results["dimensions"] if d["score"] >= 80]
        low_scores = [d for d in results["dimensions"] if d["score"] < 70]

        if high_scores:
            feedback += "优势维度：\n"
            for dim in high_scores[:3]:
                feedback += f"- {dim['name']}：{dim['feedback']}\n"

        if low_scores:
            feedback += "\n待提升维度：\n"
            for dim in low_scores[:3]:
                feedback += f"- {dim['name']}：需要改进\n"

        overall = results.get("overall_score", 0)
        if overall >= 85:
            feedback += f"\n总体评分{overall}分，项目质量优秀。"
        elif overall >= 70:
            feedback += f"\n总体评分{overall}分，项目有一定基础，部分维度需加强。"
        else:
            feedback += f"\n总体评分{overall}分，项目需要大幅完善后再提交。"

        return feedback

    def _generate_summary_suggestions(self, results: dict) -> list:
        suggestions = []
        for dim in results["dimensions"]:
            suggestions.extend(dim["suggestions"])
        return suggestions[:8]
