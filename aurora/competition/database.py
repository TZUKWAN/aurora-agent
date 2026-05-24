"""Competition database for AuroraAgent."""

from dataclasses import dataclass
from typing import Dict, List, Optional


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
            CompetitionInfo(
                id="chuang_qingchun",
                name="创青春",
                full_name="\"创青春\"全国大学生创业大赛",
                organizer="共青团中央",
                level="国家级",
                category="A类",
                tracks=[
                    TrackInfo(
                        name="创业计划赛",
                        description="面向大学生的创业计划项目评审",
                        eligibility="全日制在校大学生及毕业3年以内 alumni",
                        weight=0.40
                    ),
                    TrackInfo(
                        name="创业实践挑战赛",
                        description="已落地运营的创业实践项目",
                        eligibility="已注册公司或已实际运营的团队",
                        weight=0.35
                    ),
                    TrackInfo(
                        name="公益创业赛",
                        description="以社会公益为导向的创业项目",
                        eligibility="全体在校学生及社会组织",
                        weight=0.25
                    ),
                ],
                timeline=[
                    TimelineEvent(phase="校赛", start_date="2026-03-01", end_date="2026-04-30"),
                    TimelineEvent(phase="省赛", start_date="2026-05-01", end_date="2026-06-30"),
                    TimelineEvent(phase="国赛", start_date="2026-09-01", end_date="2026-10-31"),
                ],
                requirements={
                    "team_size": "3-5人",
                    "leader_eligibility": "全日制在校学生或毕业3年以内",
                    "project_type": "创业计划、创业实践、公益创业",
                },
                evaluation_dimensions=[
                    EvaluationDimension(name="创新性", weight=0.30, description="项目原创性、技术或模式创新程度"),
                    EvaluationDimension(name="商业性", weight=0.30, description="商业模式完整性、市场可行性、盈利前景"),
                    EvaluationDimension(name="团队", weight=0.20, description="团队背景、能力互补、执行力"),
                    EvaluationDimension(name="社会效益", weight=0.20, description="社会价值创造、带动就业、公共利益贡献"),
                ],
                official_website="https://www.chuangqingchun.com/",
            ),
            CompetitionInfo(
                id="internet_plus_provincial",
                name="互联网+省赛",
                full_name="中国国际大学生创新大赛（省赛专项）",
                organizer="各省教育厅",
                level="省级",
                category="A类",
                tracks=[
                    TrackInfo(
                        name="高教主赛道",
                        description="面向高等院校全日制在校学生的创新项目（省赛版）",
                        eligibility="全日制在校本科生、研究生",
                        weight=0.45
                    ),
                    TrackInfo(
                        name="青年红色筑梦之旅",
                        description="助力乡村振兴、社会服务的创新创业项目（省赛版）",
                        eligibility="全体在校学生",
                        weight=0.25
                    ),
                    TrackInfo(
                        name="职教赛道",
                        description="职业院校学生的创新技能项目（省赛版）",
                        eligibility="职业院校在校学生",
                        weight=0.15
                    ),
                    TrackInfo(
                        name="产业命题赛道",
                        description="企业命题的技术解决方案（省赛版）",
                        eligibility="全体在校学生",
                        weight=0.15
                    ),
                ],
                timeline=[
                    TimelineEvent(phase="校赛报名", start_date="2026-02-01", end_date="2026-03-31"),
                    TimelineEvent(phase="省赛", start_date="2026-04-01", end_date="2026-05-31"),
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
                id="chuang_yi",
                name="中国创翼",
                full_name="中国创翼创业创新大赛",
                organizer="人力资源社会保障部",
                level="国家级",
                category="B类",
                tracks=[
                    TrackInfo(
                        name="主体赛",
                        description="面向所有创业项目的综合赛道",
                        eligibility="各类创业团队及小微企业",
                        weight=0.35
                    ),
                    TrackInfo(
                        name="青年创意专项赛",
                        description="面向青年群体的创意创业项目",
                        eligibility="35岁以下青年创业团队",
                        weight=0.25
                    ),
                    TrackInfo(
                        name="劳务品牌专项赛",
                        description="具有地方特色的劳务品牌创业项目",
                        eligibility="劳务品牌相关创业团队",
                        weight=0.20
                    ),
                    TrackInfo(
                        name="乡村振兴专项赛",
                        description="服务乡村振兴战略的创业项目",
                        eligibility="面向农村的创业团队及企业",
                        weight=0.20
                    ),
                ],
                timeline=[
                    TimelineEvent(phase="市赛", start_date="2026-03-01", end_date="2026-05-31"),
                    TimelineEvent(phase="省赛", start_date="2026-06-01", end_date="2026-07-31"),
                    TimelineEvent(phase="国赛", start_date="2026-09-01", end_date="2026-10-31"),
                ],
                requirements={
                    "team_size": "1-5人",
                    "leader_eligibility": "创业团队负责人或企业法人",
                    "project_type": "创业创新项目",
                },
                evaluation_dimensions=[
                    EvaluationDimension(name="创新引领", weight=0.30, description="项目创新性、技术或模式引领性"),
                    EvaluationDimension(name="带动就业", weight=0.25, description="直接及间接带动就业人数与质量"),
                    EvaluationDimension(name="项目团队", weight=0.25, description="团队专业能力、创业经验、协作水平"),
                    EvaluationDimension(name="发展前景", weight=0.20, description="市场前景、成长潜力、可持续性"),
                ],
                official_website="https://cy.ncss.org.cn/",
            ),
            CompetitionInfo(
                id="maker_china",
                name="创客中国",
                full_name="创客中国创新创业大赛",
                organizer="工业和信息化部",
                level="国家级",
                category="B类",
                tracks=[
                    TrackInfo(
                        name="企业组",
                        description="已注册企业的创新创业项目",
                        eligibility="注册企业在孵或成长型企业",
                        weight=0.55
                    ),
                    TrackInfo(
                        name="创客组",
                        description="个人或团队的创意创新项目",
                        eligibility="创业团队、个人创客",
                        weight=0.45
                    ),
                ],
                timeline=[
                    TimelineEvent(phase="报名", start_date="2026-04-01", end_date="2026-06-30"),
                    TimelineEvent(phase="区域赛", start_date="2026-07-01", end_date="2026-08-31"),
                    TimelineEvent(phase="决赛", start_date="2026-09-01", end_date="2026-10-31"),
                ],
                requirements={
                    "team_size": "1-5人",
                    "leader_eligibility": "企业法人或团队负责人",
                    "project_type": "技术创新、产品创新",
                },
                evaluation_dimensions=[
                    EvaluationDimension(name="创新性", weight=0.30, description="技术或产品创新程度、知识产权"),
                    EvaluationDimension(name="实用性", weight=0.25, description="产品落地能力、市场适用性"),
                    EvaluationDimension(name="团队", weight=0.25, description="团队专业能力、执行力、互补性"),
                    EvaluationDimension(name="商业模式", weight=0.20, description="商业模式完整性、盈利可行性"),
                ],
                official_website="https://www.cnmaker.org.cn/",
            ),
            CompetitionInfo(
                id="red_tour",
                name="红旅专项",
                full_name="中国国际大学生创新大赛红色筑梦之旅专项赛",
                organizer="教育部",
                level="国家级",
                category="A类",
                tracks=[
                    TrackInfo(
                        name="红色之旅",
                        description="传承红色基因、弘扬革命精神的创新创业项目",
                        eligibility="全体在校学生",
                        weight=0.35
                    ),
                    TrackInfo(
                        name="乡村振兴",
                        description="服务乡村振兴战略的创新创业项目",
                        eligibility="全体在校学生",
                        weight=0.35
                    ),
                    TrackInfo(
                        name="社区治理",
                        description="服务基层社区治理创新的创业项目",
                        eligibility="全体在校学生",
                        weight=0.30
                    ),
                ],
                timeline=[
                    TimelineEvent(phase="报名", start_date="2026-03-01", end_date="2026-04-30"),
                    TimelineEvent(phase="省赛", start_date="2026-05-01", end_date="2026-06-30"),
                    TimelineEvent(phase="国赛", start_date="2026-08-01", end_date="2026-09-30"),
                ],
                requirements={
                    "team_size": "3-5人",
                    "leader_eligibility": "全日制在校学生",
                    "project_type": "红色教育、乡村振兴、社区治理",
                },
                evaluation_dimensions=[
                    EvaluationDimension(name="社会效益", weight=0.30, description="社会价值创造、公益影响力、群众受益面"),
                    EvaluationDimension(name="创新性", weight=0.25, description="项目模式创新、技术应用创新"),
                    EvaluationDimension(name="可持续性", weight=0.25, description="项目长期运营能力、可复制推广性"),
                    EvaluationDimension(name="团队", weight=0.20, description="团队协作、执行力、社会责任感"),
                ],
                official_website="https://cy.ncss.org.cn/",
            ),
        ]

        for comp in competitions:
            self._competitions[comp.id] = comp

    def add_competition(self, competition: CompetitionInfo) -> None:
        """Add a custom competition to the database."""
        self._competitions[competition.id] = competition

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
