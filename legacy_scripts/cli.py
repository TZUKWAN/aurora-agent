#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商业计划书撰写系统 - 命令行接口
"""

import argparse
import sys
from pathlib import Path
from business_plan_writer import BusinessPlanWriter, DocxBuilder


def init_command(args):
    """初始化项目命令"""
    print("=" * 60)
    print("初始化商业计划书项目")
    print("=" * 60)

    writer = BusinessPlanWriter(args.outline)

    # 创建项目信息
    project_info = writer.create_project_info(
        product_name=args.product,
        company_name=args.company,
        project_description=args.desc
    )

    # 生成内容计划
    content_plan = writer.generate_content_plan(project_info)

    # 保存内容计划
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    plan_path = output_dir / "content_plan.json"
    writer.save_content_plan(content_plan, str(plan_path))

    print(f"\n✅ 项目初始化完成！")
    print(f"📁 内容计划: {plan_path}")
    print(f"\n下一步:")
    print(f"  1. 编辑 {plan_path}，根据每个章节的提示词撰写内容")
    print(f"  2. 将撰写好的内容填入 'generated_content' 字段")
    print(f"  3. 运行 'build' 命令生成 Word 文档")


def build_command(args):
    """构建文档命令"""
    print("=" * 60)
    print("构建商业计划书 Word 文档")
    print("=" * 60)

    writer = BusinessPlanWriter()
    builder = DocxBuilder()

    # 加载内容计划
    content_plan = writer.load_content_plan(args.input)

    # 构建文档
    output_path = args.output
    builder.build_document(content_plan, output_path)

    print(f"\n✅ 文档构建完成！")
    print(f"📄 输出文档: {output_path}")


def info_command(args):
    """查看大纲信息"""
    writer = BusinessPlanWriter(args.outline)
    outline = writer.outline

    print("=" * 60)
    print("商业计划书大纲信息")
    print("=" * 60)
    print(f"模板名称: {outline.get('template_name', '未知')}")
    print(f"章节总数: {outline.get('total_sections', 0)}")
    print("\n章节列表:")
    print("-" * 60)

    sections = outline.get("sections", [])
    for i, sec in enumerate(sections, 1):
        title = sec.get("title", "无标题")
        level = sec.get("level", 2)
        needs_chart = "📊" if sec.get("needs_chart") else "  "
        print(f"{needs_chart} {i:2d}. [Heading{level}] {title}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="商业计划书撰写系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 初始化一个新项目
  python cli.py init --product "智链供应链" --company "武汉智链科技" --desc "AI供应链平台"

  # 查看大纲信息
  python cli.py info

  # 构建Word文档
  python cli.py build --input output/content_plan.json --output business_plan.docx
        """
    )

    subparsers = parser.add_subparsers(title="命令", dest="command")

    # init 命令
    parser_init = subparsers.add_parser("init", help="初始化新项目")
    parser_init.add_argument("--product", "-p", required=True, help="项目/产品名称")
    parser_init.add_argument("--company", "-c", required=True, help="公司名称")
    parser_init.add_argument("--desc", "-d", default="", help="项目描述")
    parser_init.add_argument("--output", "-o", default="output", help="输出目录 (默认: output)")
    parser_init.add_argument("--outline", help="大纲文件路径 (可选)")

    # build 命令
    parser_build = subparsers.add_parser("build", help="构建Word文档")
    parser_build.add_argument("--input", "-i", required=True, help="内容计划JSON文件")
    parser_build.add_argument("--output", "-o", required=True, help="输出Word文档路径")

    # info 命令
    parser_info = subparsers.add_parser("info", help="查看大纲信息")
    parser_info.add_argument("--outline", help="大纲文件路径 (可选)")

    args = parser.parse_args()

    if args.command == "init":
        init_command(args)
    elif args.command == "build":
        build_command(args)
    elif args.command == "info":
        info_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
