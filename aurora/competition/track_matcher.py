"""Track matching engine for AuroraAgent."""

from typing import Dict, List

from aurora.competition.database import CompetitionDatabase, CompetitionInfo, TrackInfo


class TrackMatcher:
    """Match projects to competition tracks."""

    def __init__(self):
        self._db = CompetitionDatabase()

    def match(
        self,
        project_info: Dict[str, str],
        competition_id: str = None
    ) -> List[Dict]:
        """
        Match project to tracks.

        Args:
            project_info: Dictionary containing project details:
                - technology: 技术领域
                - business_model: 商业模式
                - target_market: 目标市场
                - social_impact: 社会影响描述
                - team_background: 团队背景
                - project_stage: 项目阶段
            competition_id: Optional competition ID to filter by

        Returns:
            List of matching tracks with confidence scores
        """
        if competition_id:
            competitions = [self._db.get_competition(competition_id)]
        else:
            competitions = self._db.list_competitions()

        results = []
        for comp in competitions:
            if not comp:
                continue

            for track in comp.tracks:
                score = self._calculate_match_score(project_info, track, comp)
                if score >= 0.15:
                    results.append({
                        "competition_id": comp.id,
                        "competition_name": comp.name,
                        "track_name": track.name,
                        "track_description": track.description,
                        "confidence": round(score, 2),
                        "reasons": self._get_match_reasons(project_info, track, comp),
                    })

        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results[:5]

    def _calculate_match_score(
        self,
        project_info: Dict[str, str],
        track: TrackInfo,
        competition: CompetitionInfo
    ) -> float:
        """Calculate matching score for a track."""
        score = 0.0
        factors = []

        tech = project_info.get("technology", "").lower()
        business = project_info.get("business_model", "").lower()
        market = project_info.get("target_market", "").lower()
        social = project_info.get("social_impact", "").lower()
        stage = project_info.get("project_stage", "").lower()

        track_desc = track.description.lower()

        if "乡村" in track_desc or "农业" in track_desc or "三农" in track_desc:
            if any(kw in market for kw in ["乡村", "农村", "农业", "农民"]):
                factors.append(0.3)
            if "乡村振兴" in social or "扶贫" in social:
                factors.append(0.2)

        elif "职教" in track_desc:
            if "职业" in project_info.get("team_background", "").lower():
                factors.append(0.3)
            if "技能" in tech:
                factors.append(0.2)

        elif "产业" in track_desc or "企业" in track_desc:
            if "企业" in business or "合作" in business:
                factors.append(0.3)
            if "技术服务" in tech or "解决方案" in tech:
                factors.append(0.2)

        elif "创意" in track_desc or "文化" in track_desc:
            if "文化" in tech or "创意" in tech or "IP" in tech:
                factors.append(0.3)
            if "内容" in business or "媒体" in business:
                factors.append(0.2)

        elif "环保" in track_desc or "生态" in track_desc or "绿色" in track_desc:
            if any(kw in tech for kw in ["环保", "绿色", "节能", "碳中和"]):
                factors.append(0.3)
            if "可持续" in social:
                factors.append(0.2)

        elif "公益" in track_desc:
            if any(kw in social for kw in ["公益", "慈善", "志愿", "社会福利"]):
                factors.append(0.3)
            if "社会" in social or "公共" in social:
                factors.append(0.2)

        elif "红色" in track_desc or "革命" in track_desc:
            if any(kw in social for kw in ["红色", "革命", "党建", "传承"]):
                factors.append(0.3)
            if "教育" in market or "文化" in tech:
                factors.append(0.2)

        elif "社区" in track_desc or "治理" in track_desc:
            if any(kw in market for kw in ["社区", "基层", "治理", "公共管理"]):
                factors.append(0.3)
            if any(kw in social for kw in ["社区", "民生", "治理"]):
                factors.append(0.2)

        elif "创客" in track_desc or "创意" in track_desc:
            if any(kw in tech for kw in ["创客", "创意", "DIY", "开源"]):
                factors.append(0.3)
            if "初创" in stage or "创意" in stage:
                factors.append(0.2)

        elif "劳务" in track_desc or "品牌" in track_desc:
            if any(kw in market for kw in ["劳务", "人力资源", "就业", "培训"]):
                factors.append(0.3)
            if "就业" in social or "品牌" in business:
                factors.append(0.2)

        elif "科技" in track_desc or "创新" in track_desc:
            if any(kw in tech for kw in ["ai", "人工智能", "大数据", "物联网", "区块链"]):
                factors.append(0.3)
            if "技术" in tech:
                factors.append(0.2)

        else:
            if "初创" in stage or "创意" in stage:
                factors.append(0.2)
            if "成长" in stage:
                factors.append(0.1)

        if factors:
            score = min(sum(factors), 1.0)
        else:
            score = 0.2

        # Boost score by track weight for ranking purposes
        score = min(score * (0.5 + track.weight), 1.0)

        return score

    def _get_match_reasons(
        self,
        project_info: Dict[str, str],
        track: TrackInfo,
        competition: CompetitionInfo
    ) -> List[str]:
        """Get reasons for matching."""
        reasons = []
        track_desc = track.description.lower()

        if "乡村" in track_desc:
            if any(kw in project_info.get("target_market", "").lower() for kw in ["乡村", "农村"]):
                reasons.append("项目目标市场与乡村赛道匹配")
            if "乡村振兴" in project_info.get("social_impact", ""):
                reasons.append("项目具有乡村振兴社会价值")

        elif "科技" in track_desc:
            if any(kw in project_info.get("technology", "").lower() for kw in ["AI", "人工智能", "大数据"]):
                reasons.append("项目技术创新性强")

        elif "文化" in track_desc:
            if "文化" in project_info.get("technology", ""):
                reasons.append("项目具有文化创意属性")

        elif "公益" in track_desc:
            if any(kw in project_info.get("social_impact", "") for kw in ["公益", "慈善"]):
                reasons.append("项目具有公益属性")

        elif "红色" in track_desc or "革命" in track_desc:
            if any(kw in project_info.get("social_impact", "") for kw in ["红色", "革命", "传承"]):
                reasons.append("项目具有红色文化属性")

        elif "社区" in track_desc or "治理" in track_desc:
            if any(kw in project_info.get("target_market", "") for kw in ["社区", "治理"]):
                reasons.append("项目聚焦社区治理领域")

        elif "创客" in track_desc:
            if any(kw in project_info.get("technology", "") for kw in ["创客", "创意"]):
                reasons.append("项目具有创客创意属性")

        elif "劳务" in track_desc:
            if any(kw in project_info.get("target_market", "") for kw in ["劳务", "就业"]):
                reasons.append("项目与劳务品牌领域相关")

        reasons.append(f"该赛道权重: {track.weight * 100:.0f}%")
        return reasons
