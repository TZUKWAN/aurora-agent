"""大创申报模块完整测试脚本."""

import os
import sys
import tempfile

TEST_DIR = tempfile.mkdtemp(prefix="dachuang_test_")
print(f"测试输出目录: {TEST_DIR}")


def test_application():
    """测试申报书生成器."""
    from application import DachuangApplicationGenerator

    gen = DachuangApplicationGenerator()
    project = {
        "project_name": "基于深度学习的古籍文字识别系统",
        "project_type": "创新训练",
        "discipline": "计算机科学与技术",
        "leader_name": "张三",
        "leader_id": "2022010001",
        "leader_major": "计算机科学与技术",
        "leader_grade": "2022级",
        "team_members": [
            {"name": "李四", "id": "2022010002", "major": "软件工程", "grade": "2022级", "role": "算法设计与实现"},
            {"name": "王五", "id": "2022010003", "major": "人工智能", "grade": "2022级", "role": "数据标注与预处理"},
        ],
        "advisor_name": "陈教授",
        "advisor_title": "教授",
        "advisor_department": "计算机学院",
        "project_summary": "本项目旨在利用深度学习技术，开发一套针对古籍文字的高精度识别系统。",
        "application_reason": "随着数字化图书馆建设的推进，古籍数字化需求日益增长。",
        "research_content": "1. 构建古籍文字数据集；2. 设计深度学习模型架构；3. 开发端到端识别系统。",
        "technical_route": "采用ResNet+Transformer的混合架构，结合注意力机制。",
        "innovation_points": "1. 首次提出针对古籍的专用识别模型；2. 引入多任务学习框架。",
        "expected_outcomes": "1. 发表学术论文1-2篇；2. 申请软件著作权1项；3. 完成系统原型。",
        "budget_items": [
            {"category": "设备费", "item_name": "GPU服务器租赁", "amount": 3000.0, "description": "模型训练所需算力资源"},
            {"category": "材料费", "item_name": "数据集采购", "amount": 1500.0, "description": "古籍扫描图像采购"},
            {"category": "测试费", "item_name": "模型评测", "amount": 800.0, "description": "第三方评测服务"},
            {"category": "差旅费", "item_name": "古籍馆调研", "amount": 1200.0, "description": "实地采集数据"},
            {"category": "出版费", "item_name": "论文版面费", "amount": 2000.0, "description": "核心期刊发表"},
            {"category": "劳务费", "item_name": "数据标注", "amount": 1500.0, "description": "外包数据标注服务"},
        ],
        "start_date": "2025-06-01",
        "end_date": "2026-05-31",
    }
    content = gen.generate(project)
    assert content["meta"]["generator"] == "DachuangApplicationGenerator"
    assert content["basic_info"]["project_name"] == "基于深度学习的古籍文字识别系统"
    assert content["budget"]["total_amount"] == 10000.0

    # 测试DOCX导出
    docx_path = os.path.join(TEST_DIR, "申报书.docx")
    gen.export_to_docx(content, docx_path)
    assert os.path.isfile(docx_path), "DOCX文件未生成"
    assert os.path.getsize(docx_path) > 0, "DOCX文件为空"

    # 测试JSON导出
    json_path = os.path.join(TEST_DIR, "申报书.json")
    gen.export_to_json(content, json_path)
    assert os.path.isfile(json_path), "JSON文件未生成"

    # 测试错误处理
    try:
        gen.generate({"project_name": "test"})
        assert False, "应抛出ValueError"
    except ValueError:
        pass

    print("  [application.py] 申报书生成器测试通过")


def test_midterm():
    """测试中期检查报告生成器."""
    from midterm import MidtermReportGenerator

    gen = MidtermReportGenerator()
    report = {
        "project_name": "基于深度学习的古籍文字识别系统",
        "project_type": "创新训练",
        "leader_name": "张三",
        "leader_id": "2022010001",
        "advisor_name": "陈教授",
        "report_date": "2025-12-15",
        "project_progress": "项目整体进展良好，目前已完成数据集构建和模型初步设计。",
        "completed_work": [
            {"phase": "第一阶段", "description": "收集并整理5000页古籍扫描图像", "completion_date": "2025-09-30", "status": "已完成"},
            {"phase": "第二阶段", "description": "设计混合模型架构", "completion_date": "2025-11-15", "status": "已完成"},
        ],
        "existing_problems": [
            {"problem": "图像质量参差不齐", "impact": "影响识别准确率", "solution": "引入图像修复预处理"},
        ],
        "next_steps": [
            {"phase": "第三阶段", "plan": "模型训练与调优", "deadline": "2026-02-28", "responsible": "张三"},
        ],
        "budget_usage": {
            "allocated": 10000.0,
            "spent": 4800.0,
            "details": [
                {"category": "设备费", "amount": 2000.0, "description": "GPU服务器租赁"},
                {"category": "材料费", "amount": 1000.0, "description": "数据集采购"},
            ],
        },
        "achievement_preview": "已完成5000页古籍图像采集，构建10万字符标注数据集。",
        "advisor_comment": "项目进展顺利，建议按计划推进。",
    }
    content = gen.generate(report)
    assert content["meta"]["generator"] == "MidtermReportGenerator"
    assert content["budget_usage"]["usage_rate"] == 48.0

    docx_path = os.path.join(TEST_DIR, "中期检查报告.docx")
    gen.export_to_docx(content, docx_path)
    assert os.path.isfile(docx_path)

    json_path = os.path.join(TEST_DIR, "中期检查报告.json")
    gen.export_to_json(content, json_path)
    assert os.path.isfile(json_path)

    print("  [midterm.py] 中期检查报告生成器测试通过")


