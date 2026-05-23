"""Evaluation engine for AuroraAgent."""

from typing import Dict, List

from aurora.competition.database import CompetitionDatabase


class EvaluationEngine:
    """Evaluate projects against competition criteria."""

    def __init__(self):
        self._comp_db = CompetitionDatabase()

    def evaluate(
        self,
        project_info: Dict,
        competition_id: str = "internet_plus",
        dimensions: List[str] = None
    ) -> Dict:
        """
        Evaluate a project.

        Args:
            project_info: Project details
            competition_id: Target competition
            dimensions: Specific dimensions to evaluate

        Returns:
            Evaluation results with scores and feedback
        """
        comp = self._comp_db.get_competition(competition_id)
        if not comp:
            return {"error": f"Unknown competition: {competition_id}"}

        default_dims = [d.name for d in comp.evaluation_dimensions]
        target_dims = dimensions or default_dims

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

    def _evaluate_dimension(
        self,
        dimension,
        project_info: Dict
    ) -> (float, str, List[str]):
        """Evaluate a single dimension."""
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

    def _evaluate_innovation(self, info: Dict) -> (float, str, List[str]):
        tech = info.get("technology", "").lower()
        innovation = info.get("innovation", "")

        score = 60.0
        feedback = ""
        suggestions = []

        if "ai" in tech or "人工智能" in tech:
            score += 15
            feedback += "技术创新性强"
        if "原创" in innovation or "自主研发" in innovation:
            score += 10
            feedback += "，具有原创性"
        if "专利" in info.get("intellectual_property", ""):
            score += 10
            feedback += "，知识产权保护完善"

        if score < 70:
            suggestions.append("建议突出技术创新点")
            suggestions.append("考虑申请知识产权保护")

        return min(score, 100), feedback or "创新性一般", suggestions

    def _evaluate_team(self, info: Dict) -> (float, str, List[str]):
        team = info.get("team_background", "")
        info.get("team_members", "")

        score = 60.0
        feedback = ""
        suggestions = []

        if "985" in team or "211" in team or "双一流" in team:
            score += 15
            feedback += "团队学历背景优秀"
        if "创业经验" in team or "项目经验" in team:
            score += 10
            feedback += "，具备相关经验"
        try:
            if int(info.get("team_size", "3")) >= 3:
                score += 10
                feedback += "，团队规模合理"
        except (ValueError, TypeError):
            pass

        if score < 70:
            suggestions.append("建议补充团队背景介绍")
            suggestions.append("考虑引入有经验的成员")

        return min(score, 100), feedback or "团队情况一般", suggestions

    def _evaluate_business_model(self, info: Dict) -> (float, str, List[str]):
        model = info.get("business_model", "")
        revenue = info.get("revenue_model", "")

        score = 60.0
        feedback = ""
        suggestions = []

        if "盈利" in model or "收入" in model:
            score += 15
            feedback += "商业模式清晰"
        if "多元化" in model or revenue:
            score += 10
            feedback += "，收入来源明确"
        if "可扩展" in model:
            score += 10
            feedback += "，具备扩展性"

        if score < 70:
            suggestions.append("建议明确盈利模式")
            suggestions.append("考虑多元化收入来源")

        return min(score, 100), feedback or "商业模式待完善", suggestions

    def _evaluate_employment(self, info: Dict) -> (float, str, List[str]):
        impact = info.get("social_impact", "")

        score = 50.0
        feedback = ""
        suggestions = []

        if "就业" in impact or "岗位" in impact:
            score += 25
            feedback += "具备带动就业潜力"
        if "乡村" in impact or "扶贫" in impact:
            score += 20
            feedback += "，社会价值突出"

        if score < 60:
            suggestions.append("建议突出带动就业的规划")
            suggestions.append("考虑社会责任相关内容")

        return min(score, 100), feedback or "带动就业方面需加强", suggestions

    def _evaluate_education(self, info: Dict) -> (float, str, List[str]):
        team = info.get("team_background", "")

        score = 60.0
        feedback = ""
        suggestions = []

        if "学生" in team or "大学" in team:
            score += 20
            feedback += "符合学生创新创业定位"
        if "专业" in team or "研究" in team:
            score += 15
            feedback += "，专业知识转化较好"

        if score < 70:
            suggestions.append("建议突出学生身份和专业背景")
            suggestions.append("强调知识转化过程")

        return min(score, 100), feedback or "教育维度表现一般", suggestions

    def _evaluate_social_value(self, info: Dict) -> (float, str, List[str]):
        impact = info.get("social_impact", "")

        score = 50.0
        feedback = ""
        suggestions = []

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

    def _evaluate_tech_innovation(self, info: Dict) -> (float, str, List[str]):
        return self._evaluate_innovation(info)

    def _evaluate_team_collaboration(self, info: Dict) -> (float, str, List[str]):
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

    def _evaluate_prospects(self, info: Dict) -> (float, str, List[str]):
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

    def _evaluate_feasibility(self, info: Dict) -> (float, str, List[str]):
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

    def _evaluate_business_value(self, info: Dict) -> (float, str, List[str]):
        revenue = info.get("revenue_model", "")
        market = info.get("market_size", "")

        score = 60.0
        feedback = ""
        suggestions = []

        if "盈利" in revenue or "收入" in revenue:
            score += 20
            feedback += "盈利模式明确"
        if market and int(market.replace("亿", "").replace("万", "")) > 10:
            score += 15
            feedback += "，市场规模大"

        if score < 70:
            suggestions.append("建议明确盈利能力")
            suggestions.append("分析市场规模和增长潜力")

        return min(score, 100), feedback or "商业价值待提升", suggestions

    def _evaluate_team_capability(self, info: Dict) -> (float, str, List[str]):
        return self._evaluate_team(info)

    def _evaluate_generic(self, info: Dict) -> (float, str, List[str]):
        return 60.0, "综合表现一般", ["建议进一步完善相关内容"]

    def _generate_summary_feedback(self, results: Dict) -> str:
        """Generate summary feedback."""
        feedback = "【综合评价】\n"

        high_scores = [d for d in results["dimensions"] if d["score"] >= 80]
        low_scores = [d for d in results["dimensions"] if d["score"] < 70]

        if high_scores:
            feedback += "优势方面：\n"
            for dim in high_scores[:3]:
                feedback += f"- {dim['name']}: {dim['feedback']}\n"

        if low_scores:
            feedback += "\n待改进方面：\n"
            for dim in low_scores[:3]:
                feedback += f"- {dim['name']}: 需要加强\n"

        return feedback

    def _generate_summary_suggestions(self, results: Dict) -> List[str]:
        """Generate summary suggestions."""
        suggestions = []
        for dim in results["dimensions"]:
            suggestions.extend(dim["suggestions"])
        return suggestions[:6]
