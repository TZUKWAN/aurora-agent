"""Competition-related tools for AuroraAgent."""

import json

from aurora.competition.database import CompetitionDatabase
from aurora.competition.track_matcher import TrackMatcher


def _register_tools(registry):
    """Register competition tools to the registry."""
    registry.register(
        "competition_search",
        "搜索竞赛信息",
        {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "搜索关键词"}
            },
            "required": ["keyword"]
        },
        _competition_search_handler
    )

    registry.register(
        "track_matcher",
        "智能匹配参赛赛道",
        {
            "type": "object",
            "properties": {
                "technology": {"type": "string", "description": "技术领域"},
                "business_model": {"type": "string", "description": "商业模式"},
                "target_market": {"type": "string", "description": "目标市场"},
                "social_impact": {"type": "string", "description": "社会影响"},
                "team_background": {"type": "string", "description": "团队背景"},
                "project_stage": {"type": "string", "description": "项目阶段"},
                "competition_id": {"type": "string", "description": "竞赛ID（可选）"}
            },
            "required": ["technology", "target_market"]
        },
        _track_matcher_handler
    )

    registry.register(
        "competition_info",
        "获取竞赛详细信息",
        {
            "type": "object",
            "properties": {
                "competition_id": {"type": "string", "description": "竞赛ID"}
            },
            "required": ["competition_id"]
        },
        _competition_info_handler
    )

    registry.register(
        "list_competitions",
        "列出所有可用竞赛",
        {},
        _list_competitions_handler
    )

    registry.register(
        "three_dimensional_logic",
        "使用白玉三维逻辑框架分析项目（选题维度、内容维度、展示维度）",
        {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "项目名称"},
                "project_description": {"type": "string", "description": "项目描述"},
                "competition_type": {"type": "string", "description": "竞赛类型（可选）"}
            },
            "required": ["project_name", "project_description"]
        },
        _three_dimensional_logic_handler
    )

    registry.register(
        "five_barriers_diagnosis",
        "使用白玉五重障碍框架诊断团队（心态障碍、思维障碍、人才障碍、制度障碍、组织障碍）",
        {
            "type": "object",
            "properties": {
                "team_description": {"type": "string", "description": "团队描述"},
                "project_description": {"type": "string", "description": "项目描述"}
            },
            "required": ["team_description", "project_description"]
        },
        _five_barriers_diagnosis_handler
    )


def _competition_search_handler(args):
    """Search competitions by keyword."""
    keyword = args.get("keyword", "")
    db = CompetitionDatabase()
    results = db.search_competitions(keyword)

    if not results:
        return json.dumps({"result": "未找到匹配的竞赛", "data": []}, ensure_ascii=False)

    data = []
    for comp in results:
        data.append({
            "id": comp.id,
            "name": comp.name,
            "full_name": comp.full_name,
            "organizer": comp.organizer,
            "level": comp.level,
            "category": comp.category
        })

    return json.dumps({"result": f"找到 {len(data)} 个匹配的竞赛", "data": data}, ensure_ascii=False)


def _track_matcher_handler(args):
    """Match project to competition tracks."""
    matcher = TrackMatcher()

    project_info = {
        "technology": args.get("technology", ""),
        "business_model": args.get("business_model", ""),
        "target_market": args.get("target_market", ""),
        "social_impact": args.get("social_impact", ""),
        "team_background": args.get("team_background", ""),
        "project_stage": args.get("project_stage", "")
    }

    competition_id = args.get("competition_id")

    results = matcher.match(project_info, competition_id)

    return json.dumps({
        "result": f"找到 {len(results)} 个匹配的赛道",
        "matches": results
    }, ensure_ascii=False)


