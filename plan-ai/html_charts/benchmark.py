#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Benchmark Playwright screenshot speed"""
import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright

async def benchmark():
    html = """<!DOCTYPE html>
<html><body style="width:1920px;height:1080px;background:linear-gradient(135deg,#1a1a2e,#16213e);display:flex;align-items:center;justify:center;">
<div style="color:white;font-size:60px;font-family:sans-serif;">Test Chart</div>
</body></html>"""

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})

        t0 = time.time()
        count = 10
        for i in range(count):
            await page.set_content(html)
            await page.screenshot(path=f"D:/计划书AI/html_charts/test_{i}.png")
        elapsed = time.time() - t0
        print(f"{count} screenshots in {elapsed:.1f}s = {elapsed/count:.2f}s each")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(benchmark())
