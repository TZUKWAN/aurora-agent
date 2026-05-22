#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML图表生成主脚本
为49个项目生成所有HTML图表并截图
"""
import asyncio
import json
import time
from pathlib import Path
from playwright.async_api import async_playwright
from render import get_theme, wrap_html
from charts import CHART_FUNCTIONS, FIG_TO_FILENAME

BASE = Path(r"D:\计划书AI")
DATA_DIR = BASE / "pptx_charts" / "project_data"
OUTPUT = BASE / "output_v2" / "images"

# 项目分类映射（必须与generate_project_data.py一致）
PROJECT_CATEGORIES = {
    "云跃引擎": "cloud_ai", "智测先锋": "cloud_ai", "智构视界": "cloud_ai", "智绘经纬": "cloud_ai", "数源织机": "cloud_ai",
    "元界智驾": "autonomous_driving", "元驾驭域": "autonomous_driving",
    "具身智造": "industrial_ai", "孪生幻影": "industrial_ai", "智灵视界": "industrial_ai", "极光智检": "industrial_ai", "探微神算": "industrial_ai",
    "储能先知": "energy_storage", "拆解先知": "energy_storage", "绿网调音师": "energy_storage",
    "刺客雷达": "ecommerce_retail", "幻图智算": "ecommerce_retail", "星播智云": "ecommerce_retail", "烟火算盘": "ecommerce_retail", "质感寻源": "ecommerce_retail", "闲光变现": "ecommerce_retail",
    "心流源核": "healthcare", "银发智绘": "healthcare", "药界神农": "healthcare", "喵星食域": "healthcare",
    "影刃识微": "security", "智防深渊": "security", "证链智核": "security",
    "声境幻造": "media_entertainment", "影生万物": "media_entertainment", "视界文枢": "media_entertainment", "语境塑形": "media_entertainment", "群演矩阵": "media_entertainment", "幻视造物": "media_entertainment",
    "数语探微": "data_analytics", "息流洞见": "data_analytics", "知渊图谱": "data_analytics", "商弈智境": "data_analytics",
    "盲域星图": "accessibility", "银发译林": "accessibility", "盲盒公交": "accessibility",
    "芯流智核": "semiconductor", "芯脉智连": "semiconductor",
    "冶金回响": "recycling",
    "星轨卫士": "satellite_comm",
    "聚落寻根": "urban_heritage", "岁月留声": "urban_heritage",
    "宠心译语": "pet_tech",
}


async def generate_project(page, project, output_dir):
    """为单个项目生成所有HTML图表"""
    name = project["name"]
    idx = project["idx"]
    category = PROJECT_CATEGORIES.get(name, "cloud_ai")
    theme = get_theme(category)

    data_path = DATA_DIR / f"p{idx}_{name}.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))

    generated = 0
    for fig_key, func in CHART_FUNCTIONS.items():
        filename = FIG_TO_FILENAME[fig_key]
        out_path = output_dir / filename
        if out_path.exists() and out_path.stat().st_size > 1000:
            generated += 1
            continue

        try:
            body = func(data, theme)
            mode = "screenshot" if fig_key in ("图2-7", "图2-8", "图2-9", "图2-10", "图2-14") else "chart"
            html = wrap_html(body, theme, f"{name} · {fig_key}", mode=mode)
            await page.set_content(html)
            await page.screenshot(path=str(out_path), full_page=False)
            generated += 1
        except Exception as e:
            print(f"    ERROR {name} {fig_key}: {e}")

    return generated


async def main():
    projects = json.loads((BASE / "output_v2" / "projects_list.json").read_text(encoding="utf-8"))
    total = len(projects)

    print(f"开始生成 {total} 个项目的HTML图表...")
    t0 = time.time()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})

        for i, project in enumerate(projects):
            img_dir = OUTPUT / f"p{project['idx']}"
            img_dir.mkdir(parents=True, exist_ok=True)

            t1 = time.time()
            count = await generate_project(page, project, img_dir)
            elapsed = time.time() - t1
            print(f"[{i+1}/{total}] {project['name']}: {count}张生成 ({elapsed:.1f}s)")

        await browser.close()

    total_elapsed = time.time() - t0
    print(f"\n全部完成! 耗时 {total_elapsed:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