def _competition_info_handler(args):
    """Get detailed information about a competition."""
    comp_id = args.get("competition_id")
    db = CompetitionDatabase()
    comp = db.get_competition(comp_id)

    if not comp:
        return json.dumps({"error": f"未找到竞赛: {comp_id}"}, ensure_ascii=False)

    tracks = []
    for track in comp.tracks:
        tracks.append({
            "name": track.name,
            "description": track.description,
            "eligibility": track.eligibility
        })

    timeline = []
    for event in comp.timeline:
        timeline.append({
            "phase": event.phase,
            "start_date": event.start_date,
            "end_date": event.end_date
        })

    dimensions = []
    for dim in comp.evaluation_dimensions:
        dimensions.append({
            "name": dim.name,
            "weight": dim.weight,
            "description": dim.description
        })

    return json.dumps({
        "id": comp.id,
        "name": comp.name,
        "full_name": comp.full_name,
        "organizer": comp.organizer,
        "level": comp.level,
        "category": comp.category,
        "tracks": tracks,
        "timeline": timeline,
        "requirements": comp.requirements,
        "evaluation_dimensions": dimensions,
        "official_website": comp.official_website
    }, ensure_ascii=False)


def _list_competitions_handler(args):
    """List all available competitions."""
    db = CompetitionDatabase()
    competitions = db.list_competitions()

    data = []
    for comp in competitions:
        data.append({
            "id": comp.id,
            "name": comp.name,
            "full_name": comp.full_name,
            "level": comp.level,
            "category": comp.category,
            "track_count": len(comp.tracks)
        })

    return json.dumps({"result": f"共有 {len(data)} 个竞赛", "data": data}, ensure_ascii=False)


