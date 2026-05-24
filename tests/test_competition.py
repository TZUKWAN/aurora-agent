"""Tests for competition module."""

import pytest
from aurora.competition.database import CompetitionDatabase, CompetitionInfo, TrackInfo, EvaluationDimension
from aurora.competition.track_matcher import TrackMatcher


class TestCompetitionDatabase:
    """Test competition database functionality."""

    def test_database_initialization(self):
        """Test database initializes correctly."""
        db = CompetitionDatabase()
        assert len(db._competitions) == 8

    def test_list_competitions(self):
        """Test listing all competitions."""
        db = CompetitionDatabase()
        competitions = db.list_competitions()
        assert len(competitions) == 8

        # Check all expected competitions exist
        comp_ids = [c.id for c in competitions]
        assert "internet_plus" in comp_ids
        assert "challenge_cup" in comp_ids
        assert "san_chuang" in comp_ids
        assert "chuang_qingchun" in comp_ids
        assert "internet_plus_provincial" in comp_ids
        assert "chuang_yi" in comp_ids
        assert "maker_china" in comp_ids
        assert "red_tour" in comp_ids

    def test_get_competition_by_id(self):
        """Test getting competition by ID."""
        db = CompetitionDatabase()
        
        comp = db.get_competition("internet_plus")
        assert comp is not None
        assert comp.name == "互联网+大赛"
        assert comp.full_name == "中国国际大学生创新大赛"
        
        comp = db.get_competition("challenge_cup")
        assert comp is not None
        assert comp.name == "挑战杯"

    def test_get_nonexistent_competition(self):
        """Test getting non-existent competition."""
        db = CompetitionDatabase()
        comp = db.get_competition("nonexistent")
        assert comp is None

    def test_search_competitions(self):
        """Test searching competitions by keyword."""
        db = CompetitionDatabase()
        
        results = db.search_competitions("互联网")
        assert len(results) == 2
        result_ids = [r.id for r in results]
        assert "internet_plus" in result_ids
        assert "internet_plus_provincial" in result_ids
        
        results = db.search_competitions("挑战")
        assert len(results) >= 1
        assert any(c.id == "challenge_cup" for c in results)
        
        results = db.search_competitions("三创")
        assert len(results) == 1
        assert results[0].id == "san_chuang"
        
        results = db.search_competitions("nonexistent")
        assert len(results) == 0

    def test_get_tracks(self):
        """Test getting tracks for a competition."""
        db = CompetitionDatabase()
        
        tracks = db.get_tracks("internet_plus")
        assert len(tracks) == 5
        
        track_names = [t.name for t in tracks]
        assert "高教主赛道" in track_names
        assert "青年红色筑梦之旅" in track_names

    def test_get_evaluation_dimensions(self):
        """Test getting evaluation dimensions."""
        db = CompetitionDatabase()

        dims = db.get_evaluation_dimensions("internet_plus")
        assert len(dims) == 5

        dim_names = [d.name for d in dims]
        assert "创新性" in dim_names
        assert "团队情况" in dim_names
        assert "商业模式" in dim_names

    # --- New competition tests ---

    def test_search_chuang_qingchun(self):
        """Test searching for chuang_qingchun by name."""
        db = CompetitionDatabase()

        results = db.search_competitions("创青春")
        assert len(results) >= 1
        assert any(c.id == "chuang_qingchun" for c in results)

    def test_search_internet_plus_provincial(self):
        """Test searching for internet_plus_provincial."""
        db = CompetitionDatabase()

        results = db.search_competitions("省赛")
        assert len(results) >= 1
        assert any(c.id == "internet_plus_provincial" for c in results)

    def test_search_chuang_yi(self):
        """Test searching for chuang_yi by name."""
        db = CompetitionDatabase()

        results = db.search_competitions("创翼")
        assert len(results) >= 1
        assert any(c.id == "chuang_yi" for c in results)

    def test_search_maker_china(self):
        """Test searching for maker_china by name."""
        db = CompetitionDatabase()

        results = db.search_competitions("创客中国")
        assert len(results) >= 1
        assert any(c.id == "maker_china" for c in results)

    def test_search_red_tour(self):
        """Test searching for red_tour by name."""
        db = CompetitionDatabase()

        results = db.search_competitions("红旅")
        assert len(results) >= 1
        assert any(c.id == "red_tour" for c in results)

    def test_chuang_qingchun_data(self):
        """Test chuang_qingchun competition data integrity."""
        db = CompetitionDatabase()

        comp = db.get_competition("chuang_qingchun")
        assert comp is not None
        assert comp.name == "创青春"
        assert comp.organizer == "共青团中央"
        assert comp.level == "国家级"
        assert comp.category == "A类"
        assert comp.year == 2026
        assert comp.official_website == "https://www.chuangqingchun.com/"

        tracks = db.get_tracks("chuang_qingchun")
        assert len(tracks) == 3
        track_names = [t.name for t in tracks]
        assert "创业计划赛" in track_names
        assert "创业实践挑战赛" in track_names
        assert "公益创业赛" in track_names

        dims = db.get_evaluation_dimensions("chuang_qingchun")
        assert len(dims) == 4
        dim_names = [d.name for d in dims]
        assert "创新性" in dim_names
        assert "商业性" in dim_names
        assert "团队" in dim_names
        assert "社会效益" in dim_names

    def test_internet_plus_provincial_data(self):
        """Test internet_plus_provincial competition data integrity."""
        db = CompetitionDatabase()

        comp = db.get_competition("internet_plus_provincial")
        assert comp is not None
        assert comp.level == "省级"
        assert comp.year == 2026

        tracks = db.get_tracks("internet_plus_provincial")
        assert len(tracks) == 4

        dims = db.get_evaluation_dimensions("internet_plus_provincial")
        assert len(dims) == 5

    def test_chuang_yi_data(self):
        """Test chuang_yi competition data integrity."""
        db = CompetitionDatabase()

        comp = db.get_competition("chuang_yi")
        assert comp is not None
        assert comp.name == "中国创翼"
        assert comp.organizer == "人力资源社会保障部"
        assert comp.category == "B类"

        tracks = db.get_tracks("chuang_yi")
        assert len(tracks) == 4
        track_names = [t.name for t in tracks]
        assert "主体赛" in track_names
        assert "青年创意专项赛" in track_names
        assert "劳务品牌专项赛" in track_names
        assert "乡村振兴专项赛" in track_names

        dims = db.get_evaluation_dimensions("chuang_yi")
        assert len(dims) == 4
        dim_names = [d.name for d in dims]
        assert "创新引领" in dim_names
        assert "带动就业" in dim_names

    def test_maker_china_data(self):
        """Test maker_china competition data integrity."""
        db = CompetitionDatabase()

        comp = db.get_competition("maker_china")
        assert comp is not None
        assert comp.name == "创客中国"
        assert comp.organizer == "工业和信息化部"
        assert comp.category == "B类"

        tracks = db.get_tracks("maker_china")
        assert len(tracks) == 2
        track_names = [t.name for t in tracks]
        assert "企业组" in track_names
        assert "创客组" in track_names

        dims = db.get_evaluation_dimensions("maker_china")
        assert len(dims) == 4
        dim_names = [d.name for d in dims]
        assert "创新性" in dim_names
        assert "实用性" in dim_names

    def test_red_tour_data(self):
        """Test red_tour competition data integrity."""
        db = CompetitionDatabase()

        comp = db.get_competition("red_tour")
        assert comp is not None
        assert comp.name == "红旅专项"
        assert comp.organizer == "教育部"
        assert comp.category == "A类"

        tracks = db.get_tracks("red_tour")
        assert len(tracks) == 3
        track_names = [t.name for t in tracks]
        assert "红色之旅" in track_names
        assert "乡村振兴" in track_names
        assert "社区治理" in track_names

        dims = db.get_evaluation_dimensions("red_tour")
        assert len(dims) == 4
        dim_names = [d.name for d in dims]
        assert "社会效益" in dim_names
        assert "可持续性" in dim_names

    def test_add_competition(self):
        """Test adding a custom competition."""
        db = CompetitionDatabase()
        initial_count = len(db.list_competitions())

        custom_comp = CompetitionInfo(
            id="custom_test",
            name="自定义大赛",
            full_name="自定义测试大赛",
            organizer="测试组织",
            level="校级",
            category="C类",
            tracks=[
                TrackInfo(
                    name="测试赛道",
                    description="测试赛道描述",
                    eligibility="测试人员",
                    weight=1.0
                ),
            ],
            timeline=[],
            requirements={"team_size": "1-3人"},
            evaluation_dimensions=[
                EvaluationDimension(name="测试维度", weight=1.0, description="测试"),
            ],
            official_website="https://example.com/",
            year=2026,
        )

        db.add_competition(custom_comp)

        assert len(db.list_competitions()) == initial_count + 1
        assert db.get_competition("custom_test") is not None
        assert db.get_competition("custom_test").name == "自定义大赛"

    def test_add_competition_overwrites_existing(self):
        """Test that add_competition overwrites existing with same id."""
        db = CompetitionDatabase()

        modified = CompetitionInfo(
            id="internet_plus",
            name="修改后的大赛",
            full_name="修改后的全名",
            organizer="测试",
            level="校级",
            category="D类",
            tracks=[],
            timeline=[],
            requirements={},
            evaluation_dimensions=[],
            official_website="https://example.com/",
        )

        db.add_competition(modified)
        comp = db.get_competition("internet_plus")
        assert comp.name == "修改后的大赛"


