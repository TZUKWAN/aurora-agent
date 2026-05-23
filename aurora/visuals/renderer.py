"""Playwright-based renderer to convert HTML to high-res PNG."""

import os
import tempfile
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class HTMLRenderer:
    """Renders HTML strings to PNG images using Playwright."""

    def __init__(self):
        self.has_playwright = False
        try:
            from playwright.sync_api import sync_playwright
            self.sync_playwright = sync_playwright
            self.has_playwright = True
        except ImportError:
            logger.warning("Playwright not installed. Visual rendering disabled.")
            logger.warning("Run 'pip install playwright' and 'playwright install chromium'")

    def render_to_png(self, html_content: str, output_path: str, is_mobile: bool = False) -> bool:
        """
        Render HTML string to a PNG file.
        
        Args:
            html_content: The full HTML document string
            output_path: Where to save the PNG
            is_mobile: If True, uses a mobile viewport (e.g. 375x812)
        """
        if not self.has_playwright:
            return False

        # Create a temporary file to hold the HTML
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as f:
            f.write(html_content)
            temp_url = f"file://{os.path.abspath(f.name).replace(chr(92), '/')}"

        # Setup Playwright and capture screenshot
        try:
            with self.sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                
                if is_mobile:
                    viewport = {"width": 375, "height": 812}
                else:
                    # High resolution dashboard/chart viewport
                    viewport = {"width": 1280, "height": 800}
                    
                context = browser.new_context(viewport=viewport)
                page = context.new_page()
                
                # Load the local HTML file
                page.goto(temp_url, wait_until="networkidle")
                
                # Wait briefly for CSS/ECharts animations to settle
                page.wait_for_timeout(1500) 
                
                # Take full page screenshot
                page.screenshot(path=output_path, full_page=True)
                
                browser.close()
                return True
        except Exception as e:
            logger.error(f"Playwright rendering failed: {e}")
            return False
        finally:
            # Cleanup temp file
            try:
                os.unlink(f.name)
            except Exception:
                pass
