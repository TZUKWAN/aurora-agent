import sys
import traceback
sys.path.insert(0, '/d/SophiaAgentWork/aurora-agent')

def run_test():
    try:
        from aurora.business_plan.generator import BusinessPlanGenerator
        bpg = BusinessPlanGenerator()
        plan_data = {
            "metadata": {"competition": "Test", "track": "Tech", "generated_at": "2024", "session_id": "test_id"},
            "sections": {
                "executive_summary": {"title": "Exec", "content": "Test content", "word_count": 100},
                # Add project_overview because KeyError was thrown here
                "project_overview": {"title": "PO", "content": "PO content", "word_count": 100},
                "market_analysis": {"title": "MA", "content": "MA content", "word_count": 100},
                "product_service": {"title": "PS", "content": "PS content", "word_count": 100},
                "business_model": {"title": "BM", "content": "BM content", "word_count": 100},
                "marketing_strategy": {"title": "MS", "content": "MS content", "word_count": 100},
                "operation_plan": {"title": "OP", "content": "OP content", "word_count": 100},
                "team_introduction": {"title": "TI", "content": "TI content", "word_count": 100},
                "financial_analysis": {"title": "FA", "content": "FA content", "word_count": 100},
                "risk_assessment": {"title": "RA", "content": "RA content", "word_count": 100},
            }
        }
        res = bpg.export_to_docx(plan_data, "test_out_docx_fixed.docx")
        if not res.get("success"):
            raise ValueError(res.get("message"))
        print("DOCX Export Test: PASSED")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        traceback.print_exc()
        return False

run_test()
