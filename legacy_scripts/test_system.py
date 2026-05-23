#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试商业计划书写作系统"""

import sys
from pathlib import Path

print("=" * 60)
print("系统测试开始")
print("=" * 60)

try:
    from business_plan_writer import BusinessPlanWriter, DocxBuilder
    print("✅ 模块导入成功！")
except Exception as e:
    print(f"❌ 模块导入失败：{e}")
    sys.exit(1)

try:
    writer = BusinessPlanWriter()
    print("✅ BusinessPlanWriter 初始化成功！")

    sections = writer.outline.get("sections", [])
    total_sections = writer.outline.get("total_sections", 0)
    print(f"大纲名称: {writer.outline.get('template_name', '未知')}")
    print(f"记录章节数: {total_sections}")
    print(f"实际章节数: {len(sections)}")

    if total_sections != len(sections):
        print(f"⚠️  注意：记录的章节数({total_sections})与实际章节数({len(sections)})不一致！")

    print("\n测试项目信息创建...")
    project_info = writer.create_project_info(
        product_name="智链供应链管理平台",
        company_name="武汉智链科技有限公司",
        project_desc="基于人工智能的供应链智能管理平台，专注于提升供应链效率"
    )
    print("✅ 项目信息创建成功！")

    print("\n测试内容计划生成...")
    content_plan = writer.generate_content_plan(project_info)
    print(f"✅ 内容计划生成成功！包含 {len(content_plan.get('sections', []))} 个章节")

    print("\n测试内容计划保存...")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    plan_path = output_dir / "test_plan.json"
    writer.save_content_plan(content_plan, str(plan_path))
    print(f"✅ 内容计划保存成功！位置: {plan_path}")

    print("\n" + "=" * 60)
    print("🎉 系统测试成功！")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
