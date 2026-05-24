"""Competitor analysis engine for AuroraAgent.

Provides SWOT analysis, competitor comparison, competitive strategy generation,
and market position analysis using keyword matching and template-based reasoning.
No LLM calls required.
"""

from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Keyword dictionaries for SWOT analysis
# ---------------------------------------------------------------------------

_STRENGTH_KEYWORDS: Dict[str, List[str]] = {
    "technology": [
        "ai", "人工智能", "大模型", "机器学习", "深度学习", "大数据",
        "区块链", "物联网", "云计算", "5g", "自动驾驶", "ar", "vr",
        "自然语言处理", "计算机视觉", "芯片", "量子",
    ],
    "innovation": [
        "创新", "首创", "独创", "自主", "专利", "突破", "颠覆",
        "核心技术", "自主研发", "独家",
    ],
    "team": [
        "博士", "硕士", "海归", "名校", "专家", "资深", "多年经验",
        "industry", "专业", "技术背景", "计算机专业", "top",
    ],
    "business_model": [
        "saas", "订阅", "平台", "生态", "规模化", "可复制",
        "高毛利", "recurring", "freemium",
    ],
    "market": [
        "蓝海", "增长", "刚需", "痛点", "空白", "潜力", "爆发",
        "万亿", "千亿", "高增长",
    ],
}

_WEAKNESS_KEYWORDS: Dict[str, List[str]] = {
    "stage": [
        "初创", "早期", "概念", "demo", "mvp", "种子", "天使",
        "pre-seed", "idea",
    ],
    "resource": [
        "资金不足", "人手不足", "有限", "紧缺", "缺乏",
        "不足", "薄弱",
    ],
    "market": [
        "红海", "竞争激烈", "巨头", "垄断", "壁垒",
        "饱和", "同质化",
    ],
    "team": [
        "缺乏经验", "年轻", "学生", "兼职", "临时",
    ],
}

_OPPORTUNITY_KEYWORDS: Dict[str, List[str]] = {
    "policy": [
        "政策", "扶持", "补贴", "鼓励", "国家", "战略", "规划",
        "十四五", "双减", "数字", "智能", "新基建",
    ],
    "social": [
        "教育公平", "乡村振兴", "碳中和", "环保", "老龄化", "健康",
        "就业", "扶贫", "社会价值", "民生", "可持续",
    ],
    "technology": [
        "大模型", "生成式", "aigc", "数字化转型", "智能化",
        "自动化", "数据驱动",
    ],
    "market": [
        "下沉市场", "出海", "跨境", "海外", "新兴", "蓝海",
        "垂直", "细分",
    ],
}

_THREAT_KEYWORDS: Dict[str, List[str]] = {
    "competition": [
        "巨头", "bat", "字节", "腾讯", "阿里", "美团", "百度",
        "竞争", "模仿", "抄袭", "跟随",
    ],
    "market": [
        "萎缩", "下行", "不确定性", "波动", "风险",
        "经济", "衰退", "周期",
    ],
    "regulation": [
        "监管", "合规", "资质", "许可", "审查", "限制",
        "数据安全", "隐私", "个人信息保护",
    ],
    "technology": [
        "替代", "淘汰", "迭代", "过时", "技术风险",
    ],
}


