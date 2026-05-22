"""Manual test script for AuroraAgent - can be run without pytest."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aurora.competition.database import CompetitionDatabase, TrackInfo, EvaluationDimension
from aurora.competition.track_matcher import TrackMatcher
from aurora.business_plan.generator import BusinessPlanGenerator
from aurora.evaluation.engine import EvaluationEngine
from aurora.presentation.ppt_generator import PPTGenerator
from aurora.tools.registry import ToolRegistry


def test_competition_database():
    """Test competition database."""
    print("\n" + "="*60)
    print("测试 Competition Database")
    print("="*60)
    
    try:
        db = CompetitionDatabase()
        print(f"✓ 数据库初始化成功，包含 {len(db._competitions)} 个竞赛")
        
        # Test list competitions
        comps = db.list_competitions()
        print(f"✓ list_competitions() 返回 {len(comps)} 个竞赛")
        
        # Test get competition
        comp = db.get_competition("internet_plus")
        if comp:
            print(f"✓ get_competition('internet_plus') 成功: {comp.name}")
        else:
            print("✗ get_competition('internet_plus') 失败")
            
        # Test search
        results = db.search_competitions("互联网")
        print(f"✓ search_competitions('互联网') 返回 {len(results)} 个结果")
        
        # Test get tracks
        tracks = db.get_tracks("internet_plus")
        print(f"✓ get_tracks('internet_plus') 返回 {len(tracks)} 个赛道")
        
        # Test get dimensions
        dims = db.get_evaluation_dimensions("internet_plus")
        print(f"✓ get_evaluation_dimensions('internet_plus') 返回 {len(dims)} 个维度")
        
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_track_matcher():
    """Test track matcher."""
    print("\n" + "="*60)
    print("测试 Track Matcher")
    print("="*60)
    
    try:
        matcher = TrackMatcher()
        print("✓ TrackMatcher 初始化成功")
        
        # Test basic match
        project_info = {
            "technology": "AI人工智能",
            "target_market": "企业服务"
        }
        results = matcher.match(project_info)
        print(f"✓ match() 返回 {len(results)} 个匹配结果")
        
        if results:
            print(f"  最佳匹配: {results[0]['track_name']} (置信度: {results[0]['confidence']})")
        
        # Test rural project
        rural_project = {
            "technology": "农业科技",
            "target_market": "乡村农村",
            "social_impact": "乡村振兴"
        }
        results = matcher.match(rural_project)
        print(f"✓ 乡村项目匹配返回 {len(results)} 个结果")
        
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_business_plan_generator():
    """Test business plan generator."""
    print("\n" + "="*60)
    print("测试 Business Plan Generator")
    print("="*60)
    
    try:
        generator = BusinessPlanGenerator()
        print(f"✓ BusinessPlanGenerator 初始化成功")
        print(f"✓ 包含 {len(generator.SECTIONS)} 个章节")
        
        # Test generate plan
        project_info = {
            "project_name": "AI智能助手",
            "technology": "人工智能",
            "problem": "效率低下",
            "solution": "智能解决方案",
            "product": "AI助手",
            "target_market": "企业",
            "business_model": "订阅",
            "team_background": "高校团队",
            "funding": "50万"
        }
        
        plan = generator.generate(project_info, "internet_plus")
        print(f"✓ generate() 成功，包含 {len(plan['sections'])} 个章节")
        print(f"  竞赛: {plan['metadata']['competition']}")
        
        # Test generate section
        content = generator.generate_section(project_info, "executive_summary")
        print(f"✓ generate_section('executive_summary') 成功")
        print(f"  内容长度: {len(content)} 字符")
        
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_evaluation_engine():
    """Test evaluation engine."""
    print("\n" + "="*60)
    print("测试 Evaluation Engine")
    print("="*60)
    
    try:
        engine = EvaluationEngine()
        print("✓ EvaluationEngine 初始化成功")
        
        # Test evaluate
        project_info = {
            "technology": "AI人工智能",
            "innovation": "原创算法",
            "team_background": "985高校团队",
            "business_model": "盈利模式清晰",
            "social_impact": "带动就业"
        }
        
        result = engine.evaluate(project_info, "internet_plus")
        print(f"✓ evaluate() 成功")
        print(f"  总分: {result['overall_score']}")
        print(f"  维度数: {len(result['dimensions'])}")
        print(f"  建议数: {len(result['suggestions'])}")
        
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ppt_generator():
    """Test PPT generator."""
    print("\n" + "="*60)
    print("测试 PPT Generator")
    print("="*60)
    
    try:
        generator = PPTGenerator()
        print(f"✓ PPTGenerator 初始化成功")
        print(f"✓ 包含 {len(generator.SLIDE_STRUCTURE)} 页幻灯片")
        
        # Test generate PPT
        project_info = {
            "project_name": "创新项目",
            "team_name": "创新团队",
            "technology": "AI",
            "problem": "痛点",
            "solution": "方案"
        }
        
        ppt = generator.generate(project_info)
        print(f"✓ generate() 成功，包含 {ppt['slide_count']} 页幻灯片")
        
        # Test generate script
        script = generator.generate_script(ppt)
        print(f"✓ generate_script() 成功，脚本长度: {len(script)} 字符")
        
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_registry():
    """Test tool registry."""
    print("\n" + "="*60)
    print("测试 Tool Registry")
    print("="*60)
    
    try:
        registry = ToolRegistry()
        print("✓ ToolRegistry 初始化成功")
        
        # Register a test tool
        def test_handler(args):
            return f"测试工具被调用，参数: {args}"
        
        registry.register(
            "test_tool",
            "测试工具",
            {"type": "object", "properties": {}},
            test_handler
        )
        print("✓ register() 成功")
        
        # Test list tools
        tools = registry.list_tools()
        print(f"✓ list_tools() 返回 {len(tools)} 个工具")
        
        # Test get schemas
        schemas = registry.get_schemas()
        print(f"✓ get_schemas() 返回 {len(schemas)} 个schema")
        
        # Test dispatch
        result = registry.dispatch("test_tool", {})
        print(f"✓ dispatch() 成功: {result}")
        
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("AuroraAgent 全量测试")
    print("="*60)
    
    results = []
    
    results.append(("Competition Database", test_competition_database()))
    results.append(("Track Matcher", test_track_matcher()))
    results.append(("Business Plan Generator", test_business_plan_generator()))
    results.append(("Evaluation Engine", test_evaluation_engine()))
    results.append(("PPT Generator", test_ppt_generator()))
    results.append(("Tool Registry", test_tool_registry()))
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    print(f"总计: {len(results)} 个测试")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