def _three_dimensional_logic_handler(args):
    """Analyze a project using Baiyu's three-dimensional logic framework."""
    project_name = args.get("project_name", "")
    project_description = args.get("project_description", "")
    competition_type = args.get("competition_type", "")

    desc_len = len(project_description)
    has_name = len(project_name.strip()) > 0
    has_type = len(competition_type.strip()) > 0

    # --- Selection Dimension (选题维度) ---
    selection_score = 30
    selection_feedback = []
    if has_name:
        selection_score += 10
        selection_feedback.append("项目名称已提供，有助于选题聚焦")
    else:
        selection_feedback.append("缺少明确的项目名称，选题定位模糊")

    if desc_len > 100:
        selection_score += 15
        selection_feedback.append("项目描述详尽，选题方向清晰")
    elif desc_len > 30:
        selection_score += 8
        selection_feedback.append("项目描述基本完整，建议进一步细化选题方向")
    else:
        selection_feedback.append("项目描述过于简略，难以判断选题质量")

    if has_type:
        selection_score += 10
        selection_feedback.append(f"已明确竞赛类型（{competition_type}），选题匹配度可评估")
    else:
        selection_feedback.append("未指定竞赛类型，无法评估选题与竞赛的匹配度")

    if any(kw in project_description for kw in ["痛点", "需求", "问题", "市场", "创新"]):
        selection_score += 15
        selection_feedback.append("项目描述包含需求/痛点/创新关键词，选题具有针对性")
    else:
        selection_feedback.append("建议在项目描述中明确指出目标痛点和创新点")

    if any(kw in project_description for kw in ["社会", "价值", "影响", "公益", "可持续"]):
        selection_score += 10
        selection_feedback.append("项目体现了社会价值，选题具有意义感")
    else:
        selection_feedback.append("建议补充项目的社会价值和影响力说明")

    selection_score = min(selection_score, 100)

    # --- Content Dimension (内容维度) ---
    content_score = 25
    content_feedback = []
    if desc_len > 200:
        content_score += 15
        content_feedback.append("项目描述丰富，内容基础扎实")
    elif desc_len > 50:
        content_score += 7
        content_feedback.append("项目描述基本充分，建议补充更多技术细节")
    else:
        content_feedback.append("项目描述过于简短，内容深度不足")

    tech_keywords = ["技术", "算法", "数据", "AI", "人工智能", "机器学习", "区块链", "云", "物联网", "大数据"]
    tech_count = sum(1 for kw in tech_keywords if kw in project_description)
    if tech_count >= 3:
        content_score += 15
        content_feedback.append(f"项目涉及多种技术方向（{tech_count}个关键词），技术含量高")
    elif tech_count >= 1:
        content_score += 8
        content_feedback.append("项目包含技术要素，建议进一步阐述技术方案")
    else:
        content_feedback.append("未检测到技术关键词，建议补充技术实现方案")

    biz_keywords = ["商业模式", "盈利", "收入", "用户", "客户", "运营", "推广", "渠道"]
    biz_count = sum(1 for kw in biz_keywords if kw in project_description)
    if biz_count >= 2:
        content_score += 10
        content_feedback.append("项目包含商业模式要素，内容完整性较好")
    else:
        content_feedback.append("建议补充商业模式和运营策略相关内容")

    if any(kw in project_description for kw in ["团队", "成员", "合作", "分工"]):
        content_score += 8
        content_feedback.append("项目描述中包含团队信息")
    else:
        content_feedback.append("建议补充团队构成和分工信息")

    if any(kw in project_description for kw in ["计划", "时间", "路线", "里程碑", "阶段"]):
        content_score += 7
        content_feedback.append("项目有阶段性规划")
    else:
        content_feedback.append("建议补充项目路线图和时间计划")

    content_score = min(content_score, 100)

    # --- Presentation Dimension (展示维度) ---
    presentation_score = 20
    presentation_feedback = []
    if has_name:
        presentation_score += 8
        presentation_feedback.append("项目名称明确，有利于展示标题的提炼")

    if desc_len > 50:
        presentation_score += 8
        presentation_feedback.append("项目描述有一定篇幅，展示素材基础较好")
    else:
        presentation_feedback.append("项目描述过短，展示素材不足")

    if any(kw in project_description for kw in ["亮点", "特色", "优势", "创新", "领先"]):
        presentation_score += 15
        presentation_feedback.append("项目描述中包含亮点/优势关键词，有助于展示差异化")
    else:
        presentation_feedback.append("建议明确项目的核心亮点和竞争优势，增强展示效果")

    if any(kw in project_description for kw in ["数据", "成果", "效果", "测试", "验证"]):
        presentation_score += 12
        presentation_feedback.append("项目有数据/成果支撑，展示说服力强")
    else:
        presentation_feedback.append("建议补充量化数据和验证成果，提升展示可信度")

    if any(kw in project_description for kw in ["演示", "原型", "Demo", "MVP", "产品"]):
        presentation_score += 10
        presentation_feedback.append("项目有演示/原型基础，展示形式丰富")
    else:
        presentation_feedback.append("建议准备产品原型或演示材料，丰富展示形式")

    if has_type:
        presentation_score += 7
        presentation_feedback.append("已知竞赛类型，可针对性调整展示策略")
    else:
        presentation_feedback.append("未指定竞赛类型，建议根据目标竞赛调整展示风格")

    presentation_score = min(presentation_score, 100)

    overall_score = round((selection_score + content_score + presentation_score) / 3, 1)

    return json.dumps({
        "project_name": project_name,
        "competition_type": competition_type if competition_type else "未指定",
        "framework": "白玉三维逻辑框架",
        "dimensions": {
            "selection": {
                "label": "选题维度",
                "score": selection_score,
                "max_score": 100,
                "feedback": selection_feedback
            },
            "content": {
                "label": "内容维度",
                "score": content_score,
                "max_score": 100,
                "feedback": content_feedback
            },
            "presentation": {
                "label": "展示维度",
                "score": presentation_score,
                "max_score": 100,
                "feedback": presentation_feedback
            }
        },
        "overall_score": overall_score,
        "summary": _generate_3d_summary(selection_score, content_score, presentation_score)
    }, ensure_ascii=False)


