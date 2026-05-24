"""Evaluation engine for AuroraAgent."""

import json
import logging
import os
from typing import Dict, List, Optional

from aurora.competition.database import CompetitionDatabase

logger = logging.getLogger(__name__)

LLM_EVAL_PROMPT = """You are an expert competition judge applying the Baiyu Three-Dimensional Logic (百育三维逻辑) evaluation framework. Evaluate this project for {competition_name}.

## Baiyu Three-Dimensional Logic Framework

When evaluating EACH dimension below, you MUST analyze it across three sub-dimensions:

1. **Selection (选题)** - Is the topic/problem well-chosen? Does it address a genuine need? Is the positioning accurate and differentiated? Does the topic have sufficient scope and significance?

2. **Content (内容)** - Is the substance deep and rigorous? Are the technical details, data, and evidence solid? Is the solution well-designed with clear logic? Does the content demonstrate genuine understanding and expertise?

3. **Presentation (呈现)** - Is the delivery clear, compelling, and well-structured? Are visual aids, demos, and narratives effective? Does the presentation inspire confidence and engagement?

For each dimension, consider all three sub-dimensions in your scoring and feedback. A dimension that is strong in content but weak in presentation should score lower and receive feedback about improving delivery.

## Five Barriers Team Diagnostic (五道槛)

Also assess the team across these five barriers that commonly block competition success. Weave these into your feedback where relevant:

1. **Barrier of Cognition (认知槛)** - Does the team truly understand the problem space? Have they avoided surface-level assumptions? Is their industry insight deep enough?

2. **Barrier of Methodology (方法槛)** - Does the team use sound methods for validation, development, and scaling? Is there evidence of structured thinking (e.g., lean startup, design thinking, scientific method)?

3. **Barrier of Execution (执行槛)** - Can the team deliver on their promises? Is there evidence of prototypes, pilots, real users, or measurable milestones? Are timelines realistic?

4. **Barrier of Resources (资源槛)** - Does the team have or have a plan to acquire necessary resources (funding, talent, partnerships, data, infrastructure)?

5. **Barrier of Resilience (韧性槛)** - Does the team show ability to pivot, learn from failure, and persevere? Is there evidence of iteration based on feedback?

Rate each dimension 0-100 with specific feedback and actionable suggestions. In your feedback, reference the relevant sub-dimensions (selection/content/presentation) and any applicable barriers (cognition/methodology/execution/resources/resilience).

Project info:
{project_info}

Dimensions to evaluate:
{dimensions}

Return ONLY a JSON object:
{{
  "dimensions": [
    {{
      "name": "dimension name",
      "score": 85,
      "feedback": "Specific feedback referencing selection/content/presentation and any relevant barriers",
      "suggestions": ["suggestion 1", "suggestion 2"]
    }}
  ]
}}"""


