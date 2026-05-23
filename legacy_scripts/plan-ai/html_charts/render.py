#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML图表渲染器 - 使用Playwright将HTML字符串截图成PNG
"""
import os
import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE = Path(r"D:\计划书AI\html_charts")
OUTPUT = Path(r"D:\计划书AI\output_v2\images")

# 每个项目的配色方案 (CSS gradient + accent colors)
PROJECT_THEMES = {
    "cloud_ai": {
        "bg": "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
        "card": "rgba(255,255,255,0.08)",
        "card_border": "rgba(255,255,255,0.15)",
        "text": "#e0e0e0",
        "title": "#ffffff",
        "accent1": "#00d4ff", "accent2": "#7b2cbf", "accent3": "#ff006e",
        "accent4": "#fb5607", "accent5": "#ffbe0b", "accent6": "#8338ec",
    },
    "autonomous_driving": {
        "bg": "linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)",
        "card": "rgba(255,255,255,0.07)",
        "card_border": "rgba(255,255,255,0.12)",
        "text": "#e0e0e0",
        "title": "#ffffff",
        "accent1": "#00f5ff", "accent2": "#ff2e63", "accent3": "#08d9d6",
        "accent4": "#eaeaea", "accent5": "#ff9a3c", "accent6": "#30e3ca",
    },
    "industrial_ai": {
        "bg": "linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #1e3c72 100%)",
        "card": "rgba(255,255,255,0.09)",
        "card_border": "rgba(255,255,255,0.18)",
        "text": "#f0f0f0",
        "title": "#ffffff",
        "accent1": "#ff6b6b", "accent2": "#4ecdc4", "accent3": "#45b7d1",
        "accent4": "#96ceb4", "accent5": "#ffeaa7", "accent6": "#dfe6e9",
    },
    "energy_storage": {
        "bg": "linear-gradient(135deg, #134e5e 0%, #71b280 100%)",
        "card": "rgba(255,255,255,0.1)",
        "card_border": "rgba(255,255,255,0.2)",
        "text": "#f0f0f0",
        "title": "#ffffff",
        "accent1": "#00b894", "accent2": "#fdcb6e", "accent3": "#e17055",
        "accent4": "#74b9ff", "accent5": "#a29bfe", "accent6": "#55efc4",
    },
    "ecommerce_retail": {
        "bg": "linear-gradient(135deg, #2d3436 0%, #636e72 50%, #2d3436 100%)",
        "card": "rgba(255,255,255,0.08)",
        "card_border": "rgba(255,255,255,0.15)",
        "text": "#dfe6e9",
        "title": "#ffffff",
        "accent1": "#ff7675", "accent2": "#fd79a8", "accent3": "#fdcb6e",
        "accent4": "#6c5ce7", "accent5": "#00b894", "accent6": "#e17055",
    },
    "healthcare": {
        "bg": "linear-gradient(135deg, #1a5276 0%, #2874a6 50%, #3498db 100%)",
        "card": "rgba(255,255,255,0.1)",
        "card_border": "rgba(255,255,255,0.2)",
        "text": "#ecf0f1",
        "title": "#ffffff",
        "accent1": "#e74c3c", "accent2": "#2ecc71", "accent3": "#f39c12",
        "accent4": "#9b59b6", "accent5": "#1abc9c", "accent6": "#3498db",
    },
    "security": {
        "bg": "linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 50%, #2d2d2d 100%)",
        "card": "rgba(255,255,255,0.05)",
        "card_border": "rgba(255,255,255,0.1)",
        "text": "#b2bec3",
        "title": "#ffffff",
        "accent1": "#00cec9", "accent2": "#fd79a8", "accent3": "#ffeaa7",
        "accent4": "#0984e3", "accent5": "#6c5ce7", "accent6": "#e84393",
    },
    "media_entertainment": {
        "bg": "linear-gradient(135deg, #2c003e 0%, #512b58 50%, #900c3f 100%)",
        "card": "rgba(255,255,255,0.08)",
        "card_border": "rgba(255,255,255,0.15)",
        "text": "#e0e0e0",
        "title": "#ffffff",
        "accent1": "#ff00cc", "accent2": "#3333ff", "accent3": "#00ffcc",
        "accent4": "#ff0066", "accent5": "#ccff00", "accent6": "#ff6600",
    },
    "data_analytics": {
        "bg": "linear-gradient(135deg, #141e30 0%, #243b55 100%)",
        "card": "rgba(255,255,255,0.07)",
        "card_border": "rgba(255,255,255,0.14)",
        "text": "#dcdde1",
        "title": "#ffffff",
        "accent1": "#44bd32", "accent2": "#e1b12c", "accent3": "#c23616",
        "accent4": "#8c7ae6", "accent5": "#00a8ff", "accent6": "#9c88ff",
    },
    "accessibility": {
        "bg": "linear-gradient(135deg, #3d5a80 0%, #98c1d9 100%)",
        "card": "rgba(255,255,255,0.12)",
        "card_border": "rgba(255,255,255,0.25)",
        "text": "#2d3436",
        "title": "#2d3436",
        "accent1": "#e63946", "accent2": "#f1faee", "accent3": "#a8dadc",
        "accent4": "#457b9d", "accent5": "#1d3557", "accent6": "#e9c46a",
    },
    "semiconductor": {
        "bg": "linear-gradient(135deg, #1b1b2f 0%, #162447 50%, #1f4068 100%)",
        "card": "rgba(255,255,255,0.06)",
        "card_border": "rgba(255,255,255,0.12)",
        "text": "#dcdde1",
        "title": "#ffffff",
        "accent1": "#f5f6fa", "accent2": "#7f8fa6", "accent3": "#273c75",
        "accent4": "#44bd32", "accent5": "#e1b12c", "accent6": "#8c7ae6",
    },
    "recycling": {
        "bg": "linear-gradient(135deg, #2d4a3e 0%, #5a7d5a 50%, #8fbc8f 100%)",
        "card": "rgba(255,255,255,0.1)",
        "card_border": "rgba(255,255,255,0.2)",
        "text": "#f5f6fa",
        "title": "#ffffff",
        "accent1": "#27ae60", "accent2": "#f39c12", "accent3": "#e74c3c",
        "accent4": "#3498db", "accent5": "#9b59b6", "accent6": "#1abc9c",
    },
    "satellite_comm": {
        "bg": "linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)",
        "card": "rgba(255,255,255,0.05)",
        "card_border": "rgba(255,255,255,0.1)",
        "text": "#dcdde1",
        "title": "#ffffff",
        "accent1": "#00cec9", "accent2": "#fdcb6e", "accent3": "#74b9ff",
        "accent4": "#a29bfe", "accent5": "#55efc4", "accent6": "#ff7675",
    },
    "urban_heritage": {
        "bg": "linear-gradient(135deg, #5d4037 0%, #8d6e63 50%, #bcaaa4 100%)",
        "card": "rgba(255,255,255,0.12)",
        "card_border": "rgba(255,255,255,0.25)",
        "text": "#3e2723",
        "title": "#3e2723",
        "accent1": "#d84315", "accent2": "#ff8f00", "accent3": "#ffb300",
        "accent4": "#c0ca33", "accent5": "#7cb342", "accent6": "#00897b",
    },
    "pet_tech": {
        "bg": "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
        "card": "rgba(255,255,255,0.3)",
        "card_border": "rgba(255,255,255,0.5)",
        "text": "#5d4037",
        "title": "#3e2723",
        "accent1": "#ff6b6b", "accent2": "#4ecdc4", "accent3": "#45b7d1",
        "accent4": "#f9ca24", "accent5": "#6c5ce7", "accent6": "#a29bfe",
    },
}


def get_theme(category):
    return PROJECT_THEMES.get(category, PROJECT_THEMES["cloud_ai"])


async def render_html_to_png(html_content, output_path, width=1920, height=1080):
    """使用Playwright将HTML字符串渲染为PNG"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": height})
        await page.set_content(html_content)
        await page.screenshot(path=str(output_path), full_page=False)
        await browser.close()


