"""Chart generation using pure SVG - no external dependencies, no LLM calls."""

import math
from typing import Dict, List, Optional


# Professional color palette (blues, grays, accent)
DEFAULT_COLORS = [
    "#2563EB",  # blue-600
    "#3B82F6",  # blue-500
    "#60A5FA",  # blue-400
    "#93C5FD",  # blue-300
    "#1E40AF",  # blue-800
    "#1D4ED8",  # blue-700
    "#6366F1",  # indigo-500
    "#818CF8",  # indigo-400
    "#A5B4FC",  # indigo-300
    "#6B7280",  # gray-500
]

ACCENT_COLORS = [
    "#2563EB", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6",
    "#EC4899", "#14B8A6", "#F97316", "#06B6D4", "#84CC16",
]


class ChartGenerator:
    """Generate self-contained HTML chart components with inline SVG."""

    def __init__(self, colors: Optional[List[str]] = None):
        self.colors = colors or DEFAULT_COLORS

    def _base_html(self, title: str, body: str, width: int = 600, height: int = 400) -> str:
        """Wrap chart body in a self-contained HTML document."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #F9FAFB; padding: 24px; }}
  .chart-container {{ background: #FFFFFF; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 32px; max-width: {width + 64}px; }}
  .chart-title {{ font-size: 20px; font-weight: 600; color: #111827; margin-bottom: 24px; text-align: center; }}
</style>
</head>
<body>
<div class="chart-container">
  <div class="chart-title">{title}</div>
  {body}
</div>
</body>
</html>"""

    def generate_bar_chart(self, data: dict, title: str, options: dict = None) -> str:
        """Generate a bar chart as self-contained HTML with inline SVG.

        Args:
            data: {"labels": [...], "values": [...]}
            title: Chart title
            options: Optional dict with width, height, colors, show_legend, bar_width, etc.

        Returns:
            Complete HTML string.
        """
        opts = options or {}
        width = opts.get("width", 600)
        height = opts.get("height", 400)
        colors = opts.get("colors", self.colors)
        show_legend = opts.get("show_legend", True)
        bar_width_pct = opts.get("bar_width", 0.6)

        labels = data.get("labels", [])
        values = data.get("values", [])

        if not labels or not values:
            return self._base_html(title, "<p>No data provided</p>", width, height)

        max_val = max(values) if values else 1
        if max_val == 0:
            max_val = 1

        n = len(labels)
        # Chart area dimensions
        pad_left = 60
        pad_right = 30
        pad_top = 10
        pad_bottom = 60
        chart_w = width - pad_left - pad_right
        chart_h = height - pad_top - pad_bottom

        bar_group_w = chart_w / n
        bar_w = bar_group_w * bar_width_pct
        bar_offset = (bar_group_w - bar_w) / 2

        svg_parts = []

        # Grid lines
        num_grid = 5
        for i in range(num_grid + 1):
            y = pad_top + chart_h - (chart_h * i / num_grid)
            val = max_val * i / num_grid
            svg_parts.append(
                f'<line x1="{pad_left}" y1="{y}" x2="{width - pad_right}" y2="{y}" '
                f'stroke="#E5E7EB" stroke-width="1"/>'
            )
            svg_parts.append(
                f'<text x="{pad_left - 8}" y="{y + 4}" text-anchor="end" '
                f'fill="#6B7280" font-size="12">{val:.0f}</text>'
            )

        # Bars
        for i, (label, value) in enumerate(zip(labels, values)):
            x = pad_left + i * bar_group_w + bar_offset
            bar_h = (value / max_val) * chart_h if max_val > 0 else 0
            y = pad_top + chart_h - bar_h
            color = colors[i % len(colors)]

            svg_parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" '
                f'fill="{color}" rx="4" ry="4"/>'
            )
            # Value label on top of bar
            svg_parts.append(
                f'<text x="{x + bar_w / 2:.1f}" y="{y - 6:.1f}" text-anchor="middle" '
                f'fill="#374151" font-size="13" font-weight="600">{value}</text>'
            )
            # Category label below
            svg_parts.append(
                f'<text x="{x + bar_w / 2:.1f}" y="{pad_top + chart_h + 20:.1f}" '
                f'text-anchor="middle" fill="#6B7280" font-size="12">{label}</text>'
            )

        # Legend
        if show_legend and n <= 10:
            legend_x = pad_left
            legend_y = height - 16
            for i, label in enumerate(labels):
                lx = legend_x + i * (chart_w / n)
                svg_parts.append(
                    f'<rect x="{lx:.1f}" y="{legend_y:.1f}" width="10" height="10" '
                    f'fill="{colors[i % len(colors)]}" rx="2"/>'
                )
                svg_parts.append(
                    f'<text x="{lx + 14:.1f}" y="{legend_y + 9:.1f}" '
                    f'fill="#4B5563" font-size="11">{label}</text>'
                )

        svg = (
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
            + "".join(svg_parts)
            + "</svg>"
        )
        return self._base_html(title, svg, width, height)

    def generate_pie_chart(self, data: dict, title: str, options: dict = None) -> str:
        """Generate a pie/donut chart as self-contained HTML with inline SVG.

        Args:
            data: {"labels": [...], "values": [...]}
            title: Chart title
            options: Optional dict with width, height, colors, show_legend, donut (bool), etc.

        Returns:
            Complete HTML string.
        """
        opts = options or {}
        width = opts.get("width", 500)
        height = opts.get("height", 420)
        colors = opts.get("colors", ACCENT_COLORS)
        show_legend = opts.get("show_legend", True)
        donut = opts.get("donut", False)
        donut_radius = opts.get("donut_radius", 50)

        labels = data.get("labels", [])
        values = data.get("values", [])

        if not labels or not values:
            return self._base_html(title, "<p>No data provided</p>", width, height)

        total = sum(values)
        if total == 0:
            return self._base_html(title, "<p>No data provided</p>", width, height)

        cx = width // 2
        cy = 190
        r = 140
        svg_parts = []

        start_angle = -math.pi / 2  # start at top

        for i, (label, value) in enumerate(zip(labels, values)):
            fraction = value / total
            sweep_angle = fraction * 2 * math.pi
            end_angle = start_angle + sweep_angle

            x1 = cx + r * math.cos(start_angle)
            y1 = cy + r * math.sin(start_angle)
            x2 = cx + r * math.cos(end_angle)
            y2 = cy + r * math.sin(end_angle)

            large_arc = 1 if sweep_angle > math.pi else 0
            color = colors[i % len(colors)]

            if donut:
                inner_r = donut_radius
                ix1 = cx + inner_r * math.cos(end_angle)
                iy1 = cy + inner_r * math.sin(end_angle)
                ix2 = cx + inner_r * math.cos(start_angle)
                iy2 = cy + inner_r * math.sin(start_angle)

                path = (
                    f'<path d="M {x1:.2f} {y1:.2f} '
                    f'A {r} {r} 0 {large_arc} 1 {x2:.2f} {y2:.2f} '
                    f'L {ix1:.2f} {iy1:.2f} '
                    f'A {inner_r} {inner_r} 0 {large_arc} 0 {ix2:.2f} {iy2:.2f} Z" '
                    f'fill="{color}" stroke="#FFFFFF" stroke-width="2"/>'
                )
            else:
                path = (
                    f'<path d="M {cx} {cy} '
                    f'L {x1:.2f} {y1:.2f} '
                    f'A {r} {r} 0 {large_arc} 1 {x2:.2f} {y2:.2f} Z" '
                    f'fill="{color}" stroke="#FFFFFF" stroke-width="2"/>'
                )
            svg_parts.append(path)

            # Label line
            mid_angle = start_angle + sweep_angle / 2
            label_r = r + 24
            lx = cx + label_r * math.cos(mid_angle)
            ly = cy + label_r * math.sin(mid_angle)
            pct = fraction * 100
            svg_parts.append(
                f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
                f'fill="#374151" font-size="12" font-weight="500">{pct:.1f}%</text>'
            )

            start_angle = end_angle

        # Donut center text
        if donut:
            svg_parts.append(
                f'<text x="{cx}" y="{cy - 6}" text-anchor="middle" '
                f'fill="#111827" font-size="22" font-weight="700">{total}</text>'
            )
            svg_parts.append(
                f'<text x="{cx}" y="{cy + 14}" text-anchor="middle" '
                f'fill="#6B7280" font-size="12">Total</text>'
            )

        # Legend below
        if show_legend:
            legend_y = cy + r + 40
            cols = min(len(labels), 3)
            col_w = width / cols
            for i, label in enumerate(labels):
                row = i // cols
                col = i % cols
                lx = col * col_w + 20
                ly = legend_y + row * 22
                pct = (values[i] / total) * 100
                svg_parts.append(
                    f'<rect x="{lx:.1f}" y="{ly - 8:.1f}" width="12" height="12" '
                    f'fill="{colors[i % len(colors)]}" rx="2"/>'
                )
                svg_parts.append(
                    f'<text x="{lx + 16:.1f}" y="{ly + 2:.1f}" '
                    f'fill="#374151" font-size="12">{label} ({pct:.1f}%)</text>'
                )

        svg = (
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
            + "".join(svg_parts)
            + "</svg>"
        )
        return self._base_html(title, svg, width, height)

    def generate_line_chart(self, data: dict, title: str, options: dict = None) -> str:
        """Generate a line chart as self-contained HTML with inline SVG.

        Args:
            data: {"labels": [...], "series": [{"name": "...", "values": [...]}]}
            title: Chart title
            options: Optional dict with width, height, colors, show_legend, show_dots, etc.

        Returns:
            Complete HTML string.
        """
        opts = options or {}
        width = opts.get("width", 600)
        height = opts.get("height", 400)
        colors = opts.get("colors", ACCENT_COLORS)
        show_legend = opts.get("show_legend", True)
        show_dots = opts.get("show_dots", True)

        labels = data.get("labels", [])
        series_list = data.get("series", [])

        if not labels or not series_list:
            return self._base_html(title, "<p>No data provided</p>", width, height)

        # Find global max/min across all series
        all_values = []
        for s in series_list:
            all_values.extend(s.get("values", []))
        if not all_values:
            return self._base_html(title, "<p>No data provided</p>", width, height)

        max_val = max(all_values)
        min_val = min(all_values)
        # Add 10% padding
        val_range = max_val - min_val if max_val != min_val else max_val if max_val != 0 else 1
        y_min = max(0, min_val - val_range * 0.1)
        y_max = max_val + val_range * 0.1
        if y_max == y_min:
            y_max = y_min + 1

        pad_left = 60
        pad_right = 30
        pad_top = 20
        pad_bottom = 60
        chart_w = width - pad_left - pad_right
        chart_h = height - pad_top - pad_bottom
        n = len(labels)

        svg_parts = []

        # Grid lines
        num_grid = 5
        for i in range(num_grid + 1):
            y = pad_top + chart_h - (chart_h * i / num_grid)
            val = y_min + (y_max - y_min) * i / num_grid
            svg_parts.append(
                f'<line x1="{pad_left}" y1="{y}" x2="{width - pad_right}" y2="{y}" '
                f'stroke="#E5E7EB" stroke-width="1"/>'
            )
            svg_parts.append(
                f'<text x="{pad_left - 8}" y="{y + 4}" text-anchor="end" '
                f'fill="#6B7280" font-size="11">{val:.0f}</text>'
            )

        # X-axis labels
        for i, label in enumerate(labels):
            x = pad_left + (chart_w * i / (n - 1)) if n > 1 else pad_left + chart_w / 2
            svg_parts.append(
                f'<text x="{x:.1f}" y="{pad_top + chart_h + 24:.1f}" '
                f'text-anchor="middle" fill="#6B7280" font-size="12">{label}</text>'
            )

        # Series
        for si, series in enumerate(series_list):
            values = series.get("values", [])
            color = colors[si % len(colors)]
            points = []
            for i, v in enumerate(values):
                x = pad_left + (chart_w * i / (n - 1)) if n > 1 else pad_left + chart_w / 2
                y = pad_top + chart_h - ((v - y_min) / (y_max - y_min)) * chart_h
                points.append((x, y))

            # Area fill
            area_points = [(points[0][0], pad_top + chart_h)] + points + [(points[-1][0], pad_top + chart_h)]
            area_d = " ".join(f"L {x:.1f} {y:.1f}" for x, y in area_points)
            svg_parts.append(
                f'<path d="M {area_points[0][0]:.1f} {area_points[0][1]:.1f} {area_d}" '
                f'fill="{color}" fill-opacity="0.08" stroke="none"/>'
            )

            # Line
            line_d = " ".join(f"L {x:.1f} {y:.1f}" for x, y in points)
            svg_parts.append(
                f'<path d="M {points[0][0]:.1f} {points[0][1]:.1f} {line_d}" '
                f'fill="none" stroke="{color}" stroke-width="2.5" '
                f'stroke-linejoin="round" stroke-linecap="round"/>'
            )

            # Dots
            if show_dots:
                for x, y in points:
                    svg_parts.append(
                        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" '
                        f'fill="#FFFFFF" stroke="{color}" stroke-width="2.5"/>'
                    )

        # Legend
        if show_legend and series_list:
            legend_x = pad_left
            legend_y = height - 14
            for i, series in enumerate(series_list):
                lx = legend_x + i * 130
                color = colors[i % len(colors)]
                name = series.get("name", f"Series {i + 1}")
                svg_parts.append(
                    f'<line x1="{lx:.1f}" y1="{legend_y:.1f}" '
                    f'x2="{lx + 18:.1f}" y2="{legend_y:.1f}" '
                    f'stroke="{color}" stroke-width="3" stroke-linecap="round"/>'
                )
                svg_parts.append(
                    f'<text x="{lx + 24:.1f}" y="{legend_y + 4:.1f}" '
                    f'fill="#374151" font-size="12">{name}</text>'
                )

        svg = (
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
            + "".join(svg_parts)
            + "</svg>"
        )
        return self._base_html(title, svg, width, height)

    def generate_comparison_table(self, data: dict, title: str) -> str:
        """Generate a styled comparison table as self-contained HTML.

        Args:
            data: {"headers": [...], "rows": [[...], ...]}
            title: Table title

        Returns:
            Complete HTML string.
        """
        headers = data.get("headers", [])
        rows = data.get("rows", [])

        if not headers or not rows:
            return self._base_html(title, "<p>No data provided</p>", 600, 200)

        num_cols = len(headers)

        table_html = '<table style="width:100%;border-collapse:collapse;font-size:14px;">'

        # Header row
        table_html += "<tr>"
        for h in headers:
            table_html += (
                f'<th style="padding:12px 16px;background:#2563EB;color:#FFFFFF;'
                f'text-align:left;font-weight:600;border-bottom:2px solid #1D4ED8;'
                f'font-size:13px;letter-spacing:0.03em;">{h}</th>'
            )
        table_html += "</tr>"

        # Data rows
        for ri, row in enumerate(rows):
            bg = "#F9FAFB" if ri % 2 == 0 else "#FFFFFF"
            table_html += f'<tr style="background:{bg};">'
            for ci, cell in enumerate(row[:num_cols]):
                font_weight = "font-weight:600;" if ci == 0 else ""
                table_html += (
                    f'<td style="padding:10px 16px;border-bottom:1px solid #E5E7EB;'
                    f'color:#374151;{font_weight}">{cell}</td>'
                )
            table_html += "</tr>"

        table_html += "</table>"
        return self._base_html(title, table_html, 600, 200 + len(rows) * 40)

    def generate_kpi_card(self, metrics: list, title: str) -> str:
        """Generate KPI metric cards as self-contained HTML.

        Args:
            metrics: [{"label": "...", "value": "...", "change": "+X%"}, ...]
            title: Card section title

        Returns:
            Complete HTML string.
        """
        if not metrics:
            return self._base_html(title, "<p>No metrics provided</p>", 600, 200)

        n = len(metrics)
        # Use flex grid layout
        cols = min(n, 3)
        card_w = 170
        container_w = cols * (card_w + 20) + 40

        cards_html = '<div style="display:flex;flex-wrap:wrap;gap:16px;justify-content:center;">'
        for m in metrics:
            label = m.get("label", "")
            value = m.get("value", "")
            change = m.get("change", "")

            # Determine change color
            change_color = "#10B981"  # green
            if change.startswith("-"):
                change_color = "#EF4444"  # red
            elif not change or change == "0%" or change == "+0%":
                change_color = "#6B7280"  # gray

            change_html = ""
            if change:
                arrow = "+" if (change.startswith("+") or change[0:1].isdigit()) else ""
                display_change = change if change.startswith(("+", "-")) else f"+{change}"
                change_html = (
                    f'<div style="font-size:13px;color:{change_color};font-weight:500;'
                    f'margin-top:6px;">{display_change}</div>'
                )

            cards_html += (
                f'<div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:10px;'
                f'padding:20px 24px;min-width:{card_w}px;text-align:center;'
                f'box-shadow:0 1px 2px rgba(0,0,0,0.05);">'
                f'<div style="font-size:12px;color:#6B7280;text-transform:uppercase;'
                f'letter-spacing:0.05em;margin-bottom:8px;">{label}</div>'
                f'<div style="font-size:28px;font-weight:700;color:#111827;">{value}</div>'
                f'{change_html}'
                f"</div>"
            )
        cards_html += "</div>"

        return self._base_html(title, cards_html, container_w, 200)