class EvaluationEngine:
    """Evaluate projects against competition criteria."""

    def __init__(self, config=None):
        self._comp_db = CompetitionDatabase()
        self.config = config
        self.llm_client = self._init_llm()

    def _init_llm(self):
        try:
            if self.config is None:
                from aurora.config import load_config
                self.config = load_config()

            api_key = self.config.model.api_key or os.environ.get("AURORA_API_KEY")
            base_url = self.config.model.base_url or os.environ.get("AURORA_BASE_URL")
            if not api_key:
                return None

            from openai import OpenAI
            return OpenAI(api_key=api_key, base_url=base_url)
        except Exception:
            return None

    def evaluate(
        self,
        project_info: Dict,
        competition_id: str = "internet_plus",
        dimensions: List[str] = None
    ) -> Dict:
        """Evaluate a project. Tries LLM first, falls back to keyword matching."""
        comp = self._comp_db.get_competition(competition_id)
        if not comp:
            return {"error": f"Unknown competition: {competition_id}"}

        default_dims = [d.name for d in comp.evaluation_dimensions]
        target_dims = dimensions or default_dims

        # Try LLM evaluation
        if self.llm_client:
            result = self._llm_evaluate(project_info, comp, target_dims)
            if result:
                return result

        # Fallback to keyword evaluation
        return self._keyword_evaluate(project_info, comp, target_dims)

    def _llm_evaluate(self, project_info: Dict, comp, target_dims: List[str]) -> Optional[Dict]:
        """Use LLM for evaluation."""
        try:
            model_name = self.config.model.name or os.environ.get("AURORA_MODEL", "glm-4.7-flash")
            dim_list = "\n".join(f"- {d.name} (weight: {d.weight})" for d in comp.evaluation_dimensions if d.name in target_dims)

            prompt = LLM_EVAL_PROMPT.format(
                competition_name=comp.name,
                project_info=json.dumps(project_info, ensure_ascii=False, indent=2),
                dimensions=dim_list,
            )

            resp = self.llm_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a competition judge. Return only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=2048,
            )

            content = resp.choices[0].message.content or ""
            if not content.strip():
                rc = getattr(resp.choices[0].message, 'reasoning_content', None)
                if rc and rc.strip():
                    content = rc

            # Strip markdown code blocks
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            data = json.loads(content)
            llm_dims = data.get("dimensions", [])

            # Build result in expected format
            results = {
                "competition": comp.name,
                "dimensions": [],
                "overall_score": 0.0,
                "feedback": [],
                "suggestions": [],
            }

            total_weight = 0.0
            weighted_score = 0.0

            dim_map = {d.name: d for d in comp.evaluation_dimensions}

            for dim_data in llm_dims:
                name = dim_data.get("name", "")
                if name not in target_dims:
                    continue
                score = min(max(float(dim_data.get("score", 60)), 0), 100)
                weight = dim_map.get(name, type('obj', (), {'weight': 0.2})()).weight

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
            logger.debug(f"LLM evaluation failed, falling back: {e}")
            return None

    def _keyword_evaluate(self, project_info: Dict, comp, target_dims: List[str]) -> Dict:
        """Keyword-based evaluation (original logic)."""
        results = {
            "competition": comp.name,
            "dimensions": [],
            "overall_score": 0.0,
            "feedback": [],
            "suggestions": [],
        }

        total_weight = 0.0
        weighted_score = 0.0

        for dim in comp.evaluation_dimensions:
            if dim.name not in target_dims:
                continue

            score, dim_feedback, dim_suggestions = self._evaluate_dimension(
                dim, project_info
            )

            results["dimensions"].append({
                "name": dim.name,
                "weight": dim.weight,
                "score": score,
                "feedback": dim_feedback,
                "suggestions": dim_suggestions,
            })

            weighted_score += score * dim.weight
            total_weight += dim.weight

        if total_weight > 0:
            results["overall_score"] = round(weighted_score / total_weight, 2)

        results["feedback"] = self._generate_summary_feedback(results)
        results["suggestions"] = self._generate_summary_suggestions(results)

        return results

    def _evaluate_dimension(self, dimension, project_info: Dict):
        evaluators = {
            "创新性": self._evaluate_innovation,
            "团队情况": self._evaluate_team,
            "商业模式": self._evaluate_business_model,
            "带动就业": self._evaluate_employment,
            "教育维度": self._evaluate_education,
            "社会价值": self._evaluate_social_value,
            "科技创新": self._evaluate_tech_innovation,
            "团队协作": self._evaluate_team_collaboration,
            "发展前景": self._evaluate_prospects,
            "可行性": self._evaluate_feasibility,
            "商业价值": self._evaluate_business_value,
            "团队能力": self._evaluate_team_capability,
        }

        evaluator = evaluators.get(dimension.name)
        if evaluator:
            return evaluator(project_info)
        return self._evaluate_generic(project_info)

    def _evaluate_innovation(self, info: Dict):
        tech = info.get("technology", "").lower()
        innovation = info.get("innovation", "")
        solution = info.get("solution", "")
        score = 50.0
        feedback_parts = []
        suggestions = []

        tech_keywords = {
            "ai": 5, "人工智能": 5, "大模型": 8, "llm": 6,
            "区块链": 5, "物联网": 5, "大数据": 4, "云计算": 3,
            "5g": 4, "量子": 8, "生物技术": 6, "新材料": 6,
            "ar": 4, "vr": 4, "机器人": 6, "自动驾驶": 7,
            "深度学习": 7, "机器学习": 5, "计算机视觉": 5, "nlp": 5,
        }
        tech_score = sum(v for k, v in tech_keywords.items() if k in tech)
        if tech_score > 0:
            score += min(tech_score, 15)
            feedback_parts.append("技术领域具有创新潜力")

        innovation_indicators = ["原创", "自主研发", "首创", "突破", "独创", "专利", "发明"]
        innovation_hits = sum(1 for kw in innovation_indicators if kw in innovation)
        if innovation_hits >= 2:
            score += 12
            feedback_parts.append("创新点表述充实")
        elif innovation_hits == 1:
            score += 6
            feedback_parts.append("有创新点但不够丰富")

        ip_text = info.get("intellectual_property", "")
        if "专利" in ip_text:
            score += 8
            feedback_parts.append("知识产权保护到位")
        if "软著" in ip_text:
            score += 4

        if solution and len(solution) > 20:
            score += 5
            feedback_parts.append("解决方案描述详细")

        if not innovation:
            suggestions.append("建议补充具体创新点描述")
        if not ip_text:
            suggestions.append("建议明确知识产权布局")
        if score < 75:
            suggestions.append("需要用具体技术指标证明创新性（如效率提升X%、成本降低Y%）")

        return min(score, 100), "，".join(feedback_parts) or "创新性待深入论证", suggestions

    def _evaluate_team(self, info: Dict):
        team = info.get("team_background", "")
        score = 50.0
        feedback_parts = []
        suggestions = []

        school_keywords = ["985", "211", "双一流", "北大", "清华", "浙大", "复旦", "上交"]
        if any(kw in team for kw in school_keywords):
            score += 8
            feedback_parts.append("团队学历背景优秀")

        exp_keywords = ["创业经验", "项目经验", "实习", "工作经历", "获奖", "竞赛"]
        exp_hits = sum(1 for kw in exp_keywords if kw in team)
        if exp_hits >= 2:
            score += 10
            feedback_parts.append("团队实践经验丰富")
        elif exp_hits == 1:
            score += 5
            feedback_parts.append("团队有一定实践经验")

        try:
            team_size = int(info.get("team_size", "0"))
            if 3 <= team_size <= 5:
                score += 8
                feedback_parts.append("团队规模合理")
            elif team_size > 5:
                score += 4
                feedback_parts.append("团队规模较大")
        except (ValueError, TypeError):
            pass

        role_keywords = ["技术", "商业", "设计", "市场", "产品"]
        role_hits = sum(1 for kw in role_keywords if kw in team)
        if role_hits >= 3:
            score += 10
            feedback_parts.append("团队角色配置完善")
        elif role_hits >= 1:
            score += 4

        if "导师" in team or "教授" in team or "指导" in team:
            score += 8
            feedback_parts.append("有导师资源支撑")

        if score < 70:
            suggestions.append("建议明确团队成员分工与角色互补性")
        if role_hits < 2:
            suggestions.append("建议补充技术+商业+设计等跨学科成员")
        if "导师" not in team:
            suggestions.append("建议引入行业导师或学术指导")

        return min(score, 100), "，".join(feedback_parts) or "团队信息不足", suggestions

    def _evaluate_business_model(self, info: Dict):
        model = info.get("business_model", "")
        revenue = info.get("revenue_model", "")
        market = info.get("target_market", "")
        score = 50.0
        feedback_parts = []
        suggestions = []

        clarity_keywords = ["订阅", "SaaS", "平台", "电商", "服务费", "广告", "授权", "交易佣金"]
        if any(kw in model.lower() for kw in clarity_keywords):
            score += 12
            feedback_parts.append("商业模式类型明确")
        elif model:
            score += 4

        if revenue:
            score += 8
            feedback_parts.append("收入来源有说明")
        if "多元" in model or "多种" in revenue:
            score += 5
            feedback_parts.append("有多元化收入规划")

        scalability_keywords = ["可扩展", "规模化", "复制", "裂变", "增长"]
        if any(kw in model for kw in scalability_keywords):
            score += 6
            feedback_parts.append("具备扩展性描述")

        if market and len(market) > 5:
            score += 5
            feedback_parts.append("目标市场有定位")

        if not model:
            suggestions.append("必须明确商业模式（SaaS/平台/服务等）")
        if not revenue:
            suggestions.append("建议细化收入来源和客单价")
        if score < 70:
            suggestions.append("需要提供盈亏平衡点(BEP)和投资回报期(ROI)分析")
            suggestions.append("建议补充客户获取成本(CAC)和客户生命周期价值(LTV)")

        return min(score, 100), "，".join(feedback_parts) or "商业模式信息不足", suggestions

    def _evaluate_employment(self, info: Dict):
        impact = info.get("social_impact", "")
        score = 45.0
        feedback_parts = []
        suggestions = []

        employment_keywords = ["就业", "岗位", "招聘", "带动", "吸纳"]
        if any(kw in impact for kw in employment_keywords):
            score += 15
            feedback_parts.append("具备带动就业规划")

        rural_keywords = ["乡村", "农村", "扶贫", "县域", "农业"]
        if any(kw in impact for kw in rural_keywords):
            score += 15
            feedback_parts.append("服务乡村振兴战略")

        social_keywords = ["公益", "助残", "养老", "教育公平", "医疗", "环保"]
        if any(kw in impact for kw in social_keywords):
            score += 10
            feedback_parts.append("具有社会公益价值")

        if len(impact) > 30:
            score += 5
            feedback_parts.append("社会效益描述详细")

        if score < 60:
            suggestions.append("建议量化带动就业的具体人数和时间表")
            suggestions.append("结合国家战略阐述社会价值")
        if not impact:
            suggestions.append("必须补充社会效益和带动就业的说明")

        return min(score, 100), "，".join(feedback_parts) or "带动就业方面需要补充", suggestions

    def _evaluate_education(self, info: Dict):
        team = info.get("team_background", "")
        innovation = info.get("innovation", "")
        score = 50.0
        feedback_parts = []
        suggestions = []

        if "学生" in team or "大学" in team or "在校" in team:
            score += 12
            feedback_parts.append("符合学生创新创业定位")

        if "专业" in team or "研究" in team or "学科" in team:
            score += 8
            feedback_parts.append("体现专业知识转化")

        if "实验室" in team or "课题组" in team or "导师" in team:
            score += 8
            feedback_parts.append("有科研成果转化基础")

        if innovation and ("学习" in innovation or "教育" in innovation or "实践" in innovation):
            score += 5

        if score < 65:
            suggestions.append("建议强调学生身份与专业知识的结合")
            suggestions.append("突出从课程学习到创新创业的转化过程")
        if "导师" not in team:
            suggestions.append("建议说明指导教师的学术背景和指导作用")

        return min(score, 100), "，".join(feedback_parts) or "教育维度需补充", suggestions

    def _evaluate_social_value(self, info: Dict):
        impact = info.get("social_impact", "")
        score = 45.0
        feedback_parts = []
        suggestions = []

        rural_keywords = ["乡村振兴", "三农", "农村", "县域"]
        if any(kw in impact for kw in rural_keywords):
            score += 15
            feedback_parts.append("服务国家乡村振兴战略")

        env_keywords = ["环保", "绿色", "节能", "碳中和", "可持续发展"]
        if any(kw in impact for kw in env_keywords):
            score += 12
            feedback_parts.append("具有环保价值")

        welfare_keywords = ["公益", "助残", "养老", "弱势群体", "教育公平"]
        if any(kw in impact for kw in welfare_keywords):
            score += 12
            feedback_parts.append("具有社会公益价值")

        policy_keywords = ["国家战略", "政策", "一带一路", "健康中国"]
        if any(kw in impact for kw in policy_keywords):
            score += 8
            feedback_parts.append("契合国家政策方向")

        if len(impact) > 30:
            score += 5
            feedback_parts.append("社会价值描述充实")

        if score < 60:
            suggestions.append("建议明确项目的社会价值定位")
            suggestions.append("结合国家战略方向阐述社会意义")
        if not impact:
            suggestions.append("必须补充社会影响描述")

        return min(score, 100), "，".join(feedback_parts) or "社会价值需补充", suggestions
        if "乡村振兴" in impact or "三农" in impact:
            score += 25
            feedback += "服务国家乡村振兴战略"
        if "环保" in impact or "绿色" in impact:
            score += 20
            feedback += "，具有环保价值"
        if "公益" in impact or "社会" in impact:
            score += 20
            feedback += "，社会价值突出"
        if score < 60:
            suggestions.append("建议突出社会价值")
            suggestions.append("结合国家战略方向")
        return min(score, 100), feedback or "社会价值待提升", suggestions

    def _evaluate_tech_innovation(self, info: Dict):
        return self._evaluate_innovation(info)

    def _evaluate_team_collaboration(self, info: Dict):
        team = info.get("team_background", "")
        score = 60.0
        feedback = ""
        suggestions = []
        if "互补" in team or "分工" in team:
            score += 20
            feedback += "团队分工明确"
        if "协作" in team or "配合" in team:
            score += 15
            feedback += "，协作能力强"
        if score < 70:
            suggestions.append("建议明确团队分工")
            suggestions.append("突出团队协作优势")
        return min(score, 100), feedback or "团队协作需加强", suggestions

    def _evaluate_prospects(self, info: Dict):
        plan = info.get("development_plan", "")
        score = 60.0
        feedback = ""
        suggestions = []
        if "规划" in plan or "目标" in plan:
            score += 20
            feedback += "发展规划清晰"
        if "可复制" in plan or "扩张" in plan:
            score += 15
            feedback += "，具备扩张潜力"
        if score < 70:
            suggestions.append("建议制定清晰的发展规划")
            suggestions.append("突出可复制性和成长性")
        return min(score, 100), feedback or "发展前景待明确", suggestions

    def _evaluate_feasibility(self, info: Dict):
        tech = info.get("technology", "")
        model = info.get("business_model", "")
        score = 60.0
        feedback = ""
        suggestions = []
        if "可行" in tech or "成熟" in tech:
            score += 15
            feedback += "技术可行性高"
        if "验证" in model or "试点" in model:
            score += 15
            feedback += "，商业模式已验证"
        if score < 70:
            suggestions.append("建议验证技术可行性")
            suggestions.append("考虑进行试点测试")
        return min(score, 100), feedback or "可行性需验证", suggestions

    def _evaluate_business_value(self, info: Dict):
        revenue = info.get("revenue_model", "")
        market = info.get("market_size", "")
        score = 60.0
        feedback = ""
        suggestions = []
        if "盈利" in revenue or "收入" in revenue:
            score += 20
            feedback += "盈利模式明确"
        if market:
            try:
                if int(market.replace("亿", "").replace("万", "")) > 10:
                    score += 15
                    feedback += "，市场规模大"
            except (ValueError, TypeError):
                pass
        if score < 70:
            suggestions.append("建议明确盈利能力")
            suggestions.append("分析市场规模和增长潜力")
        return min(score, 100), feedback or "商业价值待提升", suggestions

    def _evaluate_team_capability(self, info: Dict):
        return self._evaluate_team(info)

    def _evaluate_generic(self, info: Dict):
        return 60.0, "综合表现一般", ["建议进一步完善相关内容"]

    def _generate_summary_feedback(self, results: Dict) -> str:
        feedback = "综合评价：\n"
        high_scores = [d for d in results["dimensions"] if d["score"] >= 80]
        low_scores = [d for d in results["dimensions"] if d["score"] < 70]
        if high_scores:
            feedback += "优势项：\n"
            for dim in high_scores[:3]:
                feedback += f"- {dim['name']}: {dim['feedback']}\n"
        if low_scores:
            feedback += "\n待提升项：\n"
            for dim in low_scores[:3]:
                feedback += f"- {dim['name']}: 需要改进\n"
        return feedback

    def _generate_summary_suggestions(self, results: Dict) -> List[str]:
        suggestions = []
        for dim in results["dimensions"]:
            suggestions.extend(dim["suggestions"])
        return suggestions[:6]
