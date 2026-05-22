"""Competition database for AuroraAgent."""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import yaml


@dataclass
class TrackInfo:
    name: str
    description: str
    eligibility: str
    weight: float = 0.0


@dataclass
class TimelineEvent:
    phase: str
    start_date: str
    end_date: str


@dataclass
class EvaluationDimension:
    name: str
    weight: float
    description: str


@dataclass
class CompetitionInfo:
    id: str
    name: str
    full_name: str
    organizer: str
    level: str
    category: str
    tracks: List[TrackInfo]
    timeline: List[TimelineEvent]
    requirements: Dict[str, str]
    evaluation_dimensions: List[EvaluationDimension]
    official_website: str
    year: int = 2026


class CompetitionDatabase:
    """Database of competitions."""

    def __init__(self):
        self._competitions: Dict[str, CompetitionInfo] = {}
        self._load_default_data()

    def _load_default_data(self):
        """Load default competition data."""
        competitions = [
            CompetitionInfo(
                id="internet_plus",
                name="互联网+大赛",
                full_name="中国国际大学生创新大赛",
                organizer="教育部等12部委",
                level="国家级",
                category="A类",
                tracks=[
                    TrackInfo(
                        name="高教主赛道",
                        description="面向高等院校全日制在校学生的创新项目",
                        eligibility="全日制在校本科生、研究生",
                        weight=0.40
                    ),
                    TrackInfo(
                        name="青年红色筑梦之旅",
                        description="助力乡村振兴、社会服务的创新创业项目",
                        eligibility="全体在校学生",
                        weight=0.25
                    ),
                    TrackInfo(
                        name="职教赛道",
                        description="职业院校学生的创新技能项目",
                        eligibility="职业院校在校学生",
                        weight=0.15
                    ),
                    TrackInfo(
                        name="产业命题赛道",
                        description="企业命题的技术解决方案",
                        eligibility="全体在校学生",
                        weight=0.15
                    ),
                    TrackInfo(
                        name="萌芽赛道",
                        description="中学生创新项目",
                        eligibility="中学生",
                        weight=0.05
                    ),
                ],
                timeline=[
                    TimelineEvent(phase="校赛报名", start_date="2026-03-01", end_date="2026-03-31"),
                    TimelineEvent(phase="省赛", start_date="2026-04-01", end_date="2026-04-30"),
                    TimelineEvent(phase="国赛报名", start_date="2026-05-01", end_date="2026-05-31"),
                    TimelineEvent(phase="国赛", start_date="2026-09-01", end_date="2026-09-30"),
                ],
                requirements={
                    "team_size": "3-5人",
                    "leader_eligibility": "全日制在校学生",
                    "project_type": "科技创新、商业模式创新",
                },
                evaluation_dimensions=[
                    EvaluationDimension(name="创新性", weight=0.30, description="原创性、技术突破、模式创新"),
                    EvaluationDimension(name="团队情况", weight=0.25, description="团队背景、分工协作"),
                    EvaluationDimension(name="商业模式", weight=0.25, description="模式完整性、盈利能力"),
                    EvaluationDimension(name="带动就业", weight=0.10, description="就业规模、带动效率"),
                    EvaluationDimension(name="教育维度", weight=0.10, description="知识转化、创新精神"),
                ],
                official_website="https://cy.ncss.org.cn/",
            ),
            CompetitionInfo(
                id="challenge_cup",
                name="挑战杯",
                full_name="挑战杯中国大学生创业计划竞赛",
                organizer="共青团中央、教育部、科技部等",
                level="国家级",
                category="A类",
                tracks=[
                    TrackInfo(
                        name="科技创新和未来产业",
                        description="前沿技术创新项目",
                        eligibility="全体在校学生",
                        weight=0.25
                    ),
                    TrackInfo(
                        name="乡村振兴和农业农村现代化",
                        description="服务三农的创新项目",
                        eligibility="全体在校学生",
                        weight=0.25
                    ),
                    TrackInfo(
                        name="城市治理和社会服务",
                        description="智慧城市、民生服务项目",
                        eligibility="全体在校学生",
                        weight=0.20
                    ),
                    TrackInfo(
                        name="生态环保和可持续发展",
                        description="绿色经济、碳中和项目",
                        eligibility="全体在校学生",
                        weight=0.15
                    ),
                    TrackInfo(
                        name="文化创意和区域合作",
                        description="文化产业、IP创新项目",
                        eligibility="全体在校学生",
                        weight=0.15
                    ),
                ],
                timeline=[
                    TimelineEvent(phase="校赛", start_date="2026-03-01", end_date="2026-04-30"),
                    TimelineEvent(phase="省赛", start_date="2026-05-01", end_date="2026-06-30"),
                    TimelineEvent(phase="国赛", start_date="2026-10-01", end_date="2026-10-31"),
                ],
                requirements={
                    "team_size": "3-7人",
                    "leader_eligibility": "全日制在校学生",
                    "project_type": "创业计划项目",
                },
                evaluation_dimensions=[
                    EvaluationDimension(name="社会价值", weight=0.25, description="社会效益、服务国家战略"),
                    EvaluationDimension(name="科技创新", weight=0.25, description="技术创新性、可行性"),
                    EvaluationDimension(name="商业模式", weight=0.20, description="模式创新、市场前景"),
                    EvaluationDimension(name="团队协作", weight=0.20, description="团队互补性、执行力"),
                    EvaluationDimension(name="发展前景", weight=0.10, description="成长潜力、可复制性"),
                ],
                official_website="https://www.tiaozhanbei.net/",
            ),
            CompetitionInfo(
                id="san_chuang",
                name="三创赛",
                full_name="全国大学生电子商务\"创新、创意及创业\"挑战赛",
                organizer="教育部高等学校电子商务类专业教学指导委员会",
                level="国家级",
                category="A类",
                tracks=[
                    TrackInfo(
                        name="创新赛",
                        description="电子商务创新项目",
                        eligibility="全体在校学生",
                        weight=0.35
                    ),
                    TrackInfo(
                        name="创意赛",
                        description="电子商务创意设计",
                        eligibility="全体在校学生",
                        weight=0.30
                    ),
                    TrackInfo(
                        name="创业赛",
                        description="电子商务创业项目",
                        eligibility="全体在校学生",
                        weight=0.35
                    ),
                ],
                timeline=[
                    TimelineEvent(phase="校赛", start_date="2026-04-01", end_date="2026-05-31"),
                    TimelineEvent(phase="省赛", start_date="2026-06-01", end_date="2026-07-31"),
                    TimelineEvent(phase="国赛", start_date="2026-11-01", end_date="2026-11-30"),
                ],
                requirements={
                    "team_size": "3-5人",
                    "leader_eligibility": "全日制在校学生",
                    "project_type": "电子商务相关",
                },
                evaluation_dimensions=[
                    EvaluationDimension(name="创新性", weight=0.30, description="创新程度、技术含量"),
                    EvaluationDimension(name="可行性", weight=0.25, description="技术可行性、市场可行性"),
                    EvaluationDimension(name="商业价值", weight=0.25, description="盈利能力、投资价值"),
                    EvaluationDimension(name="团队能力", weight=0.20, description="团队素质、协作能力"),
                ],
                official_website="http://www.3chuang.net/",
            ),
        ]

        for comp in competitions:
            self._competitions[comp.id] = comp

    def get_competition(self, comp_id: str) -> Optional[CompetitionInfo]:
        """Get competition by ID."""
        return self._competitions.get(comp_id)

    def list_competitions(self) -> List[CompetitionInfo]:
        """List all competitions."""
        return list(self._competitions.values())

    def search_competitions(self, keyword: str) -> List[CompetitionInfo]:
        """Search competitions by keyword."""
        keyword = keyword.lower()
        results = []
        for comp in self._competitions.values():
            if (keyword in comp.name.lower() or 
                keyword in comp.full_name.lower() or
                keyword in comp.id.lower()):
                results.append(comp)
        return results

    def get_tracks(self, comp_id: str) -> List[TrackInfo]:
        """Get tracks for a competition."""
        comp = self.get_competition(comp_id)
        return comp.tracks if comp else []

    def get_evaluation_dimensions(self, comp_id: str) -> List[EvaluationDimension]:
        """Get evaluation dimensions for a competition."""
        comp = self.get_competition(comp_id)
        return comp.evaluation_dimensions if comp else []
