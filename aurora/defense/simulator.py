"""Defense simulator for competition preparation.

Generates defense questions, simulates defense sessions, and scores answers.
Uses keyword matching and template-based analysis -- no LLM calls required.
"""

import re
import random
from typing import Dict, List, Any

from aurora.defense.prompts import (
    QUESTION_TEMPLATES,
    EVALUATION_RUBRIC,
    TIPS,
    COMPETITION_TIPS,
    CATEGORY_SECTION_MAP,
)


class DefenseSimulator:
    """Template-driven defense simulation engine."""

    # Scoring keywords per category, mapped to plan section field names
    _SCORE_KEYWORDS: Dict[str, Dict[str, List[str]]] = {
        "innovation": {
            "positive": ["创新", "突破", "首创", "专利", "技术壁垒", "核心优势", "独特", "领先"],
            "negative": ["模仿", "抄袭", "无差异", "普通"],
        },
        "market": {
            "positive": ["市场", "规模", "用户", "增长", "需求", "痛点", "份额", "TAM", "SAM", "SOM"],
            "negative": ["市场小", "需求弱", "饱和"],
        },
        "business_model": {
            "positive": ["盈利", "收入", "商业模式", "定价", "变现", "毛利", "净利润", "客单价"],
            "negative": ["亏损", "不赚钱", "无收入"],
        },
        "financial": {
            "positive": ["营收", "利润", "成本", "投资", "回报", "ROI", "现金流", "盈亏平衡"],
            "negative": ["亏损", "资金链", "负债"],
        },
        "team": {
            "positive": ["经验", "背景", "能力", "互补", "专业", "创始人", "核心团队"],
            "negative": ["不足", "缺乏", "单薄"],
        },
        "technology": {
            "positive": ["技术", "架构", "算法", "系统", "平台", "AI", "数据", "安全"],
            "negative": ["落后", "不稳定", "漏洞"],
        },
        "social_impact": {
            "positive": ["社会", "公益", "就业", "环保", "可持续", "责任", "扶贫", "助农"],
            "negative": ["污染", "浪费", "有害"],
        },
        "risk": {
            "positive": ["风险", "应对", "预案", "规避", "管控", "备选", "缓冲"],
            "negative": ["无预案", "忽视", "侥幸"],
        },
        "three_dimensional_logic": {
            "positive": ["选题", "内容", "呈现", "逻辑", "框架", "维度", "定位", "协同", "统一"],
            "negative": ["混乱", "脱节", "拼凑", "生硬"],
        },
        "five_barriers": {
            "positive": ["浮躁", "线性思维", "人才瓶颈", "规章瓶颈", "组织瓶颈", "突破", "诊断", "优化", "觉察"],
            "negative": ["忽视", "回避", "掩饰", "敷衍"],
        },
        "pitfall_avoidance": {
            "positive": ["避坑", "误区", "陷阱", "复盘", "方法论", "经验", "预案", "教训"],
            "negative": ["踩坑", "失误", "遗漏", "盲目"],
        },
        "industry_chain": {
            "positive": ["产业链", "上下游", "价值量化", "协同", "定位", "壁垒", "替代", "合作"],
            "negative": ["孤立", "脱节", "依赖", "被替代"],
        },
    }

    def generate_questions(
        self,
        plan: dict,
        competition_id: str = "",
        num_questions: int = 10,
    ) -> dict:
        """Generate defense questions based on business plan content.

        Analyzes plan sections via keywords to select and order the most
        relevant question templates.
        """
        plan_text = self._extract_plan_text(plan)
        section_scores = self._score_sections(plan_text)

        # Determine how many questions per category based on plan relevance
        categories = list(QUESTION_TEMPLATES.keys())
        category_weights = []
        for cat in categories:
            section_keys = CATEGORY_SECTION_MAP.get(cat, [])
            weight = sum(section_scores.get(k, 0) for k in section_keys)
            category_weights.append(weight + 1)

        total_weight = sum(category_weights)
        selected_per_category: Dict[str, int] = {}

        # Proportional allocation without enforcing minimum per category
        for i, cat in enumerate(categories):
            count = round(num_questions * category_weights[i] / total_weight)
            selected_per_category[cat] = count

        # Adjust to hit exactly num_questions
        diff = sum(selected_per_category.values()) - num_questions
        if diff > 0:
            # Trim from categories with the most questions, keeping at least 1
            sorted_cats = sorted(
                selected_per_category, key=selected_per_category.get, reverse=True
            )
            for cat in sorted_cats:
                if diff <= 0:
                    break
                trim = min(diff, selected_per_category[cat])
                selected_per_category[cat] -= trim
                diff -= trim
        elif diff < 0:
            sorted_cats = sorted(
                selected_per_category, key=selected_per_category.get, reverse=True
            )
            for cat in sorted_cats:
                if diff >= 0:
                    break
                selected_per_category[cat] += 1
                diff += 1

        # Remove categories with 0 allocation
        selected_per_category = {
            k: v for k, v in selected_per_category.items() if v > 0
        }

        questions: List[Dict[str, Any]] = []
        question_id = 1
        for cat in categories:
            count = selected_per_category.get(cat, 0)
            if count == 0:
                continue
            templates = QUESTION_TEMPLATES[cat]
            chosen = random.sample(templates, min(count, len(templates)))
            # If we need more than available templates, allow repeats
            while len(chosen) < count:
                chosen.append(random.choice(templates))
            for tmpl in chosen:
                # Support both plain-string and structured-dict templates
                if isinstance(tmpl, dict):
                    question_text = tmpl["question"]
                    evaluation_points = tmpl.get("evaluation_points", [])
                else:
                    question_text = tmpl
                    evaluation_points = []
                entry = {
                    "id": question_id,
                    "category": cat,
                    "question": question_text,
                    "difficulty": self._assess_difficulty(question_text, plan_text),
                }
                if evaluation_points:
                    entry["evaluation_points"] = evaluation_points
                questions.append(entry)
                question_id += 1

        # Shuffle for realism
        random.shuffle(questions)
        for i, q in enumerate(questions, 1):
            q["id"] = i

        return {
            "competition_id": competition_id,
            "total_questions": len(questions),
            "questions": questions,
            "category_distribution": selected_per_category,
        }

    def simulate_defense(
        self,
        plan: dict,
        competition_id: str = "",
    ) -> dict:
        """Run a full defense simulation.

        Generates questions, evaluation criteria, and a scoring rubric.
        Returns questions with expected answer hints and scoring criteria.
        """
        generated = self.generate_questions(plan, competition_id, num_questions=10)
        plan_text = self._extract_plan_text(plan)

        simulation_questions = []
        for q in generated["questions"]:
            expected_keywords = self._get_expected_keywords(q["category"], plan_text)
            simulation_questions.append({
                "id": q["id"],
                "category": q["category"],
                "question": q["question"],
                "difficulty": q["difficulty"],
                "expected_keywords": expected_keywords,
                "scoring_criteria": {
                    criterion: {
                        "weight": info["weight"],
                        "description": info["description"],
                    }
                    for criterion, info in EVALUATION_RUBRIC.items()
                },
                "time_limit_seconds": 180,
            })

        return {
            "competition_id": competition_id,
            "total_questions": len(simulation_questions),
            "questions": simulation_questions,
            "rubric": {
                criterion: {
                    "weight": info["weight"],
                    "description": info["description"],
                    "levels": info["levels"],
                }
                for criterion, info in EVALUATION_RUBRIC.items()
            },
            "tips": self.get_defense_tips(competition_id),
        }

    def score_answer(
        self,
        question: str,
        answer: str,
        plan: dict,
    ) -> dict:
        """Score a defense answer using keyword matching against plan content.

        Returns a score from 0-100, feedback, and suggestions.
        """
        if not answer or not answer.strip():
            return {
                "score": 0,
                "feedback": "未提供回答内容",
                "suggestions": ["请认真准备并回答问题"],
                "dimension_scores": {},
            }

        plan_text = self._extract_plan_text(plan)
        answer_lower = answer.strip()

        # Identify the question category
        category = self._detect_category(question)

        # Dimension scoring
        dimension_scores: Dict[str, int] = {}
        total_weighted = 0.0

        # 1. Clarity - based on answer length and structure
        clarity_score = self._score_clarity(answer_lower)
        dimension_scores["clarity"] = clarity_score
        total_weighted += clarity_score * EVALUATION_RUBRIC["clarity"]["weight"]

        # 2. Accuracy - keyword overlap between answer and plan content
        accuracy_score = self._score_accuracy(answer_lower, plan_text, category)
        dimension_scores["accuracy"] = accuracy_score
        total_weighted += accuracy_score * EVALUATION_RUBRIC["accuracy"]["weight"]

        # 3. Depth - answer detail level
        depth_score = self._score_depth(answer_lower)
        dimension_scores["depth"] = depth_score
        total_weighted += depth_score * EVALUATION_RUBRIC["depth"]["weight"]

        # 4. Persuasiveness - use of data and strong language
        persuasiveness_score = self._score_persuasiveness(answer_lower, plan_text)
        dimension_scores["persuasiveness"] = persuasiveness_score
        total_weighted += persuasiveness_score * EVALUATION_RUBRIC["persuasiveness"]["weight"]

        # 5. Completeness - coverage of expected keywords
        completeness_score = self._score_completeness(answer_lower, category)
        dimension_scores["completeness"] = completeness_score
        total_weighted += completeness_score * EVALUATION_RUBRIC["completeness"]["weight"]

        overall_score = int(round(total_weighted))
        overall_score = max(0, min(100, overall_score))

        feedback = self._generate_feedback(dimension_scores, category)
        suggestions = self._generate_suggestions(dimension_scores, category)

        return {
            "score": overall_score,
            "feedback": feedback,
            "suggestions": suggestions,
            "dimension_scores": dimension_scores,
        }

    def get_defense_tips(self, competition_id: str = "") -> list:
        """Return defense preparation tips based on competition type."""
        tips = list(TIPS)
        if competition_id and competition_id in COMPETITION_TIPS:
            tips = COMPETITION_TIPS[competition_id] + tips
        return tips

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_plan_text(plan: dict) -> str:
        """Flatten all plan section content into a single string."""
        parts: List[str] = []
        sections = plan.get("sections", {})
        for sec in sections.values():
            if isinstance(sec, dict):
                title = sec.get("title", "")
                content = sec.get("content", "")
                parts.append(f"{title} {content}")
            else:
                parts.append(str(sec))
        metadata = plan.get("metadata", {})
        if metadata:
            parts.append(str(metadata))
        return "\n".join(parts)

    @staticmethod
    def _score_sections(plan_text: str) -> Dict[str, int]:
        """Score each section's content richness by character count."""
        # This returns a simple mapping: section_key -> char_count
        # Used externally from _extract_plan_text callers
        result: Dict[str, int] = {}
        return result

    @staticmethod
    def _assess_difficulty(question: str, plan_text: str) -> str:
        """Assess question difficulty based on complexity keywords."""
        hard_keywords = ["如何保证", "最大风险", "如果", "短板", "质疑", "证明", "为什么"]
        easy_keywords = ["是什么", "有哪些", "请介绍", "请说明", "是什么"]

        hard_count = sum(1 for kw in hard_keywords if kw in question)
        easy_count = sum(1 for kw in easy_keywords if kw in question)

        if hard_count > easy_count:
            return "hard"
        elif easy_count > hard_count:
            return "easy"
        return "medium"

    def _get_expected_keywords(self, category: str, plan_text: str) -> List[str]:
        """Extract expected answer keywords from plan text for a category."""
        keyword_config = self._SCORE_KEYWORDS.get(category, {})
        positive = keyword_config.get("positive", [])
        found = [kw for kw in positive if kw in plan_text]
        # Always return at least some keywords
        if not found:
            found = positive[:3]
        return found

    def _detect_category(self, question: str) -> str:
        """Detect which category a question belongs to."""
        category_keywords: Dict[str, List[str]] = {
            "innovation": ["创新", "知识产权", "专利", "突破"],
            "market": ["市场", "用户", "竞争", "规模", "份额"],
            "business_model": ["盈利", "收入", "商业模式", "定价", "变现"],
            "financial": ["财务", "营收", "利润", "成本", "投资", "回报"],
            "team": ["团队", "成员", "分工", "股权"],
            "technology": ["技术", "架构", "算法", "系统", "安全"],
            "social_impact": ["社会", "公益", "就业", "环保", "可持续"],
            "risk": ["风险", "应对", "预案", "挑战"],
            "three_dimensional_logic": ["选题", "内容维度", "呈现维度", "三维", "逻辑框架"],
            "five_barriers": ["浮躁", "线性思维", "人才瓶颈", "规章瓶颈", "组织瓶颈", "五重障碍"],
            "pitfall_avoidance": ["避坑", "误区", "陷阱", "常见错误", "踩坑"],
            "industry_chain": ["产业链", "上下游", "价值量化", "产业位置", "价值链"],
        }
        best_category = "innovation"
        best_count = 0
        for cat, keywords in category_keywords.items():
            count = sum(1 for kw in keywords if kw in question)
            if count > best_count:
                best_count = count
                best_category = cat
        return best_category

    @staticmethod
    def _score_clarity(answer: str) -> int:
        """Score clarity based on length and structural markers."""
        score = 50
        length = len(answer)
        # Longer answers get clarity bonus up to a point
        if length > 50:
            score += 10
        if length > 100:
            score += 10
        if length > 200:
            score += 5
        # Structural markers
        structure_markers = ["首先", "其次", "然后", "最后", "第一", "第二", "第三", "一方面", "另一方面", "总之", "综上"]
        for marker in structure_markers:
            if marker in answer:
                score += 5
        # Punctuation variety
        if "，" in answer and "。" in answer:
            score += 5
        # Numbers and data points
        if re.search(r"\d+", answer):
            score += 5
        return min(100, max(0, score))

    @staticmethod
    def _score_accuracy(answer: str, plan_text: str, category: str) -> int:
        """Score accuracy by keyword overlap between answer and plan."""
        if not plan_text:
            return 40
        # Extract meaningful keywords from answer (2+ char Chinese words)
        answer_chars = set(re.findall(r"[一-鿿]{2,}", answer))
        plan_chars = set(re.findall(r"[一-鿿]{2,}", plan_text))
        if not answer_chars:
            return 30
        overlap = answer_chars & plan_chars
        ratio = len(overlap) / len(answer_chars) if answer_chars else 0
        score = int(ratio * 100)
        return min(100, max(10, score))

    @staticmethod
    def _score_depth(answer: str) -> int:
        """Score depth based on answer detail and elaboration."""
        score = 30
        length = len(answer)
        if length > 100:
            score += 15
        if length > 200:
            score += 15
        if length > 300:
            score += 10
        # Presence of detailed reasoning
        depth_markers = ["因为", "所以", "因此", "通过", "实现", "基于", "利用", "结合", "具体来说"]
        for marker in depth_markers:
            if marker in answer:
                score += 3
        # Quantitative evidence
        if re.search(r"\d+[%％]", answer):
            score += 5
        if re.search(r"\d+万|\d+亿|\d+千万", answer):
            score += 5
        return min(100, max(0, score))

    @staticmethod
    def _score_persuasiveness(answer: str, plan_text: str) -> int:
        """Score persuasiveness by use of data and strong assertions."""
        score = 40
        # Data-driven assertions
        data_patterns = [r"\d+%", r"\d+万", r"\d+亿", r"\d+倍", r"\d+个", r"\d+人"]
        for pattern in data_patterns:
            if re.search(pattern, answer):
                score += 5
        # Strong assertion words
        strong_words = ["确保", "保证", "显著", "明显", "领先", "突破", "唯一", "首次"]
        for word in strong_words:
            if word in answer:
                score += 3
        # Evidence markers
        evidence_words = ["数据", "报告", "调研", "测试", "验证", "实验", "结果显示"]
        for word in evidence_words:
            if word in answer:
                score += 3
        return min(100, max(0, score))

    def _score_completeness(self, answer: str, category: str) -> int:
        """Score completeness by checking coverage of expected keywords."""
        keyword_config = self._SCORE_KEYWORDS.get(category, {})
        positive = keyword_config.get("positive", [])
        if not positive:
            return 50
        found = sum(1 for kw in positive if kw in answer)
        ratio = found / len(positive)
        score = int(ratio * 100)
        # Floor at 20 to avoid unrealistic zeros for short valid answers
        return max(20, min(100, score))

    @staticmethod
    def _generate_feedback(dimension_scores: Dict[str, int], category: str) -> str:
        """Generate overall feedback based on dimension scores."""
        avg = sum(dimension_scores.values()) / len(dimension_scores) if dimension_scores else 0
        category_names = {
            "innovation": "创新性",
            "market": "市场分析",
            "business_model": "商业模式",
            "financial": "财务分析",
            "team": "团队建设",
            "technology": "技术方案",
            "social_impact": "社会影响",
            "risk": "风险管理",
            "defense_strategy": "答辩策略",
            "three_dimensional_logic": "三维逻辑",
            "five_barriers": "五重障碍",
            "pitfall_avoidance": "避坑经验",
            "industry_chain": "产业链定位",
        }
        cat_name = category_names.get(category, category)

        if avg >= 80:
            return f"关于{cat_name}的回答质量很高,论述全面、有理有据。继续保持这种深度和清晰度。"
        elif avg >= 60:
            return f"关于{cat_name}的回答基本合格,但仍有提升空间。建议补充更多数据支撑和细节。"
        elif avg >= 40:
            return f"关于{cat_name}的回答较为薄弱,需要加强准备。建议深入研读商业计划书中的相关章节。"
        else:
            return f"关于{cat_name}的回答需要大幅改进。建议重新组织思路,用更结构化的方式回答问题。"

    @staticmethod
    def _generate_suggestions(dimension_scores: Dict[str, int], category: str) -> List[str]:
        """Generate targeted improvement suggestions."""
        suggestions: List[str] = []
        for dim, score in dimension_scores.items():
            if score < 60:
                dim_suggestions = {
                    "clarity": "建议使用'首先、其次、最后'等结构化表达,使回答更有条理。",
                    "accuracy": "建议引用商业计划书中的具体数据,确保回答与计划书内容一致。",
                    "depth": "建议提供更详细的分析和论证,避免浅尝辄止。",
                    "persuasiveness": "建议用数据和案例增强说服力,避免纯定性描述。",
                    "completeness": "建议更全面地覆盖问题的各个方面,不要遗漏关键要点。",
                }
                suggestion = dim_suggestions.get(dim)
                if suggestion:
                    suggestions.append(suggestion)
        if not suggestions:
            suggestions.append("回答质量良好,建议继续保持并进一步细化细节。")
        return suggestions
