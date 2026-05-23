#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manual chart renderer - renders a single HTML file to PNG
Usage: python manual_render.py <html_file> <output_png>
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

def render(html_path, png_path, width=1920, height=1080):
    html = Path(html_path).read_text(encoding='utf-8')
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        page.set_content(html)
        page.wait_for_timeout(500)
        page.screenshot(path=str(png_path), full_page=False)
        browser.close()
    print(f"Rendered: {png_path}")

if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
