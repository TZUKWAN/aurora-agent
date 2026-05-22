#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商业计划书撰写系统 - 完整设置与测试
完全基于《商业计划书大纲2026》标准
"""

import shutil
import os
from pathlib import Path

print("=" * 70)
print("商业计划书撰写系统 - 《商业计划书大纲2026》")
print("=" * 70)

src_outline = r"D:\计划书AI\outline_with_prompts.json"
dst_outline = r"d:\LATEXTEST\aurora-agent\outline_with_prompts.json"

print("\n[1/4] 检查大纲文件...")
if os.path.exists(src_outline):
    print(f"   ✓ 从 {src_outline} 复制...")
    shutil.copy(src_outline, dst_outline)
    print(f"   ✓ 大纲文件已复制到: {dst_outline}")
else:
    print(f"   ⚠ 源文件未找到: {src_outline}")

print("\n[2/4] 导入核心模块...")
from business_plan_writer import BusinessPlanWriter, DocxBuilder
print("   ✓ 核心模块导入成功")

print("\n[3/4] 初始化撰写器...")
writer = BusinessPlanWriter()
outline_info = writer.get_outline_info()
print(f"   ✓ 大纲模板: {outline_info.get('template_name')}")
print(f"   ✓ 总章节数: {outline_info.get('total_sections')}")
print(f"   ✓ 实际章节: {len(outline_info.get('sections', []))}")

print("\n[4/4] 创建示例内容计划...")
project_info = writer.create_project_info(
    product_name="智联供应链管理平台",
    company_name="武汉智链科技有限公司",
    project_description="基于人工智能的供应链智能管理平台，提升供应链效率"
)

content_plan = writer.generate_content_plan(project_info)

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

plan_path = output_dir / "content_plan.json"
writer.save_content_plan(content_plan, str(plan_path))

print("\n" + "=" * 70)
print("🎉 系统设置完成！")
print("=" * 70)
print("\n使用方法:")
print("  1. 编辑 output/content_plan.json 中的各章节内容")
print("  2. 使用 CLI 或直接调用 DocxBuilder 生成 Word 文档")
print("\n核心功能:")
print(f"  - 完整支持《商业计划书大纲2026》标准")
print(f"  - {outline_info.get('total_sections')} 个专业章节")
print(f"  - 高质量的提示词指导")
print(f"  - 表格和图片支持")
print(f"  - 中文字体支持 (宋体/黑体)")
