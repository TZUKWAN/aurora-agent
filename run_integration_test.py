import os
import sys
import traceback
import json

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

report = {"passed": [], "failed": []}

def run_test(name, func):
    try:
        func()
        report["passed"].append(name)
    except Exception as e:
        report["failed"].append({"name": name, "error": str(e), "trace": traceback.format_exc()})

def test_financial_engine():
    from aurora.financial.engine import FinancialSandbox
    res = FinancialSandbox.calculate_projection(100, 1000, 0.05, 10000, 20)
    if len(res["projections"]) != 3: raise ValueError("Projection years not 3")
    if "break_even_month" not in res: raise ValueError("Missing break_even_month calculation")

def test_memory_db():
    from aurora.memory.session_db import MemoryManager
    db_name = "test_mem.db"
    if os.path.exists(db_name): os.remove(db_name)
    mem = MemoryManager(db_name)
    uid = mem.create_or_update_session(None, {"name": "Test Project"})
    mem.save_section(uid, "market_analysis", "Mock Content")
    data = mem.load_session(uid)
    if data["sections"]["market_analysis"] != "Mock Content": raise ValueError("Memory mismatch")
    os.remove(db_name)

def test_web_search():
    from aurora.tools.web_search_tools import search_market_data
    res = search_market_data("AI market size 2024", max_results=1)
    if "Search error" in res: raise ValueError(f"DDG Search failed: {res}")

def test_visual_renderer():
    from aurora.visuals.renderer import HTMLRenderer
    hr = HTMLRenderer()
    if not hr.has_playwright:
        raise ValueError("Playwright is not detected by renderer")
    success = hr.render_to_png("<html><body style='background: blue;'><h1>Test</h1></body></html>", "test_render.png")
    if not success or not os.path.exists("test_render.png"):
        raise ValueError("Failed to create PNG via Playwright")
    os.remove("test_render.png")

def test_agent_init():
    # Will fail if llm setup errors out due to missing env var or config, handle gracefully
    from aurora.agent import AuroraAgent
    try:
        agent = AuroraAgent()
    except Exception as e:
        raise ValueError(f"Agent failed to init: {str(e)}")

def test_docx_export():
    from aurora.business_plan.generator import BusinessPlanGenerator
    bpg = BusinessPlanGenerator()
    plan_data = {
        "metadata": {"competition": "Test", "track": "Tech", "generated_at": "2024", "session_id": "test_id"},
        "sections": {
            "executive_summary": {"title": "Exec", "content": "Test content", "word_count": 100}
        }
    }
    # This invokes the patched export_to_docx
    res = bpg.export_to_docx(plan_data, "test_out.docx")
    if not res.get("success"):
        raise ValueError(res.get("message"))
    if not os.path.exists("test_out.docx"):
        raise ValueError("Docx file was not created on disk")
    os.remove("test_out.docx")

def test_ppt_patch():
    from aurora.presentation.ppt_generator import PPTGenerator
    ppt = PPTGenerator()
    if not hasattr(ppt, "renderer"):
        raise ValueError("PPT Generator was not patched correctly with HAS_VISUALS components")

run_test("Financial Engine", test_financial_engine)
run_test("Memory SQLite DB", test_memory_db)
run_test("DDG Web Search", test_web_search)
run_test("Playwright HTML Renderer", test_visual_renderer)
run_test("AuroraAgent Initialization", test_agent_init)
run_test("DOCX Generator (Patched)", test_docx_export)
run_test("PPTX Generator (Patched)", test_ppt_patch)

with open("test_report.json", "w") as f:
    json.dump(report, f, indent=2)
print("Finished automated testing.")