def test_final_report():
    """测试结题报告生成器."""
    from final_report import FinalReportGenerator

    gen = FinalReportGenerator()
    report = {
        "project_name": "基于深度学习的古籍文字识别系统",
        "project_type": "创新训练",
        "leader_name": "张三",
        "leader_id": "2022010001",
        "advisor_name": "陈教授",
        "start_date": "2025-06-01",
        "end_date": "2026-05-31",
        "completion_status": "按期完成",
        "project_summary": "本项目按照计划完成了所有预定目标。",
        "achievements": [
            {"type": "论文", "title": "基于深度学习的古籍文字识别方法研究", "status": "已发表", "date": "2026-03-15", "description": "发表于《计算机学报》"},
            {"type": "软件著作权", "title": "古籍文字智能识别系统V1.0", "status": "已登记", "date": "2026-04-20", "description": "团队共同完成"},
        ],
        "budget_final": {
            "allocated": 10000.0,
            "spent": 9650.0,
            "details": [
                {"category": "设备费", "amount": 3000.0, "description": "GPU服务器租赁"},
                {"category": "材料费", "amount": 1500.0, "description": "数据集采购"},
                {"category": "出版费", "amount": 2000.0, "description": "论文版面费"},
            ],
        },
        "research_summary": "构建了高质量训练数据集，设计了混合架构模型。",
        "innovation_summary": "首次提出专门针对古籍文字的深度学习识别模型。",
        "experience_summary": "掌握了完整科研流程，深入学习了前沿技术。",
        "future_outlook": "模型对严重破损页面识别效果仍有提升空间。",
        "team_contributions": [
            {"name": "张三", "contribution": "项目负责人，负责整体方案设计"},
            {"name": "李四", "contribution": "负责算法实现与模型调优"},
        ],
        "advisor_evaluation": "项目团队表现优秀，建议评定为优秀等级。",
        "department_evaluation": "同意结题，建议评定为优秀等级。",
    }
    content = gen.generate(report)
    assert content["meta"]["generator"] == "FinalReportGenerator"
    assert len(content["achievements"]) == 2
    assert content["budget_final"]["usage_rate"] == 96.5

    docx_path = os.path.join(TEST_DIR, "结题报告.docx")
    gen.export_to_docx(content, docx_path)
    assert os.path.isfile(docx_path)

    json_path = os.path.join(TEST_DIR, "结题报告.json")
    gen.export_to_json(content, json_path)
    assert os.path.isfile(json_path)

    print("  [final_report.py] 结题报告生成器测试通过")


def test_budget():
    """测试经费预算生成器."""
    from budget import BudgetGenerator

    gen = BudgetGenerator()
    items = [
        {"category": "设备费", "item_name": "GPU服务器租赁", "amount": 3000.0, "description": "模型训练算力", "quantity": 12, "unit_price": 250.0},
        {"category": "材料费", "item_name": "数据集采购", "amount": 1500.0, "description": "古籍扫描图像", "quantity": 1, "unit_price": 1500.0},
        {"category": "差旅费", "item_name": "古籍馆调研", "amount": 1200.0, "description": "实地采集数据", "quantity": 3, "unit_price": 400.0},
        {"category": "出版/文献/信息传播费", "item_name": "论文版面费", "amount": 2000.0, "description": "核心期刊发表", "quantity": 1, "unit_price": 2000.0},
        {"category": "劳务费", "item_name": "数据标注", "amount": 1500.0, "description": "外包标注服务", "quantity": 1, "unit_price": 1500.0},
    ]
    budget = gen.generate_budget_table(items)
    assert budget["total_amount"] == 9200.0
    assert budget["item_count"] == 5
    assert budget["category_summary"]["设备费"] == 3000.0

    # 校验
    validation = gen.validate_budget(budget, max_amount=10000)
    assert validation["is_valid"] is True
    assert len(validation["errors"]) == 0

    # Excel导出
    excel_path = os.path.join(TEST_DIR, "经费预算表.xlsx")
    gen.export_budget_excel(budget, excel_path)
    assert os.path.isfile(excel_path)
    assert os.path.getsize(excel_path) > 0

    # JSON导出
    json_path = os.path.join(TEST_DIR, "经费预算表.json")
    gen.export_to_json(budget, json_path)
    assert os.path.isfile(json_path)

    # 测试超限校验
    over_budget = gen.generate_budget_table([
        {"category": "设备费", "item_name": "服务器", "amount": 8000.0, "description": "GPU"},
        {"category": "材料费", "item_name": "数据集", "amount": 3000.0, "description": "数据"},
    ])
    validation2 = gen.validate_budget(over_budget, max_amount=10000)
    assert validation2["is_valid"] is False
    assert len(validation2["errors"]) > 0

    print("  [budget.py] 经费预算生成器测试通过")


if __name__ == "__main__":
    print("=" * 60)
    print("大创申报模块完整测试")
    print("=" * 60)

    test_application()
    test_midterm()
    test_final_report()
    test_budget()

    print("\n" + "=" * 60)
    print("所有测试通过!")
    print(f"测试输出文件位于: {TEST_DIR}")
    print("\n生成的文件:")
    for f in sorted(os.listdir(TEST_DIR)):
        size = os.path.getsize(os.path.join(TEST_DIR, f))
        print(f"  {f} ({size} bytes)")
    print("=" * 60)
