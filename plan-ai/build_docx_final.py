#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_docx.py
读取 content.json，用 officecli 批量组装成 .docx 文件。
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_officecli(args: list) -> None:
    cmd = ["officecli"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        err = result.stderr or ""
        # 若 create 失败因为文件被 resident 锁定，先尝试 close 再重试一次
        if args[0] == "create" and "opened by a resident process" in err:
            file_arg = args[1]
            subprocess.run(["officecli", "close", file_arg], capture_output=True, text=True, encoding="utf-8")
            result2 = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
            if result2.returncode == 0:
                return
        print(f"OfficeCLI 错误: {err}", file=sys.stderr)
        raise RuntimeError(f"officecli {' '.join(args)} failed")


def build_batch_commands(content: dict) -> list:
    commands = []
    sections = content.get("sections", [])

    for sec in sections:
        title = sec.get("title", "")
        level = sec.get("level", 2)
        sec_type = sec.get("type", "generated")

        # 标题样式映射
        style_map = {0: "Normal", 1: "Heading1", 2: "Heading2", 3: "Heading3", 4: "Heading4"}
        heading_style = style_map.get(level, "Heading2")

        # 添加标题（如果有）
        if title:
            commands.append({
                "op": "add",
                "parent": "/body",
                "type": "paragraph",
                "props": {"text": title, "style": heading_style}
            })

        # 处理表格类型
        if sec_type == "table" and sec.get("table_data"):
            table = sec["table_data"]
            if not table:
                continue
            rows = len(table)
            cols = max(len(r) for r in table) if table else 1
            # 添加表格
            commands.append({
                "op": "add",
                "parent": "/body",
                "type": "table",
                "props": {"rows": rows, "cols": cols}
            })
            # 填充单元格（表格索引从1开始，作为body的最后一个子元素）
            table_path = f"/body/tbl[last()]"
            for r_idx, row in enumerate(table):
                for c_idx, val in enumerate(row):
                    cell_path = f"{table_path}/tr[{r_idx+1}]/tc[{c_idx+1}]"
                    commands.append({
                        "op": "set",
                        "path": cell_path,
                        "props": {"text": str(val)}
                    })
        elif sec_type == "table" and sec.get("table_skeleton") and sec.get("table_skeleton").get("data"):
            # 如果table_data不存在，尝试table_skeleton.data
            table = sec["table_skeleton"]["data"]
            rows = len(table)
            cols = max(len(r) for r in table) if table else 1
            commands.append({
                "op": "add",
                "parent": "/body",
                "type": "table",
                "props": {"rows": rows, "cols": cols}
            })
            table_path = f"/body/tbl[last()]"
            for r_idx, row in enumerate(table):
                for c_idx, val in enumerate(row):
                    cell_path = f"{table_path}/tr[{r_idx+1}]/tc[{c_idx+1}]"
                    commands.append({
                        "op": "set",
                        "path": cell_path,
                        "props": {"text": str(val)}
                    })

        # 添加正文内容
        text_content = ""
        if sec.get("generated_content"):
            text_content = sec["generated_content"]
        elif sec.get("content"):
            text_content = sec["content"]
        elif sec.get("prompt"):
            text_content = sec["prompt"]
        elif sec.get("fixed_text"):
            text_content = sec["fixed_text"]

        if text_content and sec_type != "table":
            # 按段落拆分
            for para in str(text_content).split("\n"):
                para = para.strip()
                if para:
                    commands.append({
                        "op": "add",
                        "parent": "/body",
                        "type": "paragraph",
                        "props": {"text": para, "style": "Normal"}
                    })

        # 添加图片
        if sec.get("needs_chart") and sec.get("chart_type", "").endswith("_png") and sec.get("chart_path"):
            commands.append({
                "op": "add",
                "parent": "/body",
                "type": "image",
                "props": {"path": sec["chart_path"], "width": "15cm"}
            })

    return commands


def main():
    parser = argparse.ArgumentParser(description="根据 content.json 生成 Word 文档")
    parser.add_argument("--content", required=True, help="content.json 路径")
    parser.add_argument("--output", required=True, help="输出 .docx 路径")
    args = parser.parse_args()

    content_path = Path(args.content)
    output_path = Path(args.output)

    content = json.loads(content_path.read_text(encoding="utf-8"))
    commands = build_batch_commands(content)

    if not commands:
        print("警告：没有可写入的内容")
        return

    # 创建空白文档
    run_officecli(["create", str(output_path)])

    # 开启常驻模式
    run_officecli(["open", str(output_path)])

    try:
        # 由于 batch 可能很长，分块执行（每批最多 100 条，避免 resident 死锁）
        chunk_size = 100
        for i in range(0, len(commands), chunk_size):
            chunk = commands[i:i+chunk_size]
            print(f"执行 batch chunk {i//chunk_size+1}/{(len(commands)-1)//chunk_size+1}，共 {len(chunk)} 条命令")
            proc = subprocess.run(
                ["officecli", "batch", str(output_path), "--json"],
                input=json.dumps(chunk, ensure_ascii=False),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=30
            )
            print(f"chunk {i//chunk_size+1} 完成，returncode={proc.returncode}")
            if proc.returncode != 0:
                print(f"Batch 错误 (chunk {i//chunk_size+1}): {proc.stderr}", file=sys.stderr)
                # 继续执行后续 chunk，不中断
    finally:
        # 关闭并保存
        print("关闭 resident 模式并保存...")
        run_officecli(["close", str(output_path)])

    print(f"文档生成完成：{output_path.resolve()}")


if __name__ == "__main__":
    main()
