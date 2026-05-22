#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path

# 读取内容
content = json.loads(Path("content_all_merged.json").read_text(encoding="utf-8"))
sections = content["sections"]

# 收集图片池
image_pool = []

# 1. 产品截图
manifest_path = Path("C:/Users/lauze/.claude/skills/business-plan-writer/assets/product-screenshots-run/manifest.json")
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for item in manifest:
        image_pool.append({
            "path": item["path"],
            "width": "15cm",
            "caption": item.get("description", "产品截图")
        })

# 2. 学术配图 + matplotlib图表
academic_dir = Path("academic_diagrams_run")
for img_file in ["swot.png", "architecture.png", "gantt.png", "value_chain.png", "competition.png", "bmc.png"]:
    p = academic_dir / img_file
    if p.exists():
        image_pool.append({
            "path": str(p.resolve()),
            "width": "15cm",
            "caption": img_file.replace(".png", "")
        })

print(f"Total images in pool: {len(image_pool)}")

# 读取财务数据
profit_data = json.loads(Path("run_profit_output.json").read_text(encoding="utf-8"))
cash_data = json.loads(Path("run_cash_output.json").read_text(encoding="utf-8"))
balance_data = json.loads(Path("run_balance_output.json").read_text(encoding="utf-8"))

# 分配图片到章节
img_idx = 0
for sec in sections:
    sid = sec["id"]
    stype = sec.get("type", "generated")
    title = sec.get("title", "")
    
    # table章节插入财务数据
    if stype == "table":
        if "利润" in title:
            sec["table_data"] = profit_data.get("data", [])
        elif "现金" in title:
            sec["table_data"] = cash_data.get("data", [])
        elif "资产" in title or "负债" in title or "负债表" in title:
            sec["table_data"] = balance_data.get("data", [])
        sec["level"] = sec.get("level", 3)
        continue
    
    # 为generated章节分配图片
    if stype == "generated":
        sec["level"] = sec.get("level", 2)
        # 计算段落数
        text = sec.get("content", "")
        paras = [p for p in str(text).split("\n") if p.strip()]
        # 每2段1张图，最多分配3张
        max_imgs = min(3, max(1, len(paras) // 2))
        # 某些重点章节多分配
        if any(k in title for k in ["产品", "技术", "市场", "商业", "运营", "风险", "价值"]):
            max_imgs = min(4, max_imgs + 1)
        
        assigned = []
        for _ in range(max_imgs):
            if img_idx < len(image_pool):
                assigned.append(image_pool[img_idx])
                img_idx += 1
            else:
                assigned.append(image_pool[img_idx % len(image_pool)])
                img_idx += 1
        sec["embedded_images"] = assigned

# 保存最终内容
Path("content_final.json").write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Prepared final content with {len(sections)} sections -> content_final.json")
print(f"Total images used/assigned: {img_idx}")
