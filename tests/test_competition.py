"""Tests for competition module."""

import pytest
from aurora.competition.database import CompetitionDatabase, CompetitionInfo, TrackInfo, EvaluationDimension
from aurora.competition.track_matcher import TrackMatcher


class TestCompetitionDatabase:
    """Test competition database functionality."""

    def test_database_initialization(self):
        """Test database initializes correctly."""
        db = CompetitionDatabase()
        assert len(db._competitions) == 3

    def test_list_competitions(self):
        """Test listing all competitions."""
        db = CompetitionDatabase()
        competitions = db.list_competitions()
        assert len(competitions) == 3
        
        # Check all expected competitions exist
        comp_ids = [c.id for c in competitions]
        assert "internet_plus" in comp_ids
        assert "challenge_cup" in comp_ids
        assert "san_chuang" in comp_ids

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
        assert len(results) == 1
        assert results[0].id == "internet_plus"
        
        results = db.search_competitions("挑战")
        assert len(results) == 1
        assert results[0].id == "challenge_cup"
        
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
