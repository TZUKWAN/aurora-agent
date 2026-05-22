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