class CompetitorAnalyzer:
    """Analyze competitors and generate strategic insights.

    All analysis is keyword-based and template-driven. No LLM calls.
    """

    # ------------------------------------------------------------------
    # SWOT Analysis
    # ------------------------------------------------------------------

    def analyze_swot(self, project_info: dict) -> dict:
        """Generate SWOT analysis from project info.

        Args:
            project_info: Dict with keys like technology, business_model,
                target_market, team_background, project_stage, innovation,
                social_impact, etc.

        Returns:
            Dict with keys: strengths, weaknesses, opportunities, threats
            (each a list of strings), and overall_assessment (string).
        """
        combined_text = self._combine_project_text(project_info)

        strengths = self._match_keywords(combined_text, _STRENGTH_KEYWORDS, project_info)
        weaknesses = self._match_keywords(combined_text, _WEAKNESS_KEYWORDS, project_info)
        opportunities = self._match_keywords(combined_text, _OPPORTUNITY_KEYWORDS, project_info)
        threats = self._match_keywords(combined_text, _THREAT_KEYWORDS, project_info)

        # Ensure at least one entry per quadrant
        if not strengths:
            strengths = ["项目具有基本的竞争力"]
        if not weaknesses:
            weaknesses = ["需进一步评估潜在短板"]
        if not opportunities:
            opportunities = ["市场环境存在发展空间"]
        if not threats:
            threats = ["需关注市场动态变化"]

        assessment = self._generate_swot_assessment(
            strengths, weaknesses, opportunities, threats, project_info
        )

        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "opportunities": opportunities,
            "threats": threats,
            "overall_assessment": assessment,
        }

    # ------------------------------------------------------------------
    # Competitor Comparison
    # ------------------------------------------------------------------

    def compare_competitors(self, our_project: dict, competitors: list) -> dict:
        """Compare our project against a list of competitors.

        Args:
            our_project: Dict describing our project (same shape as project_info).
            competitors: List of dicts, each with keys: name, strengths,
                weaknesses, market_share.

        Returns:
            Dict with comparison_matrix (list of dicts) and
            competitive_advantage analysis (string).
        """
        if not competitors:
            return {
                "comparison_matrix": [],
                "competitive_advantage": "无竞争对手数据，无法进行比较分析",
            }

        our_swot = self.analyze_swot(our_project)
        our_score = self._calculate_competitive_score(our_swot, our_project)

        matrix = []
        matrix.append({
            "name": "我方项目",
            "strength_count": len(our_swot["strengths"]),
            "weakness_count": len(our_swot["weaknesses"]),
            "opportunity_count": len(our_swot["opportunities"]),
            "threat_count": len(our_swot["threats"]),
            "competitive_score": round(our_score, 2),
            "market_share": "待定",
        })

        for comp in competitors:
            comp_swot = self._analyze_competitor(comp)
            comp_score = self._calculate_competitive_score(comp_swot, comp)

            market_share = comp.get("market_share", "未知")
            if isinstance(market_share, (int, float)):
                market_share = f"{market_share}%"

            matrix.append({
                "name": comp.get("name", "未知对手"),
                "strength_count": len(comp_swot["strengths"]),
                "weakness_count": len(comp_swot["weaknesses"]),
                "opportunity_count": len(comp_swot["opportunities"]),
                "threat_count": len(comp_swot["threats"]),
                "competitive_score": round(comp_score, 2),
                "market_share": market_share,
            })

        advantage = self._build_advantage_analysis(our_project, our_swot, competitors, matrix)

        return {
            "comparison_matrix": matrix,
            "competitive_advantage": advantage,
        }

    # ------------------------------------------------------------------
    # Competitive Strategy
    # ------------------------------------------------------------------

    def generate_competitive_strategy(
        self, project_info: dict, competitors: list
    ) -> dict:
        """Generate competitive strategy recommendations.

        Args:
            project_info: Project description dict.
            competitors: List of competitor dicts.

        Returns:
            Dict with strategies (list of dicts, each with name, priority,
            description).
        """
        swot = self.analyze_swot(project_info)
        strategies = []

        # Technology-driven strategies
        tech = project_info.get("technology", "").lower()
        innovation = project_info.get("innovation", "").lower()

        if any(kw in tech for kw in ["ai", "人工智能", "大模型", "机器学习"]):
            strategies.append({
                "name": "技术壁垒构建",
                "priority": "高",
                "description": (
                    "基于AI技术优势，持续投入核心算法研发，建立技术护城河。"
                    "通过专利申请、论文发表和开源社区建设巩固技术领先地位。"
                ),
            })

        if any(kw in innovation for kw in ["创新", "首创", "独创", "自主研发"]):
            strategies.append({
                "name": "先发优势扩大",
                "priority": "高",
                "description": (
                    "利用先发创新优势，快速占领市场心智。"
                    "通过持续迭代和用户反馈闭环，保持产品差异化竞争力。"
                ),
            })

        # Market-driven strategies
        market = project_info.get("target_market", "").lower()
        social = project_info.get("social_impact", "").lower()

        if any(kw in market for kw in ["教育", "医疗", "农业", "环保"]):
            strategies.append({
                "name": "垂直领域深耕",
                "priority": "高",
                "description": (
                    f"聚焦{project_info.get('target_market', '目标')}垂直领域，"
                    "深入理解行业痛点和用户需求，打造领域专家形象，"
                    "形成难以复制的行业know-how壁垒。"
                ),
            })

        if any(kw in social for kw in ["公平", "乡村振兴", "碳中和", "可持续", "扶贫"]):
            strategies.append({
                "name": "社会价值驱动",
                "priority": "中",
                "description": (
                    "强化社会价值叙事，获取政策支持和公众认可。"
                    "积极对接政府项目和公益资源，建立品牌社会责任形象。"
                ),
            })

        # Business model strategies
        biz = project_info.get("business_model", "").lower()
        if any(kw in biz for kw in ["saas", "订阅", "平台", "生态"]):
            strategies.append({
                "name": "平台生态构建",
                "priority": "中",
                "description": (
                    "构建平台化商业模式，通过网络效应形成竞争壁垒。"
                    "吸引第三方开发者或合作伙伴加入，打造产业生态闭环。"
                ),
            })

        # Stage-based strategies
        stage = project_info.get("project_stage", "").lower()
        if any(kw in stage for kw in ["初创", "早期", "种子"]):
            strategies.append({
                "name": "快速验证与迭代",
                "priority": "高",
                "description": (
                    "采用精益创业方法论，快速构建MVP并投入市场验证。"
                    "通过用户反馈快速迭代，降低试错成本，找到产品市场契合点。"
                ),
            })

        # Competition-driven strategies
        if competitors and len(competitors) > 0:
            strong_competitors = [
                c for c in competitors
                if isinstance(c.get("market_share"), (int, float)) and c["market_share"] > 20
            ]
            if strong_competitors:
                strategies.append({
                    "name": "差异化竞争",
                    "priority": "高",
                    "description": (
                        "面对市场强势竞争对手，采取差异化定位策略。"
                        "避开正面竞争，聚焦细分市场或特定用户群体，"
                        "通过独特价值主张获取市场份额。"
                    ),
                })

        # Weakness-mitigation strategies
        if swot["weaknesses"]:
            strategies.append({
                "name": "短板补强",
                "priority": "中",
                "description": (
                    "针对识别到的薄弱环节制定专项改善计划。"
                    "通过外部合作、人才引进或技术采购等方式弥补关键短板。"
                ),
            })

        # Generic fallback if no specific strategies matched
        if not strategies:
            strategies.append({
                "name": "核心竞争力打造",
                "priority": "高",
                "description": (
                    "明确项目核心竞争力定位，集中资源打造差异化优势。"
                    "通过持续创新和用户体验优化建立市场认知。"
                ),
            })

        # Sort by priority
        priority_order = {"高": 0, "中": 1, "低": 2}
        strategies.sort(key=lambda s: priority_order.get(s["priority"], 3))

        return {
            "strategies": strategies,
            "total_count": len(strategies),
        }

    # ------------------------------------------------------------------
    # Market Position Analysis
    # ------------------------------------------------------------------

    def analyze_market_position(
        self, project_info: dict, market_data: dict = None
    ) -> dict:
        """Analyze market position based on project info and optional market data.

        Args:
            project_info: Project description dict.
            market_data: Optional dict with keys like market_size,
                growth_rate, competitor_count, etc.

        Returns:
            Dict with position (leader/challenger/follower/niche),
            analysis (string), recommendations (list of strings).
        """
        market_data = market_data or {}

        position_score = self._calculate_position_score(project_info, market_data)

        position = self._determine_position(position_score)

        analysis = self._build_position_analysis(
            position, position_score, project_info, market_data
        )

        recommendations = self._build_position_recommendations(
            position, project_info, market_data
        )

        return {
            "position": position,
            "score": round(position_score, 2),
            "analysis": analysis,
            "recommendations": recommendations,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _combine_project_text(project_info: dict) -> str:
        """Combine all project_info values into a single lowercase string."""
        parts = []
        for v in project_info.values():
            if isinstance(v, str):
                parts.append(v.lower())
            elif isinstance(v, list):
                parts.extend(str(item).lower() for item in v)
            elif isinstance(v, dict):
                parts.extend(str(item).lower() for item in v.values())
            else:
                parts.append(str(v).lower())
        return " ".join(parts)

    @staticmethod
    def _match_keywords(
        text: str,
        keyword_dict: Dict[str, List[str]],
        project_info: dict,
    ) -> List[str]:
        """Match keyword categories against text and generate insight strings."""
        results = []
        for category, keywords in keyword_dict.items():
            matched = [kw for kw in keywords if kw in text]
            if not matched:
                continue

            if category == "technology":
                tech = project_info.get("technology", "")
                results.append(f"技术优势: 在{tech or '核心技术'}领域具备竞争力")
            elif category == "innovation":
                inn = project_info.get("innovation", "")
                results.append(f"创新优势: {inn or '产品具有创新性'}")
            elif category == "team":
                team = project_info.get("team_background", "")
                results.append(f"团队优势: {team or '团队背景扎实'}")
            elif category == "business_model":
                biz = project_info.get("business_model", "")
                results.append(f"商业模式优势: {biz or '商业模式具有可扩展性'}")
            elif category == "market":
                mkt = project_info.get("target_market", "")
                if category in _STRENGTH_KEYWORDS:
                    results.append(f"市场机会: {mkt or '目标市场'}具有发展潜力")
                else:
                    results.append(f"市场挑战: {mkt or '目标市场'}面临一定竞争压力")
            elif category == "stage":
                stage = project_info.get("project_stage", "")
                results.append(f"阶段风险: 项目处于{stage or '早期'}阶段，资源和经验有限")
            elif category == "resource":
                results.append("资源风险: 项目资源较为有限，需要合理配置")
            elif category == "policy":
                results.append("政策红利: 符合国家政策方向，可争取政策支持")
            elif category == "social":
                social = project_info.get("social_impact", "")
                results.append(f"社会价值: {social or '项目具有积极社会影响'}")
            elif category == "competition":
                results.append("竞争威胁: 市场存在强势竞争对手，需要差异化定位")
            elif category == "regulation":
                results.append("合规风险: 需关注行业监管政策和数据合规要求")
            elif category == "threat_tech":
                results.append("技术迭代风险: 需关注技术更新换代的速度")

        return results

    @staticmethod
    def _generate_swot_assessment(
        strengths, weaknesses, opportunities, threats, project_info
    ) -> str:
        """Generate a brief overall assessment string."""
        s_count = len(strengths)
        w_count = len(weaknesses)
        o_count = len(opportunities)
        t_count = len(threats)

        tech = project_info.get("technology", "")
        market = project_info.get("target_market", "")

        parts = []
        if s_count >= 2 and o_count >= 2:
            parts.append(
                f"项目在{tech}+{market}方向具有良好的发展潜力，"
                "优势明显且机遇丰富。"
            )
        elif s_count >= w_count:
            parts.append(
                f"项目在{tech or '核心领域'}具备一定优势，"
                "但需注意短板的补强。"
            )
        else:
            parts.append(
                "项目当前面临较多挑战，需要集中资源突破关键瓶颈。"
            )

        if o_count > t_count:
            parts.append("整体机遇大于威胁，建议积极把握市场机会。")
        elif t_count > o_count:
            parts.append("外部威胁较多，建议采取稳健的防御性策略。")
        else:
            parts.append("机遇与威胁并存，建议审慎推进。")

        return "".join(parts)

    def _analyze_competitor(self, competitor: dict) -> dict:
        """Build a mini-SWOT for a single competitor dict."""
        strengths = competitor.get("strengths", [])
        weaknesses = competitor.get("weaknesses", [])

        if isinstance(strengths, str):
            strengths = [strengths]
        if isinstance(weaknesses, str):
            weaknesses = [weaknesses]

        # Generate opportunities and threats from name/market context
        name = competitor.get("name", "")
        opportunities = [f"{name}存在被超越的市场缝隙"]
        threats = [f"{name}在市场中具备一定竞争力"]

        if weaknesses:
            opportunities.append(f"{name}的薄弱环节为我方提供切入点")

        if strengths:
            threats.append(f"{name}在{strengths[0] if isinstance(strengths, list) else strengths}领域构成直接竞争")

        return {
            "strengths": strengths if strengths else ["待进一步分析"],
            "weaknesses": weaknesses if weaknesses else ["待进一步分析"],
            "opportunities": opportunities,
            "threats": threats,
        }

    @staticmethod
    def _calculate_competitive_score(swot: dict, info: dict) -> float:
        """Calculate a 0-100 competitive score from SWOT + project info."""
        s_score = len(swot.get("strengths", [])) * 15
        w_score = len(swot.get("weaknesses", [])) * 10
        o_score = len(swot.get("opportunities", [])) * 10
        t_score = len(swot.get("threats", [])) * 8

        base = 50 + s_score + o_score - w_score - t_score

        # Bonus for market share
        ms = info.get("market_share", 0)
        if isinstance(ms, (int, float)):
            base += ms * 0.3

        return max(0, min(100, base))

    @staticmethod
    def _build_advantage_analysis(
        our_project: dict,
        our_swot: dict,
        competitors: list,
        matrix: list,
    ) -> str:
        """Build a competitive advantage narrative string."""
        our_entry = matrix[0]
        our_score = our_entry["competitive_score"]

        comp_scores = [row["competitive_score"] for row in matrix[1:]]
        avg_comp_score = sum(comp_scores) / len(comp_scores) if comp_scores else 50

        tech = our_project.get("technology", "")
        innovation = our_project.get("innovation", "")

        parts = []

        if our_score > avg_comp_score + 10:
            parts.append(
                f"我方项目综合竞争力评分({our_score})高于竞争对手平均水平({avg_comp_score:.1f})，"
                "具备较强的竞争实力。"
            )
        elif our_score > avg_comp_score - 10:
            parts.append(
                f"我方项目综合竞争力评分({our_score})与竞争对手平均水平({avg_comp_score:.1f})接近，"
                "需要进一步打造差异化优势。"
            )
        else:
            parts.append(
                f"我方项目综合竞争力评分({our_score})低于竞争对手平均水平({avg_comp_score:.1f})，"
                "需要集中资源构建核心壁垒。"
            )

        if tech:
            parts.append(f"在{tech}技术方向上，")
        if innovation:
            parts.append(f"凭借{innovation}的创新点，")
        else:
            parts.append("通过持续优化和创新，")

        parts.append("可以在竞争中找到差异化定位和突破口。")

        return "".join(parts)

    @staticmethod
    def _calculate_position_score(project_info: dict, market_data: dict) -> float:
        """Calculate a 0-1 position score."""
        score = 0.5  # baseline

        tech = project_info.get("technology", "").lower()
        innovation = project_info.get("innovation", "").lower()
        stage = project_info.get("project_stage", "").lower()
        biz = project_info.get("business_model", "").lower()
        team = project_info.get("team_background", "").lower()
        social = project_info.get("social_impact", "").lower()

        # Technology boost
        if any(kw in tech for kw in ["ai", "人工智能", "大模型", "区块链", "大数据"]):
            score += 0.1

        # Innovation boost
        if any(kw in innovation for kw in ["创新", "首创", "独创", "自主研发", "核心"]):
            score += 0.1

        # Stage penalty
        if any(kw in stage for kw in ["初创", "早期", "种子", "概念"]):
            score -= 0.1
        elif any(kw in stage for kw in ["成长", "成熟", "扩张"]):
            score += 0.1

        # Business model bonus
        if any(kw in biz for kw in ["saas", "平台", "生态", "订阅"]):
            score += 0.05

        # Team bonus
        if any(kw in team for kw in ["博士", "名校", "资深", "专家", "专业"]):
            score += 0.05

        # Social impact bonus
        if any(kw in social for kw in ["公平", "振兴", "可持续", "扶贫"]):
            score += 0.05

        # Market data adjustments
        if market_data:
            market_share = market_data.get("our_market_share", 0)
            if isinstance(market_share, (int, float)):
                score += min(market_share / 100, 0.2)

            growth = market_data.get("growth_rate", 0)
            if isinstance(growth, (int, float)) and growth > 20:
                score += 0.05

            comp_count = market_data.get("competitor_count", 0)
            if isinstance(comp_count, int) and comp_count > 10:
                score -= 0.05
            elif isinstance(comp_count, int) and comp_count < 3:
                score += 0.05

        return max(0.0, min(1.0, score))

    @staticmethod
    def _determine_position(score: float) -> str:
        """Map score to position label."""
        if score >= 0.75:
            return "leader"
        elif score >= 0.55:
            return "challenger"
        elif score >= 0.35:
            return "follower"
        else:
            return "niche"

    @staticmethod
    def _build_position_analysis(
        position: str,
        score: float,
        project_info: dict,
        market_data: dict,
    ) -> str:
        """Build a narrative analysis for the market position."""
        tech = project_info.get("technology", "")
        market = project_info.get("target_market", "")
        stage = project_info.get("project_stage", "")

        position_labels = {
            "leader": "市场领导者",
            "challenger": "市场挑战者",
            "follower": "市场跟随者",
            "niche": "利基市场参与者",
        }

        label = position_labels.get(position, position)

        parts = [
            f"项目在{market or '目标市场'}中的定位为{label}（评分: {score:.2f}）。",
        ]

        if position == "leader":
            parts.append(
                "项目具备较强的技术和市场优势，处于行业领先地位。"
                "应持续投入研发保持领先，同时关注潜在颠覆者的威胁。"
            )
        elif position == "challenger":
            parts.append(
                f"项目在{tech or '核心技术'}方向具有竞争力，"
                "有能力挑战现有市场格局。"
                "建议集中资源在关键细分市场实现突破，逐步扩大市场份额。"
            )
        elif position == "follower":
            parts.append(
                f"项目处于{stage or '当前'}阶段，市场地位仍在建立中。"
                "建议通过差异化定位和快速迭代，逐步提升市场影响力。"
            )
        else:
            parts.append(
                "项目适合聚焦细分市场或特定用户群体，"
                "通过深度服务建立利基市场优势，"
                "避免与大型竞争对手正面交锋。"
            )

        return "".join(parts)

    @staticmethod
    def _build_position_recommendations(
        position: str,
        project_info: dict,
        market_data: dict,
    ) -> List[str]:
        """Build position-specific recommendations."""
        recs = []

        tech = project_info.get("technology", "")
        market = project_info.get("target_market", "")

        if position == "leader":
            recs.extend([
                "持续加大研发投入，保持技术领先",
                "构建生态体系，提高用户转换成本",
                "关注潜在颠覆性技术和商业模式",
                "积极进行行业标准和专利布局",
            ])
        elif position == "challenger":
            recs.extend([
                f"聚焦{market or '核心细分市场'}实现局部突破",
                "打造差异化产品功能和服务体验",
                "争取头部客户和标杆案例",
                "合理利用资本加速市场扩张",
            ])
        elif position == "follower":
            recs.extend([
                "学习行业领先者的成功经验",
                "寻找领先者未覆盖的细分需求",
                "通过快速迭代缩小产品差距",
                "建立核心用户群体，培养品牌忠诚度",
            ])
        else:  # niche
            recs.extend([
                "深耕细分市场，做到领域内最好",
                "建立专业的用户社群和口碑",
                "控制成本，保持精益运营",
                "寻找利基市场中的扩展机会",
            ])

        if tech:
            recs.append(f"充分利用{tech}技术优势建立竞争壁垒")

        return recs