def wrap_html(body_content, theme, title="", mode="chart"):
    """包装HTML页面，添加统一样式
    mode="chart": 白色背景，用于普通图表
    mode="screenshot": 深色背景，用于产品前端截图
    """
    accents = [theme["accent1"], theme["accent2"], theme["accent3"],
               theme["accent4"], theme["accent5"], theme["accent6"]]
    accent_css = "\n".join([f"      --accent{i+1}: {accents[i]};" for i in range(6)])

    if mode == "screenshot":
        # 深色模式 - 产品截图
        bg = theme["bg"]
        text_color = theme["text"]
        title_color = theme["title"]
        card_bg = theme["card"]
        card_border = theme["card_border"]
        shadow = "0 8px 32px rgba(0,0,0,0.15)"
        text_shadow = "text-shadow: 0 2px 10px rgba(0,0,0,0.3);"
        backdrop = "backdrop-filter: blur(10px);"
    else:
        # 白色模式 - 普通图表
        bg = "#ffffff"
        text_color = "#333333"
        title_color = "#1a1a1a"
        card_bg = "#f5f5f5"
        card_border = "#e0e0e0"
        shadow = "0 4px 12px rgba(0,0,0,0.08)"
        text_shadow = ""
        backdrop = ""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        width: 1920px;
        height: 1080px;
        background: {bg};
        color: {text_color};
        font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        padding: 40px 60px;
    }}
    :root {{
        --bg: {bg};
        --card: {card_bg};
        --card-border: {card_border};
        --text: {text_color};
        --title: {title_color};
{accent_css}
    }}
    .header {{
        font-size: 42px;
        font-weight: bold;
        color: var(--title);
        margin-bottom: 30px;
        padding-bottom: 15px;
        border-bottom: 3px solid var(--accent1);
        {text_shadow}
    }}
    .card {{
        background: var(--card);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 20px 24px;
        {backdrop}
        box-shadow: {shadow};
        transition: transform 0.3s;
    }}
    .card:hover {{ transform: translateY(-2px); }}
    .accent-1 {{ border-left: 4px solid var(--accent1); }}
    .accent-2 {{ border-left: 4px solid var(--accent2); }}
    .accent-3 {{ border-left: 4px solid var(--accent3); }}
    .accent-4 {{ border-left: 4px solid var(--accent4); }}
    .accent-5 {{ border-left: 4px solid var(--accent5); }}
    .accent-6 {{ border-left: 4px solid var(--accent6); }}
    .grid {{ display: grid; gap: 20px; }}
    .flex {{ display: flex; gap: 20px; }}
    .flex-col {{ flex-direction: column; }}
    .flex-wrap {{ flex-wrap: wrap; }}
    .text-center {{ text-align: center; }}
    .font-bold {{ font-weight: bold; }}
    .text-lg {{ font-size: 24px; }}
    .text-xl {{ font-size: 28px; }}
    .text-2xl {{ font-size: 32px; }}
    .text-sm {{ font-size: 18px; }}
    .text-xs {{ font-size: 16px; }}
    .mt-2 {{ margin-top: 10px; }}
    .mt-4 {{ margin-top: 20px; }}
    .p-2 {{ padding: 10px; }}
    .p-4 {{ padding: 20px; }}
    .flex-1 {{ flex: 1; }}
    .items-center {{ align-items: center; }}
    .justify-center {{ justify-content: center; }}
</style>
</head>
<body>
{body_content}
</body>
</html>"""