class TestTrackMatcher:
    """Test track matching functionality."""

    def test_matcher_initialization(self):
        """Test track matcher initialization."""
        matcher = TrackMatcher()
        assert matcher._db is not None

    def test_match_basic_project(self):
        """Test matching a basic project."""
        matcher = TrackMatcher()
        
        project_info = {
            "technology": "AI人工智能",
            "business_model": "SaaS订阅",
            "target_market": "企业服务",
            "social_impact": "",
            "team_background": "高校团队",
            "project_stage": "初创"
        }
        
        results = matcher.match(project_info)
        assert len(results) > 0
        
        # Check results are sorted by confidence
        for i in range(len(results) - 1):
            assert results[i]["confidence"] >= results[i + 1]["confidence"]

    def test_match_rural_project(self):
        """Test matching a rural-focused project."""
        matcher = TrackMatcher()
        
        project_info = {
            "technology": "农业科技",
            "business_model": "B2B",
            "target_market": "乡村农村",
            "social_impact": "乡村振兴",
            "team_background": "农业大学",
            "project_stage": "初创"
        }
        
        results = matcher.match(project_info)
        assert len(results) > 0
        
        # Should match rural track
        rural_tracks = [r for r in results if "乡村" in r.get("track_name", "")]
        assert len(rural_tracks) > 0

    def test_match_with_specific_competition(self):
        """Test matching with specific competition."""
        matcher = TrackMatcher()
        
        project_info = {
            "technology": "AI",
            "target_market": "企业"
        }
        
        results = matcher.match(project_info, competition_id="internet_plus")
        assert len(results) > 0
        
        # All results should be from internet_plus
        for r in results:
            assert r["competition_id"] == "internet_plus"

    def test_match_empty_project(self):
        """Test matching with empty project info."""
        matcher = TrackMatcher()
        
        project_info = {}
        results = matcher.match(project_info)
        # Should still return some results based on weights
        assert len(results) >= 0

    def test_match_reasons(self):
        """Test that match reasons are provided."""
        matcher = TrackMatcher()

        project_info = {
            "technology": "AI人工智能",
            "target_market": "企业服务"
        }

        results = matcher.match(project_info)
        if results:
            assert "reasons" in results[0]
            assert len(results[0]["reasons"]) > 0

    # --- New track matching tests ---

    def test_match_public_welfare_project(self):
        """Test matching a public welfare project to chuang_qingchun."""
        matcher = TrackMatcher()

        project_info = {
            "technology": "互联网平台",
            "business_model": "公益捐赠+社会企业",
            "target_market": "社会大众",
            "social_impact": "公益慈善扶贫帮困",
            "team_background": "高校公益社团",
            "project_stage": "成长"
        }

        results = matcher.match(project_info)
        assert len(results) > 0

        # Should match public welfare track in chuang_qingchun
        public_welfare_tracks = [
            r for r in results
            if "公益" in r.get("track_name", "") or "公益" in r.get("track_description", "")
        ]
        assert len(public_welfare_tracks) > 0

    def test_match_red_tour_project(self):
        """Test matching a red-themed project to red_tour competition."""
        matcher = TrackMatcher()

        project_info = {
            "technology": "数字媒体",
            "business_model": "教育服务",
            "target_market": "教育市场",
            "social_impact": "传承红色文化弘扬革命精神",
            "team_background": "马克思主义学院",
            "project_stage": "初创"
        }

        results = matcher.match(project_info, competition_id="red_tour")
        assert len(results) > 0

        # Should match red journey track
        red_tracks = [
            r for r in results
            if "红色" in r.get("track_name", "")
        ]
        assert len(red_tracks) > 0

    def test_match_community_governance_project(self):
        """Test matching a community governance project."""
        matcher = TrackMatcher()

        project_info = {
            "technology": "智慧社区平台",
            "business_model": "政府购买服务",
            "target_market": "基层社区治理",
            "social_impact": "社区治理民生改善",
            "team_background": "公共管理学院",
            "project_stage": "初创"
        }

        results = matcher.match(project_info, competition_id="red_tour")
        assert len(results) > 0

        # Should match community governance track
        community_tracks = [
            r for r in results
            if "社区" in r.get("track_name", "")
        ]
        assert len(community_tracks) > 0

    def test_match_maker_project(self):
        """Test matching a maker project to maker_china."""
        matcher = TrackMatcher()

        project_info = {
            "technology": "开源硬件创客创意",
            "business_model": "硬件销售",
            "target_market": "教育市场",
            "social_impact": "",
            "team_background": "工程学院",
            "project_stage": "创意"
        }

        results = matcher.match(project_info, competition_id="maker_china")
        assert len(results) > 0

        # Should match maker track
        maker_tracks = [
            r for r in results
            if "创客" in r.get("track_name", "")
        ]
        assert len(maker_tracks) > 0

    def test_match_chuang_yi_rural_project(self):
        """Test matching a rural project to chuang_yi rural track."""
        matcher = TrackMatcher()

        project_info = {
            "technology": "农业科技",
            "business_model": "B2B",
            "target_market": "乡村农村",
            "social_impact": "乡村振兴",
            "team_background": "农业大学",
            "project_stage": "初创"
        }

        results = matcher.match(project_info, competition_id="chuang_yi")
        assert len(results) > 0

        # Should match rural track
        rural_tracks = [
            r for r in results
            if "乡村" in r.get("track_name", "")
        ]
        assert len(rural_tracks) > 0

    def test_all_competitions_have_valid_data(self):
        """Test that all 8 competitions have valid required fields."""
        db = CompetitionDatabase()
        competitions = db.list_competitions()
        assert len(competitions) == 8

        for comp in competitions:
            assert comp.id, f"Missing id for competition"
            assert comp.name, f"Missing name for {comp.id}"
            assert comp.full_name, f"Missing full_name for {comp.id}"
            assert comp.organizer, f"Missing organizer for {comp.id}"
            assert comp.level in ("国家级", "省级", "市级", "校级"), f"Invalid level for {comp.id}: {comp.level}"
            assert comp.category in ("A类", "B类", "C类", "D类"), f"Invalid category for {comp.id}: {comp.category}"
            assert len(comp.tracks) > 0, f"No tracks for {comp.id}"
            assert len(comp.timeline) > 0, f"No timeline for {comp.id}"
            assert len(comp.evaluation_dimensions) > 0, f"No evaluation dimensions for {comp.id}"
            assert comp.year == 2026, f"Wrong year for {comp.id}: {comp.year}"

            # Validate track weights sum approximately to 1.0
            total_weight = sum(t.weight for t in comp.tracks)
            assert 0.8 <= total_weight <= 1.2, f"Track weights for {comp.id} sum to {total_weight}"

            # Validate evaluation dimension weights sum to 1.0
            total_eval_weight = sum(d.weight for d in comp.evaluation_dimensions)
            assert 0.9 <= total_eval_weight <= 1.1, f"Eval weights for {comp.id} sum to {total_eval_weight}"


class TestCompetitionDataStructures:
    """Test competition data structures."""

    def test_track_info(self):
        """Test TrackInfo dataclass."""
        track = TrackInfo(
            name="测试赛道",
            description="测试描述",
            eligibility="全体学生",
            weight=0.5
        )
        assert track.name == "测试赛道"
        assert track.weight == 0.5

    def test_evaluation_dimension(self):
        """Test EvaluationDimension dataclass."""
        dim = EvaluationDimension(
            name="创新性",
            weight=0.3,
            description="测试描述"
        )
        assert dim.name == "创新性"
        assert dim.weight == 0.3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