def _generate_3d_summary(selection_score, content_score, presentation_score):
    """Generate a brief summary for three-dimensional analysis."""
    scores = {
        "选题": selection_score,
        "内容": content_score,
        "展示": presentation_score
    }
    strongest = max(scores, key=scores.get)
    weakest = min(scores, key=scores.get)

    parts = [f"三维分析结果："]
    for dim, score in scores.items():
        if score >= 75:
            parts.append(f"{dim}维度表现优秀（{score}分）")
        elif score >= 50:
            parts.append(f"{dim}维度表现中等（{score}分）")
        else:
            parts.append(f"{dim}维度需要提升（{score}分）")

    parts.append(f"最强维度：{strongest}；最需改进维度：{weakest}")
    return "。".join(parts)


def _five_barriers_diagnosis_handler(args):
    """Diagnose a team using Baiyu's five barriers framework."""
    team_description = args.get("team_description", "")
    project_description = args.get("project_description", "")

    team_len = len(team_description)
    project_len = len(project_description)

    # --- Mindset Barrier (心态障碍) ---
    mindset_score = 25
    mindset_feedback = []
    mindset_suggestions = []

    if any(kw in team_description for kw in ["积极", "热情", "主动", "自信", "坚定"]):
        mindset_score += 20
        mindset_feedback.append("团队描述中体现积极心态")
    elif any(kw in team_description for kw in ["消极", "犹豫", "焦虑", "担忧"]):
        mindset_score += 5
        mindset_feedback.append("团队描述中存在消极心态信号")
    else:
        mindset_feedback.append("未检测到明确的心态倾向")

    if any(kw in team_description for kw in ["目标", "愿景", "使命", "决心"]):
        mindset_score += 15
        mindset_feedback.append("团队有明确的目标感")
    else:
        mindset_feedback.append("团队目标感不明确")
        mindset_suggestions.append("建议明确团队共同目标，建立统一的愿景认知")

    if any(kw in team_description for kw in ["合作", "协作", "团结", "凝聚力"]):
        mindset_score += 15
        mindset_feedback.append("团队展现了协作精神")
    else:
        mindset_feedback.append("协作意识不够明显")
        mindset_suggestions.append("建议加强团队凝聚力建设，培养共赢心态")

    if any(kw in team_description for kw in ["坚持", "毅力", "韧性", "抗压"]):
        mindset_score += 10
        mindset_feedback.append("团队具备抗压和坚持的品质")
    else:
        mindset_suggestions.append("建议培养团队韧性和抗压能力，应对竞赛挑战")

    if team_len > 100:
        mindset_score += 5
    mindset_score = min(mindset_score, 100)
    if not mindset_suggestions:
        mindset_suggestions.append("保持当前积极心态，持续激励团队成员")

    # --- Thinking Barrier (思维障碍) ---
    thinking_score = 25
    thinking_feedback = []
    thinking_suggestions = []

    if any(kw in project_description for kw in ["创新", "独创", "新颖", "突破", "颠覆"]):
        thinking_score += 15
        thinking_feedback.append("项目体现创新思维")
    else:
        thinking_feedback.append("创新思维不够突出")
        thinking_suggestions.append("建议运用设计思维方法，从多角度思考项目创新点")

    if any(kw in team_description for kw in ["跨学科", "多学科", "交叉", "综合", "多元"]):
        thinking_score += 15
        thinking_feedback.append("团队具备跨学科思维")
    else:
        thinking_feedback.append("跨学科思维不足")
        thinking_suggestions.append("建议引入不同专业背景的成员，拓展思维广度")

    if any(kw in project_description for kw in ["分析", "调研", "研究", "数据驱动", "实证"]):
        thinking_score += 12
        thinking_feedback.append("项目展现了分析性思维")
    else:
        thinking_suggestions.append("建议加强数据和调研支撑，培养实证分析思维")

    if any(kw in team_description for kw in ["学习", "成长", "反思", "迭代", "复盘"]):
        thinking_score += 10
        thinking_feedback.append("团队有持续学习和反思意识")
    else:
        thinking_suggestions.append("建议建立定期复盘机制，培养成长型思维")

    if any(kw in project_description for kw in ["用户", "体验", "场景", "痛点", "需求分析"]):
        thinking_score += 10
        thinking_feedback.append("项目体现了用户思维")
    else:
        thinking_suggestions.append("建议从用户视角重新审视项目价值")

    thinking_score = min(thinking_score, 100)
    if not thinking_suggestions:
        thinking_suggestions.append("保持当前思维开放性，持续探索新方法论")

    # --- Talent Barrier (人才障碍) ---
    talent_score = 25
    talent_feedback = []
    talent_suggestions = []

    role_count = sum(1 for kw in ["开发", "设计", "产品", "运营", "技术", "管理", "市场", "负责人", "leader"]
                     if kw in team_description)
    if role_count >= 4:
        talent_score += 20
        talent_feedback.append(f"团队角色配置丰富（{role_count}个角色），人才结构完整")
    elif role_count >= 2:
        talent_score += 12
        talent_feedback.append(f"团队有基本角色分工（{role_count}个角色），但不够全面")
        talent_suggestions.append("建议补充缺失角色的成员，完善团队人才结构")
    else:
        talent_feedback.append("团队角色分工不明确")
        talent_suggestions.append("建议明确团队成员角色和职责，确保关键岗位有人负责")

    if any(kw in team_description for kw in ["经验", "资深", "专业", "背景", "学历"]):
        talent_score += 15
        talent_feedback.append("团队成员有专业背景描述")
    else:
        talent_feedback.append("未描述团队成员专业背景")
        talent_suggestions.append("建议评估团队成员专业能力，识别技能短板")

    team_size_keywords = ["人", "成员", "位"]
    if any(kw in team_description for kw in team_size_keywords):
        talent_score += 8
        talent_feedback.append("团队规模信息已提供")
    else:
        talent_suggestions.append("建议明确团队规模，评估人力是否充足")

    if any(kw in team_description for kw in ["互补", "协作", "搭配", "配合"]):
        talent_score += 10
        talent_feedback.append("团队有互补性描述")
    else:
        talent_suggestions.append("建议评估团队成员间的技能互补性")

    talent_score = min(talent_score, 100)
    if not talent_suggestions:
        talent_suggestions.append("团队人才配置良好，注意保持成员稳定性和持续成长")

    # --- Regulation Barrier (制度障碍) ---
    regulation_score = 25
    regulation_feedback = []
    regulation_suggestions = []

    if any(kw in team_description for kw in ["流程", "规范", "制度", "标准", "SOP"]):
        regulation_score += 20
        regulation_feedback.append("团队有流程制度意识")
    else:
        regulation_feedback.append("未检测到流程制度描述")
        regulation_suggestions.append("建议建立基本的工作流程和沟通规范")

    if any(kw in team_description for kw in ["会议", "汇报", "沟通", "例会", "站会"]):
        regulation_score += 15
        regulation_feedback.append("团队有定期沟通机制")
    else:
        regulation_suggestions.append("建议建立定期例会机制，确保信息同步")

    if any(kw in team_description for kw in ["考核", "评估", "目标", "KPI", "OKR"]):
        regulation_score += 15
        regulation_feedback.append("团队有目标考核机制")
    else:
        regulation_suggestions.append("建议建立目标管理和绩效评估机制")

    if any(kw in team_description for kw in ["文档", "记录", "归档", "知识库"]):
        regulation_score += 10
        regulation_feedback.append("团队有文档管理意识")
    else:
        regulation_suggestions.append("建议建立项目文档管理规范，沉淀团队知识")

    if any(kw in team_description for kw in ["分工", "责任", "负责", "职责"]):
        regulation_score += 10
        regulation_feedback.append("团队有明确的责任分工")
    else:
        regulation_suggestions.append("建议明确每个成员的职责范围和问责机制")

    regulation_score = min(regulation_score, 100)
    if not regulation_suggestions:
        regulation_suggestions.append("团队制度完善，注意根据项目进展动态调整")

    # --- Organization Barrier (组织障碍) ---
    organization_score = 25
    organization_feedback = []
    organization_suggestions = []

    if any(kw in team_description for kw in ["领导", "负责人", "队长", "组长", "协调"]):
        organization_score += 18
        organization_feedback.append("团队有明确的领导核心")
    else:
        organization_feedback.append("未检测到明确的领导角色")
        organization_suggestions.append("建议指定团队负责人，建立清晰的领导体系")

    if any(kw in team_description for kw in ["架构", "层次", "扁平", "层级", "组织"]):
        organization_score += 15
        organization_feedback.append("团队有组织架构描述")
    else:
        organization_suggestions.append("建议明确团队组织架构，优化决策效率")

    if any(kw in team_description for kw in ["远程", "线上", "协同", "工具", "Slack", "飞书", "钉钉"]):
        organization_score += 12
        organization_feedback.append("团队使用了协同工具或远程协作方式")
    else:
        organization_suggestions.append("建议选择合适的协同工具，提升团队协作效率")

    if any(kw in team_description for kw in ["敏捷", "Scrum", "迭代", "冲刺", "sprint"]):
        organization_score += 10
        organization_feedback.append("团队采用了敏捷管理方法")
    else:
        organization_suggestions.append("建议引入敏捷管理方法，提高项目推进效率")

    if any(kw in team_description for kw in ["资源", "资金", "支持", "赞助", "预算"]):
        organization_score += 8
        organization_feedback.append("团队有资源意识")
    else:
        organization_suggestions.append("建议盘点团队可用资源，做好资源规划")

    organization_score = min(organization_score, 100)
    if not organization_suggestions:
        organization_suggestions.append("团队组织结构健康，注意随项目发展动态优化")

    # --- Overall ---
    overall_score = round(
        (mindset_score + thinking_score + talent_score + regulation_score + organization_score) / 5, 1
    )

    return json.dumps({
        "framework": "白玉五重障碍框架",
        "barriers": {
            "mindset": {
                "label": "心态障碍",
                "score": mindset_score,
                "max_score": 100,
                "feedback": mindset_feedback,
                "suggestions": mindset_suggestions
            },
            "thinking": {
                "label": "思维障碍",
                "score": thinking_score,
                "max_score": 100,
                "feedback": thinking_feedback,
                "suggestions": thinking_suggestions
            },
            "talent": {
                "label": "人才障碍",
                "score": talent_score,
                "max_score": 100,
                "feedback": talent_feedback,
                "suggestions": talent_suggestions
            },
            "regulation": {
                "label": "制度障碍",
                "score": regulation_score,
                "max_score": 100,
                "feedback": regulation_feedback,
                "suggestions": regulation_suggestions
            },
            "organization": {
                "label": "组织障碍",
                "score": organization_score,
                "max_score": 100,
                "feedback": organization_feedback,
                "suggestions": organization_suggestions
            }
        },
        "overall_score": overall_score,
        "summary": _generate_5b_summary(
            mindset_score, thinking_score, talent_score, regulation_score, organization_score
        )
    }, ensure_ascii=False)


def _generate_5b_summary(mindset, thinking, talent, regulation, organization):
    """Generate a brief summary for five barriers diagnosis."""
    scores = {
        "心态障碍": mindset,
        "思维障碍": thinking,
        "人才障碍": talent,
        "制度障碍": regulation,
        "组织障碍": organization
    }

    strongest = max(scores, key=scores.get)
    weakest = min(scores, key=scores.get)

    parts = ["五重障碍诊断结果："]
    for barrier, score in scores.items():
        if score >= 75:
            parts.append(f"{barrier}风险较低（{score}分）")
        elif score >= 50:
            parts.append(f"{barrier}风险中等（{score}分）")
        else:
            parts.append(f"{barrier}风险较高（{score}分），需重点关注")

    parts.append(f"表现最好的维度：{strongest}；最需改善的维度：{weakest}")
    return "。".join(parts)
