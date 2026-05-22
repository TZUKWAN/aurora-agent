#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML图表模板 - 为每个图表类型生成HTML body内容
"""
import json


def org_chart(data, theme):
    d = data["org_chart"]
    l2 = d["l2"]
    l3 = d["l3"]
    l4 = d["l4"]

    l2_html = "".join([
        f'<div class="card accent-{i+1} text-center" style="padding:16px 32px;font-size:22px;font-weight:bold;min-width:200px;">{t}</div>'
        for i, t in enumerate(l2)
    ])

    l3_rows = []
    for gi, group in enumerate(l3):
        cells = "".join([
            f'<div class="card accent-{gi*2+ti+1} text-center" style="padding:12px 24px;font-size:18px;min-width:140px;">{t}</div>'
            for ti, t in enumerate(group)
        ])
        l3_rows.append(f'<div class="flex justify-center" style="gap:16px;">{cells}</div>')

    l4_blocks = []
    for gi, group in enumerate(l4):
        cells = "".join([
            f'<div style="background:var(--accent{(gi*4+ti)%6+1});opacity:0.85;border-radius:10px;padding:8px 12px;font-size:15px;text-align:center;color:#333;min-width:100px;">{t}</div>'
            for ti, t in enumerate(group)
        ])
        l4_blocks.append(f'<div class="card" style="padding:12px;"><div class="flex flex-wrap justify-center" style="gap:10px;">{cells}</div></div>')

    l4_grid = "\n".join(l4_blocks)

    return f'''
<div class="header">{data["projectName"]} · 公司组织架构</div>
<div class="flex justify-center" style="margin-bottom:20px;">
    <div class="card accent-1 text-center" style="padding:18px 60px;font-size:26px;font-weight:bold;background:var(--accent1);color:#333;">总经理</div>
</div>
<div class="flex justify-center" style="gap:40px;margin-bottom:20px;">
    {l2_html}
</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px;">
    {''.join(l3_rows)}
</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
    {l4_grid}
</div>
'''


def strategy_roadmap(data, theme):
    phases = data["strategy_roadmap"]["phases"]
    cards = []
    for i, p in enumerate(phases):
        items = "".join([f'<div style="background:#f5f5f5;border-radius:8px;padding:10px 14px;margin-top:8px;font-size:15px;">• {item}</div>' for item in p["items"]])
        cards.append(f'''
        <div class="card accent-{i+1}" style="display:flex;flex-direction:column;">
            <div style="font-size:22px;font-weight:bold;color:var(--accent{i+1});margin-bottom:6px;">{p["name"]}</div>
            <div style="font-size:15px;opacity:0.8;margin-bottom:10px;">{p["period"]}</div>
            {items}
        </div>''')

    return f'''
<div class="header">{data["projectName"]} · 发展战略路线</div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:24px;">
    {''.join(cards)}
</div>
'''


def swot(data, theme):
    quads = data["swot"]["quads"]
    positions = [
        ("优势 Strengths", "accent-1", quads[0]["items"]),
        ("劣势 Weaknesses", "accent-2", quads[1]["items"]),
        ("机会 Opportunities", "accent-3", quads[2]["items"]),
        ("威胁 Threats", "accent-4", quads[3]["items"]),
    ]
    cards = []
    for title, accent, items in positions:
        items_html = "".join([f'<div style="background:#f0f0f0;border-radius:8px;padding:12px 16px;margin-top:10px;font-size:17px;">{item}</div>' for item in items])
        cards.append(f'''
        <div class="card {accent}" style="display:flex;flex-direction:column;">
            <div style="font-size:24px;font-weight:bold;margin-bottom:8px;">{title}</div>
            {items_html}
        </div>''')

    return f'''
<div class="header">{data["projectName"]} · SWOT分析</div>
<div style="display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:24px;height:900px;">
    {''.join(cards)}
</div>
'''


def porter_six(data, theme):
    items = data["porter_six"]["items"]
    cards = []
    for i, item in enumerate(items):
        cards.append(f'''
        <div class="card accent-{i+1}" style="display:flex;flex-direction:column;justify-content:center;">
            <div style="font-size:26px;font-weight:bold;color:var(--accent{i+1});margin-bottom:10px;">{item["title"]}</div>
            <div style="font-size:18px;opacity:0.9;margin-bottom:8px;">{item["desc"]}</div>
            <div style="font-size:16px;opacity:0.7;white-space:pre-line;">{item["detail"]}</div>
        </div>''')

    return f'''
<div class="header">{data["projectName"]} · 波特六力分析</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr;gap:24px;height:900px;">
    {''.join(cards)}
</div>
'''


def rd_roadmap(data, theme):
    phases = data["rd_roadmap"]["phases"]
    cards = []
    for i, p in enumerate(phases):
        items = "".join([f'<div style="background:#f5f5f5;border-radius:8px;padding:10px 14px;margin-top:8px;font-size:15px;">• {item}</div>' for item in p["items"]])
        cards.append(f'''
        <div class="card accent-{i+1}" style="display:flex;flex-direction:column;">
            <div style="font-size:22px;font-weight:bold;color:var(--accent{i+1});margin-bottom:6px;">{p["name"]}</div>
            <div style="font-size:15px;opacity:0.8;margin-bottom:10px;">{p["period"]}</div>
            {items}
        </div>''')

    return f'''
<div class="header">{data["projectName"]} · 研发路线</div>
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:20px;">
    {''.join(cards)}
</div>
'''


def product_matrix(data, theme):
    d = data["product_matrix"]
    rows = d["rows"]
    cols = d["cols"]
    matrix = d["data"]

    header = "".join([f'<div style="background:var(--accent{i+1});padding:14px;border-radius:10px;font-weight:bold;text-align:center;font-size:16px;">{c}</div>' for i, c in enumerate(cols)])
    body = ""
    for ri, r in enumerate(rows):
        row_html = f'<div style="background:var(--accent{ri+2});padding:14px;border-radius:10px;font-weight:bold;text-align:center;font-size:16px;">{r}</div>'
        for ci, cell in enumerate(matrix[ri]):
            row_html += f'<div style="background:#f0f0f0;padding:14px;border-radius:10px;text-align:center;font-size:16px;border:1px solid var(--accent{(ri+ci)%6+1});">{cell}</div>'
        body += f'<div style="display:grid;grid-template-columns:120px repeat(5,1fr);gap:12px;margin-top:12px;">{row_html}</div>'

    return f'''
<div class="header">{data["projectName"]} · 产品矩阵</div>
<div style="display:grid;grid-template-columns:120px repeat(5,1fr);gap:12px;">
    <div style="background:var(--title);color:var(--bg);padding:14px;border-radius:10px;font-weight:bold;text-align:center;">版本</div>
    {header}
</div>
{body}
<div style="margin-top:24px;padding:16px;background:#f0f0f0;border-radius:12px;font-size:16px;text-align:center;">{d["bottomDesc"]}</div>
'''


def layered_arch(data, theme, title_key, default_title):
    layers = data[title_key]["layers"]
    cards = []
    for i, layer in enumerate(layers):
        items = "".join([
            f'<div style="background:var(--accent{(i+j)%6+1});opacity:0.9;border-radius:10px;padding:10px 18px;font-size:16px;text-align:center;color:#333;font-weight:500;">{item}</div>'
            for j, item in enumerate(layer["items"])
        ])
        cards.append(f'''
        <div class="card accent-{i+1}" style="display:flex;align-items:center;gap:24px;padding:20px 30px;">
            <div style="font-size:22px;font-weight:bold;color:var(--accent{i+1});min-width:140px;text-align:center;">{layer["name"]}</div>
            <div class="flex flex-wrap" style="gap:14px;flex:1;">{items}</div>
        </div>''')

    return f'''
<div class="header">{data["projectName"]} · {default_title}</div>
<div style="display:flex;flex-direction:column;gap:16px;">
    {''.join(cards)}
</div>
'''


def funnel(data, theme):
    stages = data["funnel"]["stages"]
    cards = []
    for i, s in enumerate(stages):
        width = max(20, 100 - i * 15)
        cards.append(f'''
        <div style="display:flex;align-items:center;gap:20px;margin-bottom:16px;">
            <div style="width:100px;text-align:right;font-size:18px;font-weight:bold;color:var(--accent{i+1});">{s["value"]}</div>
            <div style="width:{width}%;background:linear-gradient(90deg,var(--accent{i+1}),transparent);padding:16px 24px;border-radius:12px;font-size:20px;font-weight:bold;">{s["name"]}</div>
            <div style="font-size:16px;opacity:0.8;">{s["desc"]} | {s["count"]}</div>
        </div>''')

    return f'''
<div class="header">{data["projectName"]} · 营销渠道漏斗</div>
<div style="display:flex;flex-direction:column;justify-content:center;height:900px;padding:0 60px;">
    {''.join(cards)}
</div>
'''


def business_canvas(data, theme):
    cells = data["business_canvas"]["cells"]
    grid = []
    for i, c in enumerate(cells):
        items = "".join([f'<div style="background:#f0f0f0;border-radius:6px;padding:8px 12px;margin-top:6px;font-size:15px;">{item}</div>' for item in c["items"]])
        grid.append(f'''
        <div class="card accent-{i%6+1}" style="display:flex;flex-direction:column;">
            <div style="font-size:18px;font-weight:bold;color:var(--accent{i%6+1});margin-bottom:6px;">{c["title"]}</div>
            {items}
        </div>''')

    return f'''
<div class="header">{data["projectName"]} · 商业模式画布</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(3,1fr);gap:16px;height:900px;">
    {''.join(grid)}
</div>
'''


def flowchart(data, theme, title_key, default_title):
    steps = data[title_key]["steps"]
    cards = []
    for i, step in enumerate(steps):
        cards.append(f'''
        <div style="display:flex;flex-direction:column;align-items:center;gap:10px;">
            <div style="width:50px;height:50px;background:var(--accent{i%6+1});border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:bold;color:#333;">{i+1}</div>
            <div class="card accent-{i%6+1} text-center" style="padding:16px 20px;font-size:18px;font-weight:bold;min-width:140px;">{step}</div>
        </div>''')

    arrows = '<div style="font-size:30px;color:var(--accent1);opacity:0.6;">→</div>' * (len(steps) - 1)

    return f'''
<div class="header">{data["projectName"]} · {default_title}</div>
<div style="display:flex;align-items:center;justify-content:center;gap:16px;height:800px;flex-wrap:wrap;">
    {''.join(cards)}
</div>
'''


def market_growth(data, theme):
    d = data["market_growth"]
    items = d["data"]
    max_val = max(x["value"] for x in items)

    bars = []
    for i, item in enumerate(items):
        h = (item["value"] / max_val) * 600
        bars.append(f'''
        <div style="display:flex;flex-direction:column;align-items:center;gap:10px;">
            <div style="height:650px;display:flex;align-items:flex-end;">
                <div style="width:120px;height:{h}px;background:linear-gradient(180deg,var(--accent{i%6+1}),transparent);border-radius:12px 12px 0 0;display:flex;align-items:flex-start;justify-content:center;padding-top:10px;font-size:18px;font-weight:bold;color:#333;">{item["label"]}</div>
            </div>
            <div style="font-size:20px;font-weight:bold;color:var(--accent{i%6+1});">{item["year"]}</div>
        </div>''')

    return f'''
<div class="header">{data["projectName"]} · 市场规模增长趋势</div>
<div style="display:flex;justify-content:center;align-items:flex-end;gap:40px;height:800px;padding-bottom:40px;">
    {''.join(bars)}
</div>
<div style="text-align:center;font-size:28px;font-weight:bold;color:var(--accent1);margin-top:20px;">年复合增长率(CAGR): {d["cagr"]}</div>
'''


def policy_timeline(data, theme):
    phases = data["policy_timeline"]["phases"]
    cards = []
    for i, p in enumerate(phases):
        items = "".join([f'<div style="background:#f5f5f5;border-radius:8px;padding:10px 14px;margin-top:8px;font-size:15px;">• {item}</div>' for item in p["items"]])
        cards.append(f'''
        <div class="card accent-{i+1}" style="display:flex;flex-direction:column;flex:1;">
            <div style="font-size:22px;font-weight:bold;color:var(--accent{i+1});margin-bottom:6px;">{p["name"]}</div>
            <div style="font-size:15px;opacity:0.8;margin-bottom:10px;">{p["dur"]}</div>
            {items}
        </div>''')

    return f'''
<div class="header">{data["projectName"]} · 政策支持时间线</div>
<div style="display:flex;gap:20px;height:850px;align-items:stretch;">
    {''.join(cards)}
</div>
'''


def personas(data, theme):
    personas = data["personas"]["personas"]
    cards = []
    for i, p in enumerate(personas):
        attrs = "".join([f'<div style="background:#f5f5f5;border-radius:8px;padding:10px 14px;margin-top:8px;font-size:16px;">{attr}</div>' for attr in p["attrs"]])
        cards.append(f'''
        <div class="card accent-{i+1}" style="display:flex;flex-direction:column;align-items:center;padding:30px;flex:1;">
            <div style="width:90px;height:90px;background:var(--accent{i+1});border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:40px;font-weight:bold;color:#333;margin-bottom:16px;">{p["name"][0]}</div>
            <div style="font-size:24px;font-weight:bold;margin-bottom:16px;">{p["name"]}</div>
            {attrs}
        </div>''')

    return f'''
<div class="header">{data["projectName"]} · 目标客户画像</div>
<div style="display:flex;gap:30px;justify-content:center;height:850px;align-items:stretch;">
    {''.join(cards)}
</div>
'''


def customer_radar(data, theme):
    labels = data["customer_radar"]["labels"]
    values = data["customer_radar"]["values"]

    bars = []
    for i, (label, val) in enumerate(zip(labels, values)):
        bars.append(f'''
        <div style="margin-bottom:20px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                <span style="font-size:20px;font-weight:bold;">{label}</span>
                <span style="font-size:20px;font-weight:bold;color:var(--accent{i%6+1});">{val}%</span>
            </div>
            <div style="height:24px;background:#f5f5f5;border-radius:12px;overflow:hidden;">
                <div style="width:{val}%;height:100%;background:linear-gradient(90deg,var(--accent{i%6+1}),var(--accent{(i+1)%6+1}));border-radius:12px;"></div>
            </div>
        </div>''')

    return f'''
<div class="header">{data["projectName"]} · 客户需求分析</div>
<div style="max-width:1400px;margin:0 auto;padding-top:40px;">
    {''.join(bars)}
</div>
'''


def product_comparison(data, theme):
    d = data["product_comparison"]
    headers = d["headers"]
    rows = d["rows"]

    header_html = "".join([f'<div style="background:var(--accent{i+1});padding:16px;font-weight:bold;text-align:center;font-size:18px;border-radius:10px 10px 0 0;">{h}</div>' for i, h in enumerate(headers)])
    body = ""
    for ri, row in enumerate(rows):
        row_html = ""
        for ci, cell in enumerate(row):
            if ci == 0:
                bg = "var(--accent5)"
            elif ci == 1:
                bg = "#e8e8e8"
            else:
                bg = "#f0f0f0"
            row_html += f'<div style="background:{bg};padding:16px;text-align:center;font-size:18px;font-weight:{"bold" if ci==1 else "normal"};border-top:1px solid #f5f5f5;">{cell}</div>'
        body += f'<div style="display:grid;grid-template-columns:repeat(4,1fr);">{row_html}</div>'

    return f'''
<div class="header">{data["projectName"]} · 产品优势对比</div>
<div style="max-width:1400px;margin:0 auto;">
    <div style="display:grid;grid-template-columns:repeat(4,1fr);">{header_html}</div>
    {body}
    <div style="margin-top:24px;padding:16px;background:#f0f0f0;border-radius:12px;font-size:18px;text-align:center;">{d["bottomText"]}</div>
</div>
'''


def effect_bar(data, theme):
    items = data["effect_bar"]["data"]
    bars = []
    for i, item in enumerate(items):
        bars.append(f'''
        <div style="margin-bottom:30px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
                <span style="font-size:22px;font-weight:bold;">{item["label"]} <span style="font-size:16px;opacity:0.7;">({item["desc"]})</span></span>
                <span style="font-size:28px;font-weight:bold;color:var(--accent{i+1});">{item["value"]}%</span>
            </div>
            <div style="height:36px;background:#f5f5f5;border-radius:18px;overflow:hidden;">
                <div style="width:{item["value"]}%;height:100%;background:linear-gradient(90deg,var(--accent{i+1}),var(--accent{(i+2)%6+1}));border-radius:18px;"></div>
            </div>
        </div>''')

    return f'''
<div class="header">{data["projectName"]} · 应用效果数据对比</div>
<div style="max-width:1200px;margin:0 auto;padding-top:60px;">
    {''.join(bars)}
</div>
'''


def market_share(data, theme):
    slices = data["market_share"]["slices"]
    total = sum(s["pct"] for s in slices)
    cumulative = 0
    pie_slices = []
    legend = []
    for i, s in enumerate(slices):
        pct = (s["pct"] / total) * 100
        start = cumulative * 3.6
        end = (cumulative + s["pct"]) * 3.6
        cumulative += s["pct"]
        # SVG pie slice
        x1 = 300 + 250 * __import__('math').cos(__import__('math').radians(start - 90))
        y1 = 300 + 250 * __import__('math').sin(__import__('math').radians(start - 90))
        x2 = 300 + 250 * __import__('math').cos(__import__('math').radians(end - 90))
        y2 = 300 + 250 * __import__('math').sin(__import__('math').radians(end - 90))
        large_arc = 1 if s["pct"] > 50 else 0
        color = f"var(--accent{i+1})"
        pie_slices.append(f'<path d="M 300 300 L {x1} {y1} A 250 250 0 {large_arc} 1 {x2} {y2} Z" fill="{color}" stroke="#d0d0d0" stroke-width="2"/>')
        legend.append(f'''
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
            <div style="width:24px;height:24px;background:{color};border-radius:6px;"></div>
            <span style="font-size:20px;">{s["label"]} <strong>{s["pct"]}%</strong></span>
        </div>''')

    svg = f'''<svg width="600" height="600" viewBox="0 0 600 600">
        {''.join(pie_slices)}
        <circle cx="300" cy="300" r="120" fill="url(#bg)" />
    </svg>'''

    return f'''
<div class="header">{data["projectName"]} · 市场占有率分析</div>
<div style="display:flex;align-items:center;justify-content:center;gap:80px;height:850px;">
    <div>{svg}</div>
    <div>{''.join(legend)}</div>
</div>
<div style="text-align:center;font-size:22px;font-weight:bold;color:var(--accent1);margin-top:10px;">{data["market_share"]["bottomText"]}</div>
'''


def revenue_growth(data, theme):
    d = data["revenue_growth"]
    years = d["years"]
    revenue = d["revenue"]
    profit = d["profit"]
    max_val = max(max(revenue), max(profit))

    bars = []
    for i, year in enumerate(years):
        rev_h = (revenue[i] / max_val) * 500
        pro_h = (profit[i] / max_val) * 500
        bars.append(f'''
        <div style="display:flex;flex-direction:column;align-items:center;gap:10px;flex:1;">
            <div style="display:flex;align-items:flex-end;gap:8px;height:550px;">
                <div style="width:50px;height:{rev_h}px;background:var(--accent1);border-radius:8px 8px 0 0;display:flex;align-items:flex-start;justify-content:center;padding-top:8px;font-size:14px;font-weight:bold;color:#333;">{revenue[i]}</div>
                <div style="width:50px;height:{pro_h}px;background:var(--accent3);border-radius:8px 8px 0 0;display:flex;align-items:flex-start;justify-content:center;padding-top:8px;font-size:14px;font-weight:bold;color:#333;">{profit[i]}</div>
            </div>
            <div style="font-size:20px;font-weight:bold;color:var(--accent5);">{year}</div>
        </div>''')

    return f'''
<div class="header">{data["projectName"]} · 收入增长趋势</div>
<div style="display:flex;align-items:flex-end;gap:30px;height:650px;padding:0 80px 40px;">
    {''.join(bars)}
</div>
<div style="display:flex;justify-content:center;gap:40px;margin-top:20px;">
    <div style="display:flex;align-items:center;gap:10px;"><div style="width:30px;height:20px;background:var(--accent1);border-radius:4px;"></div><span style="font-size:18px;">营收</span></div>
    <div style="display:flex;align-items:center;gap:10px;"><div style="width:30px;height:20px;background:var(--accent3);border-radius:4px;"></div><span style="font-size:18px;">净利润</span></div>
</div>
'''


def quadrant(data, theme, title_key, default_title):
    d = data[title_key]
    items = d["items"]
    quad_labels = d["quadLabels"]

    # 四象限背景
    quads_html = f'''
    <div style="position:absolute;top:60px;left:60px;width:850px;height:420px;background:#fafafa;border-radius:16px;padding:20px;border:1px solid #f5f5f5;">
        <div style="font-size:20px;font-weight:bold;color:var(--accent1);">{quad_labels[0]}</div>
    </div>
    <div style="position:absolute;top:60px;right:60px;width:850px;height:420px;background:#fafafa;border-radius:16px;padding:20px;border:1px solid #f5f5f5;">
        <div style="font-size:20px;font-weight:bold;color:var(--accent2);">{quad_labels[1]}</div>
    </div>
    <div style="position:absolute;bottom:60px;left:60px;width:850px;height:420px;background:#fafafa;border-radius:16px;padding:20px;border:1px solid #f5f5f5;">
        <div style="font-size:20px;font-weight:bold;color:var(--accent3);">{quad_labels[2]}</div>
    </div>
    <div style="position:absolute;bottom:60px;right:60px;width:850px;height:420px;background:#fafafa;border-radius:16px;padding:20px;border:1px solid #f5f5f5;">
        <div style="font-size:20px;font-weight:bold;color:var(--accent4);">{quad_labels[3]}</div>
    </div>
    '''

    # 公司卡片
    company_cards = []
    positions = [
        (150, 150), (400, 120), (650, 180), (900, 140), (1150, 200),
        (180, 580), (450, 620), (700, 560), (950, 600), (1200, 640)
    ]
    for i, item in enumerate(items):
        x, y = positions[i % len(positions)]
        company_cards.append(f'''
        <div style="position:absolute;left:{x}px;top:{y}px;background:var(--accent{i%6+1});padding:12px 20px;border-radius:12px;font-size:16px;font-weight:bold;color:#333;box-shadow:0 4px 15px rgba(0,0,0,0.3);white-space:pre-line;text-align:center;">
            {item["name"]}<br/><span style="font-size:13px;opacity:0.9;font-weight:normal;">{item["desc"]}</span>
        </div>''')

    return f'''
<div class="header">{data["projectName"]} · {default_title}</div>
<div style="position:relative;width:100%;height:900px;">
    {quads_html}
    {''.join(company_cards)}
</div>
'''


def revenue_donut(data, theme):
    slices = data["revenue_donut"]["slices"]
    bars = []
    for i, s in enumerate(slices):
        bars.append(f'''
        <div style="display:flex;align-items:center;gap:20px;margin-bottom:24px;">
            <div style="width:160px;font-size:20px;font-weight:bold;">{s["label"]}</div>
            <div style="flex:1;height:36px;background:#f5f5f5;border-radius:18px;overflow:hidden;">
                <div style="width:{s["pct"]}%;height:100%;background:var(--accent{i+1});border-radius:18px;"></div>
            </div>
            <div style="width:80px;text-align:right;font-size:24px;font-weight:bold;color:var(--accent{i+1});">{s["pct"]}%</div>
            <div style="width:280px;font-size:16px;opacity:0.8;">{s["desc"]}</div>
        </div>''')

    return f'''
<div class="header">{data["projectName"]} · 收入构成分析</div>
<div style="max-width:1400px;margin:0 auto;padding-top:60px;">
    {''.join(bars)}
</div>
'''


def funding_use(data, theme):
    items = data["funding_use"]["items"]
    bars = []
    for i, s in enumerate(items):
        bars.append(f'''
        <div style="display:flex;align-items:center;gap:20px;margin-bottom:28px;">
            <div style="width:140px;font-size:20px;font-weight:bold;">{s["label"]}</div>
            <div style="flex:1;height:40px;background:#f5f5f5;border-radius:20px;overflow:hidden;">
                <div style="width:{s["pct"]}%;height:100%;background:linear-gradient(90deg,var(--accent{i+1}),var(--accent{(i+1)%6+1}));border-radius:20px;display:flex;align-items:center;justify-content:flex-end;padding-right:16px;font-size:18px;font-weight:bold;color:#333;">{s["pct"]}%</div>
            </div>
            <div style="width:300px;font-size:16px;opacity:0.8;">{s["desc"]}</div>
        </div>''')

    return f'''
<div class="header">{data["projectName"]} · 资金用途分布</div>
<div style="max-width:1300px;margin:0 auto;padding-top:60px;">
    {''.join(bars)}
</div>
'''


def financing_milestone(data, theme):
    phases = data["financing_milestone"]["phases"]
    cards = []
    for i, p in enumerate(phases):
        items = "".join([f'<div style="background:#f5f5f5;border-radius:8px;padding:10px 14px;margin-top:8px;font-size:15px;">• {item}</div>' for item in p["items"]])
        amount_badge = f'<div style="background:var(--accent{i+1});padding:8px 16px;border-radius:20px;font-size:18px;font-weight:bold;color:#333;display:inline-block;margin:10px 0;">{p["amount"]}</div>' if p["amount"] != "—" else ""
        cards.append(f'''
        <div class="card accent-{i+1}" style="display:flex;flex-direction:column;flex:1;align-items:center;text-align:center;">
            <div style="font-size:22px;font-weight:bold;color:var(--accent{i+1});margin-bottom:6px;">{p["name"]}</div>
            <div style="font-size:15px;opacity:0.8;margin-bottom:6px;">{p["period"]}</div>
            {amount_badge}
            {items}
        </div>''')

    return f'''
<div class="header">{data["projectName"]} · 融资里程碑</div>
<div style="display:flex;gap:18px;height:850px;align-items:stretch;">
    {''.join(cards)}
</div>
'''


def risk_matrix(data, theme):
    rows = data["risk_matrix"]["rows"]
    headers = ["风险类型", "发生概率", "影响程度", "综合评级", "应对优先级"]

    header_html = "".join([f'<div style="background:var(--title);color:var(--bg);padding:16px;font-weight:bold;text-align:center;font-size:18px;">{h}</div>' for h in headers])
    body = ""
    for ri, row in enumerate(rows):
        row_html = f'<div style="background:var(--accent{ri+1});padding:16px;font-weight:bold;text-align:center;font-size:18px;">{row["name"]}</div>'
        for ci, item in enumerate(row["items"]):
            row_html += f'<div style="background:#eeeeee;padding:16px;text-align:center;font-size:17px;border-top:1px solid #f0f0f0;">{item}</div>'
        body += f'<div style="display:grid;grid-template-columns:140px repeat(4,1fr);">{row_html}</div>'

    return f'''
<div class="header">{data["projectName"]} · 风险评估矩阵</div>
<div style="max-width:1500px;margin:0 auto;">
    <div style="display:grid;grid-template-columns:140px repeat(4,1fr);">{header_html}</div>
    {body}
</div>
'''


def product_screenshot(data, theme, index):
    """生成复杂多样的产品界面HTML mockup"""
    name = data["projectName"]
    c1 = theme["accent1"]
    c2 = theme["accent2"]
    c3 = theme["accent3"]
    c4 = theme["accent4"]
    c5 = theme["accent5"]
    text = theme["text"]
    title = theme["title"]

    # 10种截然不同的复杂UI布局
    layouts = [
        # 0. Dashboard Pro: 侧边栏 + KPI行 + 3图表面板 + 活动流
        f'''<div style="display:flex;height:100%;font-size:15px;">
            <div style="width:220px;background:rgba(0,0,0,0.25);padding:20px;display:flex;flex-direction:column;gap:10px;">
                <div style="font-size:22px;font-weight:bold;color:{c1};margin-bottom:15px;">{name}</div>
                <div style="padding:10px 14px;background:rgba(255,255,255,0.08);border-radius:8px;border-left:3px solid {c1};">仪表盘</div>
                <div style="padding:10px 14px;background:rgba(255,255,255,0.04);border-radius:8px;">数据洞察</div>
                <div style="padding:10px 14px;background:rgba(255,255,255,0.04);border-radius:8px;">用户管理</div>
                <div style="padding:10px 14px;background:rgba(255,255,255,0.04);border-radius:8px;">系统设置</div>
                <div style="padding:10px 14px;background:rgba(255,255,255,0.04);border-radius:8px;">告警中心</div>
                <div style="margin-top:auto;padding:12px;background:rgba(255,255,255,0.06);border-radius:10px;">
                    <div style="font-size:13px;opacity:0.7;">系统版本</div>
                    <div style="font-size:16px;font-weight:bold;">v3.2.1</div>
                </div>
            </div>
            <div style="flex:1;padding:24px;display:flex;flex-direction:column;gap:16px;overflow:hidden;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="font-size:14px;opacity:0.6;">最后更新: 2026-04-28 14:32:18</div>
                    <div style="display:flex;gap:10px;">
                        <span style="padding:6px 12px;background:rgba(255,255,255,0.06);border-radius:6px;font-size:13px;">🔔 3</span>
                        <span style="padding:6px 12px;background:rgba(255,255,255,0.06);border-radius:6px;font-size:13px;">👤 Admin</span>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:14px;">
                    <div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:16px;border-left:4px solid {c1};">
                        <div style="font-size:13px;opacity:0.7;">今日营收</div><div style="font-size:26px;font-weight:bold;color:{c1};">¥128.5万</div><div style="font-size:12px;color:{c3};">▲ 12.3%</div>
                    </div>
                    <div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:16px;border-left:4px solid {c2};">
                        <div style="font-size:13px;opacity:0.7;">活跃用户</div><div style="font-size:26px;font-weight:bold;color:{c2};">45,231</div><div style="font-size:12px;color:{c3};">▲ 8.7%</div>
                    </div>
                    <div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:16px;border-left:4px solid {c3};">
                        <div style="font-size:13px;opacity:0.7;">转化率</div><div style="font-size:26px;font-weight:bold;color:{c3};">6.82%</div><div style="font-size:12px;color:{c4};">▼ 0.3%</div>
                    </div>
                    <div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:16px;border-left:4px solid {c4};">
                        <div style="font-size:13px;opacity:0.7;">平均客单价</div><div style="font-size:26px;font-weight:bold;color:{c4};">¥342</div><div style="font-size:12px;color:{c3};">▲ 5.1%</div>
                    </div>
                    <div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:16px;border-left:4px solid {c5};">
                        <div style="font-size:13px;opacity:0.7;">系统健康度</div><div style="font-size:26px;font-weight:bold;color:{c5};">99.97%</div><div style="font-size:12px;color:{c3};">▲ 0.02%</div>
                    </div>
                </div>
                <div style="flex:1;display:grid;grid-template-columns:2fr 1fr 1fr;gap:14px;min-height:0;">
                    <div style="background:rgba(255,255,255,0.05);border-radius:12px;padding:18px;display:flex;flex-direction:column;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:10px;"><span style="font-weight:bold;">核心指标趋势</span><span style="font-size:12px;opacity:0.5;">近30天</span></div>
                        <div style="flex:1;display:flex;align-items:flex-end;gap:6px;padding:0 8px;">
                            <div style="flex:1;background:linear-gradient(180deg,{c1},rgba(0,0,0,0));border-radius:4px 4px 0 0;height:45%;"></div>
                            <div style="flex:1;background:linear-gradient(180deg,{c1},rgba(0,0,0,0));border-radius:4px 4px 0 0;height:62%;"></div>
                            <div style="flex:1;background:linear-gradient(180deg,{c1},rgba(0,0,0,0));border-radius:4px 4px 0 0;height:55%;"></div>
                            <div style="flex:1;background:linear-gradient(180deg,{c1},rgba(0,0,0,0));border-radius:4px 4px 0 0;height:78%;"></div>
                            <div style="flex:1;background:linear-gradient(180deg,{c1},rgba(0,0,0,0));border-radius:4px 4px 0 0;height:68%;"></div>
                            <div style="flex:1;background:linear-gradient(180deg,{c2},rgba(0,0,0,0));border-radius:4px 4px 0 0;height:85%;"></div>
                            <div style="flex:1;background:linear-gradient(180deg,{c2},rgba(0,0,0,0));border-radius:4px 4px 0 0;height:72%;"></div>
                            <div style="flex:1;background:linear-gradient(180deg,{c2},rgba(0,0,0,0));border-radius:4px 4px 0 0;height:90%;"></div>
                            <div style="flex:1;background:linear-gradient(180deg,{c2},rgba(0,0,0,0));border-radius:4px 4px 0 0;height:95%;"></div>
                            <div style="flex:1;background:linear-gradient(180deg,{c3},rgba(0,0,0,0));border-radius:4px 4px 0 0;height:88%;"></div>
                        </div>
                        <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:11px;opacity:0.5;">
                            <span>04-19</span><span>04-28</span>
                        </div>
                    </div>
                    <div style="background:rgba(255,255,255,0.05);border-radius:12px;padding:18px;display:flex;flex-direction:column;">
                        <div style="font-weight:bold;margin-bottom:10px;">用户来源分布</div>
                        <div style="flex:1;display:flex;align-items:center;justify-content:center;">
                            <div style="width:140px;height:140px;border-radius:50%;background:conic-gradient({c1} 0% 35%, {c2} 35% 60%, {c3} 60% 80%, {c4} 80% 100%);"></div>
                        </div>
                        <div style="display:flex;flex-direction:column;gap:6px;margin-top:8px;font-size:12px;">
                            <div style="display:flex;align-items:center;gap:6px;"><div style="width:10px;height:10px;background:{c1};border-radius:2px;"></div><span>搜索引擎 35%</span></div>
                            <div style="display:flex;align-items:center;gap:6px;"><div style="width:10px;height:10px;background:{c2};border-radius:2px;"></div><span>直接访问 25%</span></div>
                            <div style="display:flex;align-items:center;gap:6px;"><div style="width:10px;height:10px;background:{c3};border-radius:2px;"></div><span>社交媒体 20%</span></div>
                        </div>
                    </div>
                    <div style="background:rgba(255,255,255,0.05);border-radius:12px;padding:18px;display:flex;flex-direction:column;gap:10px;">
                        <div style="font-weight:bold;margin-bottom:4px;">最近动态</div>
                        <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;font-size:13px;"><span style="color:{c1};">●</span> 新订单 #8932 已支付</div>
                        <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;font-size:13px;"><span style="color:{c2};">●</span> 用户反馈已处理</div>
                        <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;font-size:13px;"><span style="color:{c3};">●</span> 系统备份完成</div>
                        <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;font-size:13px;"><span style="color:{c4};">●</span> API v2.1 发布</div>
                        <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;font-size:13px;"><span style="color:{c5};">●</span> 证书即将过期</div>
                    </div>
                </div>
            </div>
        </div>''',

        # 1. Data Studio: 顶部筛选 + 大数据表 + 侧边统计
        f'''<div style="height:100%;display:flex;flex-direction:column;padding:30px;font-size:15px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
                <div style="font-size:28px;font-weight:bold;">{name} 数据中心</div>
                <div style="display:flex;gap:10px;">
                    <span style="padding:8px 16px;background:rgba(255,255,255,0.06);border-radius:8px;font-size:13px;">⏱ 实时</span>
                    <span style="padding:8px 16px;background:{c1};border-radius:8px;font-size:13px;font-weight:bold;">导出报表</span>
                </div>
            </div>
            <div style="display:flex;gap:12px;margin-bottom:16px;">
                <div style="flex:1;padding:10px 14px;background:rgba(255,255,255,0.05);border-radius:8px;border:1px solid rgba(255,255,255,0.1);">🔍 搜索订单号、客户名称...</div>
                <div style="padding:10px 18px;background:rgba(255,255,255,0.05);border-radius:8px;border:1px solid rgba(255,255,255,0.1);">状态 ▼</div>
                <div style="padding:10px 18px;background:rgba(255,255,255,0.05);border-radius:8px;border:1px solid rgba(255,255,255,0.1);">时间范围 ▼</div>
                <div style="padding:10px 18px;background:rgba(255,255,255,0.05);border-radius:8px;border:1px solid rgba(255,255,255,0.1);">渠道 ▼</div>
            </div>
            <div style="flex:1;display:flex;gap:16px;min-height:0;">
                <div style="flex:1;display:flex;flex-direction:column;background:rgba(255,255,255,0.04);border-radius:12px;border:1px solid rgba(255,255,255,0.08);overflow:hidden;">
                    <div style="display:grid;grid-template-columns:80px 1.5fr 1fr 1fr 1fr 1fr 100px;gap:0;padding:12px 16px;background:rgba(255,255,255,0.06);font-weight:bold;font-size:14px;border-bottom:1px solid rgba(255,255,255,0.1);">
                        <span>ID</span><span>客户</span><span>金额</span><span>状态</span><span>渠道</span><span>时间</span><span>操作</span>
                    </div>
                    <div style="overflow-y:auto;flex:1;">
                        {''.join([f'<div style="display:grid;grid-template-columns:80px 1.5fr 1fr 1fr 1fr 1fr 100px;gap:0;padding:12px 16px;border-bottom:1px solid rgba(255,255,255,0.04);font-size:13px;align-items:center;"><span style="opacity:0.6;">#{8901+i}</span><span>客户{chr(65+i%26)}公司</span><span style="font-weight:bold;">¥{1200+i*340:,}</span><span style="padding:4px 10px;background:{c1 if i%4==0 else c2 if i%4==1 else c3 if i%4==2 else c4};border-radius:12px;font-size:12px;display:inline-block;width:fit-content;">{["已完成","处理中","待确认","已取消"][i%4]}</span><span style="opacity:0.7;">{["官网","小程序","APP","第三方"][i%4]}</span><span style="opacity:0.5;font-size:12px;">2026-04-{28-i:02d}</span><span style="color:{c1};font-size:12px;">详情 ›</span></div>' for i in range(12)])}
                    </div>
                    <div style="padding:10px 16px;background:rgba(255,255,255,0.04);display:flex;justify-content:space-between;align-items:center;font-size:13px;border-top:1px solid rgba(255,255,255,0.1);">
                        <span>显示 1-12 共 1,247 条</span>
                        <div style="display:flex;gap:6px;">
                            <span style="padding:4px 10px;background:rgba(255,255,255,0.06);border-radius:4px;">‹</span>
                            <span style="padding:4px 10px;background:{c1};border-radius:4px;">1</span>
                            <span style="padding:4px 10px;background:rgba(255,255,255,0.06);border-radius:4px;">2</span>
                            <span style="padding:4px 10px;background:rgba(255,255,255,0.06);border-radius:4px;">3</span>
                            <span style="padding:4px 10px;background:rgba(255,255,255,0.06);border-radius:4px;">›</span>
                        </div>
                    </div>
                </div>
                <div style="width:280px;display:flex;flex-direction:column;gap:14px;">
                    <div style="background:rgba(255,255,255,0.05);border-radius:12px;padding:16px;">
                        <div style="font-size:13px;opacity:0.6;margin-bottom:8px;">今日汇总</div>
                        <div style="font-size:32px;font-weight:bold;color:{c1};">¥2.4M</div>
                        <div style="margin-top:10px;display:flex;flex-direction:column;gap:6px;font-size:13px;">
                            <div style="display:flex;justify-content:space-between;"><span>订单数</span><span>1,247</span></div>
                            <div style="display:flex;justify-content:space-between;"><span>退款率</span><span>2.1%</span></div>
                            <div style="display:flex;justify-content:space-between;"><span>客单价</span><span>¥1,926</span></div>
                        </div>
                    </div>
                    <div style="background:rgba(255,255,255,0.05);border-radius:12px;padding:16px;flex:1;">
                        <div style="font-size:13px;opacity:0.6;margin-bottom:10px;">渠道占比</div>
                        <div style="display:flex;flex-direction:column;gap:8px;">
                            <div><div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px;"><span>官网</span><span>42%</span></div><div style="height:6px;background:rgba(255,255,255,0.08);border-radius:3px;"><div style="width:42%;height:100%;background:{c1};border-radius:3px;"></div></div></div>
                            <div><div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px;"><span>小程序</span><span>28%</span></div><div style="height:6px;background:rgba(255,255,255,0.08);border-radius:3px;"><div style="width:28%;height:100%;background:{c2};border-radius:3px;"></div></div></div>
                            <div><div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px;"><span>APP</span><span>18%</span></div><div style="height:6px;background:rgba(255,255,255,0.08);border-radius:3px;"><div style="width:18%;height:100%;background:{c3};border-radius:3px;"></div></div></div>
                            <div><div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px;"><span>第三方</span><span>12%</span></div><div style="height:6px;background:rgba(255,255,255,0.08);border-radius:3px;"><div style="width:12%;height:100%;background:{c4};border-radius:3px;"></div></div></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>''',

        # 2. Analytics Hub: 2x2图表网格 + 指标带 + 对比表
        f'''<div style="height:100%;display:flex;flex-direction:column;padding:30px;font-size:15px;gap:16px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-size:28px;font-weight:bold;">{name} 分析平台</div>
                <div style="display:flex;gap:8px;">
                    <span style="padding:6px 14px;background:rgba(255,255,255,0.06);border-radius:6px;font-size:13px;">今日</span>
                    <span style="padding:6px 14px;background:rgba(255,255,255,0.06);border-radius:6px;font-size:13px;">本周</span>
                    <span style="padding:6px 14px;background:{c1};border-radius:6px;font-size:13px;font-weight:bold;">本月</span>
                </div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:12px;">
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;text-align:center;"><div style="font-size:12px;opacity:0.6;">访问量</div><div style="font-size:22px;font-weight:bold;color:{c1};">89.2K</div><div style="font-size:11px;color:{c3};">▲ 15%</div></div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;text-align:center;"><div style="font-size:12px;opacity:0.6;">跳出率</div><div style="font-size:22px;font-weight:bold;color:{c2};">34.2%</div><div style="font-size:11px;color:{c4};">▼ 2%</div></div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;text-align:center;"><div style="font-size:12px;opacity:0.6;">停留时长</div><div style="font-size:22px;font-weight:bold;color:{c3};">4:32</div><div style="font-size:11px;color:{c3};">▲ 8%</div></div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;text-align:center;"><div style="font-size:12px;opacity:0.6;">新用户</div><div style="font-size:22px;font-weight:bold;color:{c4};">12.5K</div><div style="font-size:11px;color:{c3};">▲ 22%</div></div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;text-align:center;"><div style="font-size:12px;opacity:0.6;">回访率</div><div style="font-size:22px;font-weight:bold;color:{c5};">68%</div><div style="font-size:11px;color:{c3};">▲ 5%</div></div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;text-align:center;"><div style="font-size:12px;opacity:0.6;">LTV</div><div style="font-size:22px;font-weight:bold;color:{c1};">¥1,850</div><div style="font-size:11px;color:{c4};">▼ 1%</div></div>
            </div>
            <div style="flex:1;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:14px;min-height:0;">
                <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;display:flex;flex-direction:column;">
                    <div style="font-weight:bold;margin-bottom:10px;">流量趋势对比</div>
                    <div style="flex:1;display:flex;align-items:flex-end;gap:4px;padding:0 8px;">
                        {''.join([f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px;"><div style="width:100%;display:flex;align-items:flex-end;gap:2px;height:100%;"><div style="flex:1;background:{c1};border-radius:2px 2px 0 0;opacity:0.7;height:{30+int((i*7)%65)}%;"></div><div style="flex:1;background:{c2};border-radius:2px 2px 0 0;opacity:0.7;height:{20+int((i*11)%60)}%;"></div></div><span style="font-size:10px;opacity:0.5;">{i+1}</span></div>' for i in range(14)])}
                    </div>
                </div>
                <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;display:flex;flex-direction:column;">
                    <div style="font-weight:bold;margin-bottom:10px;">转化漏斗</div>
                    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:10px;padding:0 40px;">
                        <div style="display:flex;align-items:center;gap:12px;"><div style="width:100%;background:{c1};padding:10px 16px;border-radius:8px;font-weight:bold;">访问 100%</div><span style="font-size:12px;opacity:0.5;">89,200</span></div>
                        <div style="display:flex;align-items:center;gap:12px;"><div style="width:72%;background:{c2};padding:10px 16px;border-radius:8px;font-weight:bold;">浏览 72%</div><span style="font-size:12px;opacity:0.5;">64,224</span></div>
                        <div style="display:flex;align-items:center;gap:12px;"><div style="width:45%;background:{c3};padding:10px 16px;border-radius:8px;font-weight:bold;">加购 45%</div><span style="font-size:12px;opacity:0.5;">40,140</span></div>
                        <div style="display:flex;align-items:center;gap:12px;"><div style="width:18%;background:{c4};padding:10px 16px;border-radius:8px;font-weight:bold;">成交 18%</div><span style="font-size:12px;opacity:0.5;">16,056</span></div>
                    </div>
                </div>
                <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;display:flex;flex-direction:column;">
                    <div style="font-weight:bold;margin-bottom:10px;">设备分布</div>
                    <div style="flex:1;display:flex;align-items:center;justify-content:center;gap:30px;">
                        <div style="width:160px;height:160px;border-radius:50%;background:conic-gradient({c1} 0% 55%, {c2} 55% 80%, {c3} 80% 95%, {c4} 95% 100%);"></div>
                        <div style="display:flex;flex-direction:column;gap:10px;font-size:14px;">
                            <div style="display:flex;align-items:center;gap:8px;"><div style="width:12px;height:12px;background:{c1};border-radius:3px;"></div><span>移动端 55%</span></div>
                            <div style="display:flex;align-items:center;gap:8px;"><div style="width:12px;height:12px;background:{c2};border-radius:3px;"></div><span>桌面端 25%</span></div>
                            <div style="display:flex;align-items:center;gap:8px;"><div style="width:12px;height:12px;background:{c3};border-radius:3px;"></div><span>平板 15%</span></div>
                            <div style="display:flex;align-items:center;gap:8px;"><div style="width:12px;height:12px;background:{c4};border-radius:3px;"></div><span>其他 5%</span></div>
                        </div>
                    </div>
                </div>
                <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;display:flex;flex-direction:column;">
                    <div style="font-weight:bold;margin-bottom:10px;">Top 5 页面</div>
                    <div style="flex:1;display:flex;flex-direction:column;gap:8px;justify-content:center;">
                        <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:rgba(255,255,255,0.04);border-radius:6px;"><span>首页</span><span style="font-weight:bold;color:{c1};">32.5%</span></div>
                        <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:rgba(255,255,255,0.04);border-radius:6px;"><span>产品页</span><span style="font-weight:bold;color:{c2};">24.1%</span></div>
                        <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:rgba(255,255,255,0.04);border-radius:6px;"><span>价格页</span><span style="font-weight:bold;color:{c3};">18.7%</span></div>
                        <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:rgba(255,255,255,0.04);border-radius:6px;"><span>文档中心</span><span style="font-weight:bold;color:{c4};">14.2%</span></div>
                        <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:rgba(255,255,255,0.04);border-radius:6px;"><span>关于我们</span><span style="font-weight:bold;color:{c5};">10.5%</span></div>
                    </div>
                </div>
            </div>
        </div>''',

        # 3. Monitoring Center: 状态网格 + 日志流 + 指标
        f'''<div style="height:100%;display:flex;flex-direction:column;padding:30px;font-size:15px;gap:14px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-size:28px;font-weight:bold;">{name} 监控中心</div>
                <div style="display:flex;gap:10px;align-items:center;">
                    <span style="padding:6px 12px;background:rgba(255,255,255,0.06);border-radius:6px;font-size:13px;">🟢 正常运行</span>
                    <span style="padding:6px 12px;background:rgba(255,255,255,0.06);border-radius:6px;font-size:13px;">⏱ 刷新: 5s</span>
                </div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;">
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;display:flex;align-items:center;gap:12px;">
                    <div style="width:44px;height:44px;background:{c1};border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;">🖥</div>
                    <div><div style="font-size:12px;opacity:0.6;">CPU 使用率</div><div style="font-size:22px;font-weight:bold;">42%</div></div>
                </div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;display:flex;align-items:center;gap:12px;">
                    <div style="width:44px;height:44px;background:{c2};border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;">💾</div>
                    <div><div style="font-size:12px;opacity:0.6;">内存占用</div><div style="font-size:22px;font-weight:bold;">6.2GB</div></div>
                </div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;display:flex;align-items:center;gap:12px;">
                    <div style="width:44px;height:44px;background:{c3};border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;">🌐</div>
                    <div><div style="font-size:12px;opacity:0.6;">网络吞吐</div><div style="font-size:22px;font-weight:bold;">1.2Gbps</div></div>
                </div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;display:flex;align-items:center;gap:12px;">
                    <div style="width:44px;height:44px;background:{c4};border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;">🔋</div>
                    <div><div style="font-size:12px;opacity:0.6;">磁盘IO</div><div style="font-size:22px;font-weight:bold;">234MB/s</div></div>
                </div>
            </div>
            <div style="flex:1;display:grid;grid-template-columns:1.2fr 1fr;gap:14px;min-height:0;">
                <div style="display:flex;flex-direction:column;gap:14px;">
                    <div style="flex:1;background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;display:flex;flex-direction:column;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:10px;"><span style="font-weight:bold;">实时请求QPS</span><span style="font-size:20px;font-weight:bold;color:{c1};">8,492</span></div>
                        <div style="flex:1;display:flex;align-items:flex-end;gap:3px;">
                            {''.join([f'<div style="flex:1;background:linear-gradient(180deg,{c1},rgba(0,0,0,0));border-radius:2px 2px 0 0;height:{25+int((i*13)%70)}%;"></div>' for i in range(40)])}
                        </div>
                    </div>
                    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;display:flex;flex-direction:column;gap:8px;max-height:220px;">
                        <div style="font-weight:bold;margin-bottom:4px;">实时日志流</div>
                        <div style="font-family:monospace;font-size:12px;overflow-y:auto;display:flex;flex-direction:column;gap:4px;">
                            <div><span style="color:{c3};">[WARN]</span> <span style="opacity:0.7;">14:32:18</span> 请求延迟超过阈值 1.2s</div>
                            <div><span style="color:{c1};">[INFO]</span> <span style="opacity:0.7;">14:32:15</span> 节点 node-03 健康检查通过</div>
                            <div><span style="color:{c1};">[INFO]</span> <span style="opacity:0.7;">14:32:12</span> 任务队列处理完成 1,024 条</div>
                            <div><span style="color:{c2};">[DEBUG]</span> <span style="opacity:0.7;">14:32:09</span> 缓存命中率 96.5%</div>
                            <div><span style="color:{c3};">[WARN]</span> <span style="opacity:0.7;">14:32:06</span> 数据库连接池使用率 82%</div>
                            <div><span style="color:{c1};">[INFO]</span> <span style="opacity:0.7;">14:32:03</span> 自动扩缩容触发 +2 实例</div>
                            <div><span style="color:{c4};">[ERROR]</span> <span style="opacity:0.7;">14:32:00</span> 外部API超时重试第2次</div>
                        </div>
                    </div>
                </div>
                <div style="display:flex;flex-direction:column;gap:14px;">
                    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;">
                        <div style="font-weight:bold;margin-bottom:12px;">服务状态矩阵</div>
                        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">
                            {''.join([f'<div style="padding:12px;background:rgba(255,255,255,0.04);border-radius:8px;text-align:center;"><div style="font-size:11px;opacity:0.6;margin-bottom:4px;">svc-{i+1}</div><div style="width:10px;height:10px;background:{c1 if i%5!=0 else c3};border-radius:50%;margin:0 auto;"></div><div style="font-size:12px;margin-top:4px;">{["正常","正常","正常","正常","告警"][i%5]}</div></div>' for i in range(9)])}
                        </div>
                    </div>
                    <div style="flex:1;background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;display:flex;flex-direction:column;gap:10px;">
                        <div style="font-weight:bold;">告警规则</div>
                        <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;display:flex;justify-content:space-between;align-items:center;font-size:13px;"><span>CPU > 80%</span><span style="color:{c1};">已启用</span></div>
                        <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;display:flex;justify-content:space-between;align-items:center;font-size:13px;"><span>内存 > 90%</span><span style="color:{c1};">已启用</span></div>
                        <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;display:flex;justify-content:space-between;align-items:center;font-size:13px;"><span>QPS 突增 > 200%</span><span style="color:{c3};">静默中</span></div>
                        <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;display:flex;justify-content:space-between;align-items:center;font-size:13px;"><span>错误率 > 1%</span><span style="color:{c1};">已启用</span></div>
                    </div>
                </div>
            </div>
        </div>''',

        # 4. Command Deck: 左侧大面板 + 右侧堆叠
        f'''<div style="height:100%;display:flex;padding:30px;font-size:15px;gap:16px;">
            <div style="flex:1.3;display:flex;flex-direction:column;gap:16px;">
                <div style="font-size:28px;font-weight:bold;">{name} 指挥舱</div>
                <div style="flex:1;background:rgba(255,255,255,0.04);border-radius:12px;padding:20px;display:flex;flex-direction:column;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                        <span style="font-weight:bold;">全局态势感知</span>
                        <span style="font-size:12px;opacity:0.5;">实时渲染中</span>
                    </div>
                    <div style="flex:1;background:rgba(0,0,0,0.2);border-radius:10px;position:relative;overflow:hidden;">
                        <div style="position:absolute;top:15%;left:20%;width:12px;height:12px;background:{c1};border-radius:50%;box-shadow:0 0 15px {c1};"></div>
                        <div style="position:absolute;top:35%;left:45%;width:12px;height:12px;background:{c2};border-radius:50%;box-shadow:0 0 15px {c2};"></div>
                        <div style="position:absolute;top:55%;left:65%;width:12px;height:12px;background:{c3};border-radius:50%;box-shadow:0 0 15px {c3};"></div>
                        <div style="position:absolute;top:25%;left:75%;width:12px;height:12px;background:{c4};border-radius:50%;box-shadow:0 0 15px {c4};"></div>
                        <div style="position:absolute;top:65%;left:30%;width:12px;height:12px;background:{c5};border-radius:50%;box-shadow:0 0 15px {c5};"></div>
                        <div style="position:absolute;top:45%;left:15%;width:12px;height:12px;background:{c1};border-radius:50%;box-shadow:0 0 15px {c1};"></div>
                        <svg style="position:absolute;top:0;left:0;width:100%;height:100%;opacity:0.3;" xmlns="http://www.w3.org/2000/svg">
                            <line x1="20%" y1="15%" x2="45%" y2="35%" stroke="{c1}" stroke-width="1"/>
                            <line x1="45%" y1="35%" x2="65%" y2="55%" stroke="{c2}" stroke-width="1"/>
                            <line x1="65%" y1="55%" x2="75%" y2="25%" stroke="{c3}" stroke-width="1"/>
                            <line x1="15%" y1="45%" x2="30%" y2="65%" stroke="{c4}" stroke-width="1"/>
                        </svg>
                        <div style="position:absolute;bottom:12px;left:12px;display:flex;gap:12px;font-size:12px;">
                            <span style="display:flex;align-items:center;gap:4px;"><div style="width:8px;height:8px;background:{c1};border-radius:50%;"></div>正常节点</span>
                            <span style="display:flex;align-items:center;gap:4px;"><div style="width:8px;height:8px;background:{c3};border-radius:50%;"></div>告警节点</span>
                            <span style="display:flex;align-items:center;gap:4px;"><div style="width:8px;height:8px;background:{c4};border-radius:50%;"></div>离线节点</span>
                        </div>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;">
                    <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;text-align:center;"><div style="font-size:11px;opacity:0.6;">在线节点</div><div style="font-size:22px;font-weight:bold;color:{c1};">128</div></div>
                    <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;text-align:center;"><div style="font-size:11px;opacity:0.6;">任务队列</div><div style="font-size:22px;font-weight:bold;color:{c2};">4,521</div></div>
                    <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;text-align:center;"><div style="font-size:11px;opacity:0.6;">处理速率</div><div style="font-size:22px;font-weight:bold;color:{c3};">2.4K/s</div></div>
                    <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;text-align:center;"><div style="font-size:11px;opacity:0.6;">成功率</div><div style="font-size:22px;font-weight:bold;color:{c4};">99.8%</div></div>
                </div>
            </div>
            <div style="width:340px;display:flex;flex-direction:column;gap:14px;">
                <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;">
                    <div style="font-weight:bold;margin-bottom:12px;">任务时间轴</div>
                    <div style="display:flex;flex-direction:column;gap:10px;">
                        <div style="display:flex;gap:10px;"><div style="width:2px;background:{c1};"></div><div><div style="font-size:12px;opacity:0.6;">14:30</div><div style="font-size:14px;">批次任务 #8921 启动</div></div></div>
                        <div style="display:flex;gap:10px;"><div style="width:2px;background:{c2};"></div><div><div style="font-size:12px;opacity:0.6;">14:25</div><div style="font-size:14px;">数据预处理完成</div></div></div>
                        <div style="display:flex;gap:10px;"><div style="width:2px;background:{c3};"></div><div><div style="font-size:12px;opacity:0.6;">14:20</div><div style="font-size:14px;">模型推理阶段</div></div></div>
                        <div style="display:flex;gap:10px;"><div style="width:2px;background:{c4};"></div><div><div style="font-size:12px;opacity:0.6;">14:15</div><div style="font-size:14px;">结果聚合中...</div></div></div>
                        <div style="display:flex;gap:10px;"><div style="width:2px;background:{c5};"></div><div><div style="font-size:12px;opacity:0.6;">14:10</div><div style="font-size:14px;">任务 #8920 完成</div></div></div>
                    </div>
                </div>
                <div style="flex:1;background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;display:flex;flex-direction:column;gap:10px;">
                    <div style="font-weight:bold;">快速操作</div>
                    <div style="padding:12px;background:rgba(255,255,255,0.06);border-radius:8px;text-align:center;font-weight:bold;color:{c1};">🚀 紧急任务调度</div>
                    <div style="padding:12px;background:rgba(255,255,255,0.06);border-radius:8px;text-align:center;font-weight:bold;color:{c2};">📊 生成全景报告</div>
                    <div style="padding:12px;background:rgba(255,255,255,0.06);border-radius:8px;text-align:center;font-weight:bold;color:{c3};">🔧 系统维护模式</div>
                    <div style="padding:12px;background:rgba(255,255,255,0.06);border-radius:8px;text-align:center;font-weight:bold;color:{c4};">📥 批量数据导入</div>
                    <div style="margin-top:auto;padding:12px;background:rgba(255,255,255,0.06);border-radius:8px;">
                        <div style="font-size:12px;opacity:0.6;margin-bottom:6px;">系统负载预测</div>
                        <div style="height:60px;display:flex;align-items:flex-end;gap:3px;">
                            {''.join([f'<div style="flex:1;background:{c1 if i<8 else c3};border-radius:2px 2px 0 0;height:{20+int((i*9)%80)}%;"></div>' for i in range(12)])}
                        </div>
                    </div>
                </div>
            </div>
        </div>''',

        # 5. Admin Console: 统计行 + 权限矩阵 + 用户表 + 系统 gauges
        f'''<div style="height:100%;display:flex;flex-direction:column;padding:30px;font-size:15px;gap:14px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-size:28px;font-weight:bold;">{name} 管理后台</div>
                <div style="display:flex;gap:8px;"><span style="padding:6px 12px;background:{c1};border-radius:6px;font-size:13px;">+ 新建用户</span></div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;">
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:16px;display:flex;flex-direction:column;align-items:center;gap:6px;">
                    <div style="font-size:36px;">👥</div><div style="font-size:24px;font-weight:bold;color:{c1};">1,842</div><div style="font-size:12px;opacity:0.6;">总用户数</div>
                </div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:16px;display:flex;flex-direction:column;align-items:center;gap:6px;">
                    <div style="font-size:36px;">🔑</div><div style="font-size:24px;font-weight:bold;color:{c2};">156</div><div style="font-size:12px;opacity:0.6;">活跃会话</div>
                </div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:16px;display:flex;flex-direction:column;align-items:center;gap:6px;">
                    <div style="font-size:36px;">🛡</div><div style="font-size:24px;font-weight:bold;color:{c3};">12</div><div style="font-size:12px;opacity:0.6;">安全告警</div>
                </div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:16px;display:flex;flex-direction:column;align-items:center;gap:6px;">
                    <div style="font-size:36px;">📈</div><div style="font-size:24px;font-weight:bold;color:{c4};">99.9%</div><div style="font-size:12px;opacity:0.6;">服务可用性</div>
                </div>
            </div>
            <div style="flex:1;display:grid;grid-template-columns:1fr 1fr;gap:14px;min-height:0;">
                <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;display:flex;flex-direction:column;overflow:hidden;">
                    <div style="font-weight:bold;margin-bottom:12px;">用户权限矩阵</div>
                    <div style="flex:1;overflow:auto;">
                        <div style="display:grid;grid-template-columns:120px repeat(5,1fr);gap:0;font-size:13px;">
                            <div style="padding:8px;background:rgba(255,255,255,0.06);font-weight:bold;">角色 / 权限</div>
                            <div style="padding:8px;background:rgba(255,255,255,0.06);text-align:center;font-weight:bold;">查看</div>
                            <div style="padding:8px;background:rgba(255,255,255,0.06);text-align:center;font-weight:bold;">编辑</div>
                            <div style="padding:8px;background:rgba(255,255,255,0.06);text-align:center;font-weight:bold;">删除</div>
                            <div style="padding:8px;background:rgba(255,255,255,0.06);text-align:center;font-weight:bold;">导出</div>
                            <div style="padding:8px;background:rgba(255,255,255,0.06);text-align:center;font-weight:bold;">管理</div>
                            {''.join([
                                f'<div style="padding:8px;background:rgba(255,255,255,0.03);">{role}</div>' +
                                ''.join([f'<div style="padding:8px;text-align:center;background:rgba(255,255,255,0.03);">{["✓","✓","✗","✗","✗"][j] if i==0 else ["✓","✓","✓","✓","✗"][j] if i==1 else ["✓","✓","✓","✓","✓"][j]}</div>' for j in range(5)])
                                for i, role in enumerate(["普通用户","高级用户","管理员","运维","访客"])
                            ])}
                        </div>
                    </div>
                </div>
                <div style="display:flex;flex-direction:column;gap:14px;">
                    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;flex:1;overflow:hidden;">
                        <div style="font-weight:bold;margin-bottom:10px;">系统健康仪表盘</div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                            <div style="text-align:center;padding:12px;background:rgba(255,255,255,0.04);border-radius:8px;">
                                <div style="font-size:13px;opacity:0.6;margin-bottom:6px;">API网关</div>
                                <div style="width:60px;height:60px;border-radius:50%;border:4px solid {c1};border-top-color:transparent;margin:0 auto;display:flex;align-items:center;justify-content:center;"><span style="font-size:14px;font-weight:bold;">94%</span></div>
                            </div>
                            <div style="text-align:center;padding:12px;background:rgba(255,255,255,0.04);border-radius:8px;">
                                <div style="font-size:13px;opacity:0.6;margin-bottom:6px;">数据库</div>
                                <div style="width:60px;height:60px;border-radius:50%;border:4px solid {c2};border-top-color:transparent;margin:0 auto;display:flex;align-items:center;justify-content:center;"><span style="font-size:14px;font-weight:bold;">87%</span></div>
                            </div>
                            <div style="text-align:center;padding:12px;background:rgba(255,255,255,0.04);border-radius:8px;">
                                <div style="font-size:13px;opacity:0.6;margin-bottom:6px;">缓存层</div>
                                <div style="width:60px;height:60px;border-radius:50%;border:4px solid {c3};border-top-color:transparent;margin:0 auto;display:flex;align-items:center;justify-content:center;"><span style="font-size:14px;font-weight:bold;">98%</span></div>
                            </div>
                            <div style="text-align:center;padding:12px;background:rgba(255,255,255,0.04);border-radius:8px;">
                                <div style="font-size:13px;opacity:0.6;margin-bottom:6px;">消息队列</div>
                                <div style="width:60px;height:60px;border-radius:50%;border:4px solid {c4};border-top-color:transparent;margin:0 auto;display:flex;align-items:center;justify-content:center;"><span style="font-size:14px;font-weight:bold;">91%</span></div>
                            </div>
                        </div>
                    </div>
                    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;">
                        <div style="font-weight:bold;margin-bottom:10px;">最近登录</div>
                        <div style="display:flex;flex-direction:column;gap:8px;font-size:13px;">
                            <div style="display:flex;justify-content:space-between;"><span>admin@corp.com</span><span style="opacity:0.5;">14:32 北京</span></div>
                            <div style="display:flex;justify-content:space-between;"><span>dev@corp.com</span><span style="opacity:0.5;">14:28 上海</span></div>
                            <div style="display:flex;justify-content:space-between;"><span>ops@corp.com</span><span style="opacity:0.5;">14:15 深圳</span></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>''',

        # 6. Trading Terminal: 订单簿 + K线 + 持仓
        f'''<div style="height:100%;display:flex;flex-direction:column;padding:30px;font-size:15px;gap:14px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-size:28px;font-weight:bold;">{name} 交易终端</div>
                <div style="display:flex;gap:10px;">
                    <span style="padding:6px 12px;background:rgba(255,255,255,0.06);border-radius:6px;font-size:13px;">BTC/USDT</span>
                    <span style="padding:6px 12px;background:rgba(255,255,255,0.06);border-radius:6px;font-size:13px;">ETH/USDT</span>
                    <span style="padding:6px 12px;background:{c1};border-radius:6px;font-size:13px;font-weight:bold;">SOL/USDT</span>
                </div>
            </div>
            <div style="flex:1;display:grid;grid-template-columns:280px 1fr 280px;gap:14px;min-height:0;">
                <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:16px;display:flex;flex-direction:column;overflow:hidden;">
                    <div style="font-weight:bold;margin-bottom:10px;">订单簿</div>
                    <div style="display:flex;justify-content:space-between;font-size:12px;opacity:0.6;margin-bottom:6px;"><span>价格</span><span>数量</span></div>
                    <div style="flex:1;overflow:auto;display:flex;flex-direction:column;gap:2px;font-size:13px;font-family:monospace;">
                        {''.join([f'<div style="display:flex;justify-content:space-between;padding:3px 6px;background:rgba(255,255,255,0.03);"><span style="color:{c4};">{98.5-i*0.1:.1f}</span><span>{1200+i*45}</span></div>' for i in range(8)])}
                        <div style="text-align:center;padding:6px;font-size:18px;font-weight:bold;color:{c1};">98.42 ▲0.8%</div>
                        {''.join([f'<div style="display:flex;justify-content:space-between;padding:3px 6px;background:rgba(255,255,255,0.03);"><span style="color:{c3};">{98.4+i*0.1:.1f}</span><span>{800+i*30}</span></div>' for i in range(8)])}
                    </div>
                </div>
                <div style="display:flex;flex-direction:column;gap:14px;">
                    <div style="flex:1;background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;display:flex;flex-direction:column;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:10px;"><span style="font-weight:bold;">SOL/USDT 15分钟</span><span style="font-size:20px;font-weight:bold;color:{c1};">$98.42</span></div>
                        <div style="flex:1;display:flex;flex-direction:column;justify-content:flex-end;gap:3px;padding:0 20px;">
                            <div style="display:flex;align-items:flex-end;gap:3px;height:70%;">
                                {''.join([f'<div style="flex:1;background:{c4 if i%7==0 else c3 if i%5==0 else c1};border-radius:2px 2px 0 0;height:{20+int((i*17)%80)}%;"></div>' for i in range(24)])}
                            </div>
                            <div style="display:flex;justify-content:space-between;font-size:11px;opacity:0.4;margin-top:4px;"><span>10:00</span><span>12:00</span><span>14:00</span></div>
                        </div>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                        <div style="padding:14px;background:{c3};border-radius:10px;text-align:center;font-weight:bold;font-size:18px;">买入</div>
                        <div style="padding:14px;background:{c4};border-radius:10px;text-align:center;font-weight:bold;font-size:18px;">卖出</div>
                    </div>
                </div>
                <div style="display:flex;flex-direction:column;gap:14px;">
                    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:16px;">
                        <div style="font-weight:bold;margin-bottom:10px;">资产概览</div>
                        <div style="font-size:28px;font-weight:bold;color:{c1};margin-bottom:10px;">$142,580</div>
                        <div style="display:flex;flex-direction:column;gap:6px;font-size:13px;">
                            <div style="display:flex;justify-content:space-between;"><span>SOL</span><span>850 ($83,617)</span></div>
                            <div style="display:flex;justify-content:space-between;"><span>BTC</span><span>0.45 ($38,250)</span></div>
                            <div style="display:flex;justify-content:space-between;"><span>USDT</span><span>20,713</span></div>
                        </div>
                    </div>
                    <div style="flex:1;background:rgba(255,255,255,0.04);border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:8px;overflow:hidden;">
                        <div style="font-weight:bold;margin-bottom:4px;">当前持仓</div>
                        <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;font-size:13px;"><div style="display:flex;justify-content:space-between;"><span>SOL 做多 5x</span><span style="color:{c3};">+12.5%</span></div><div style="font-size:11px;opacity:0.5;margin-top:2px;">开仓 87.32 | 强平 72.15</div></div>
                        <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;font-size:13px;"><div style="display:flex;justify-content:space-between;"><span>BTC 现货</span><span style="color:{c3};">+8.2%</span></div><div style="font-size:11px;opacity:0.5;margin-top:2px;">成本 78,200 | 现价 85,000</div></div>
                        <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;font-size:13px;"><div style="display:flex;justify-content:space-between;"><span>ETH 做空 3x</span><span style="color:{c4};">-3.1%</span></div><div style="font-size:11px;opacity:0.5;margin-top:2px;">开仓 3,850 | 强平 4,620</div></div>
                    </div>
                </div>
            </div>
        </div>''',

        # 7. Project Hub: 甘特图 + 看板 + 里程碑
        f'''<div style="height:100%;display:flex;flex-direction:column;padding:30px;font-size:15px;gap:14px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-size:28px;font-weight:bold;">{name} 项目协作</div>
                <div style="display:flex;gap:8px;">
                    <span style="padding:6px 12px;background:rgba(255,255,255,0.06);border-radius:6px;font-size:13px;">周视图</span>
                    <span style="padding:6px 12px;background:{c1};border-radius:6px;font-size:13px;font-weight:bold;">月视图</span>
                </div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;">
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:12px;text-align:center;"><div style="font-size:11px;opacity:0.6;">总任务</div><div style="font-size:22px;font-weight:bold;color:{c1};">128</div></div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:12px;text-align:center;"><div style="font-size:11px;opacity:0.6;">进行中</div><div style="font-size:22px;font-weight:bold;color:{c2};">45</div></div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:12px;text-align:center;"><div style="font-size:11px;opacity:0.6;">已完成</div><div style="font-size:22px;font-weight:bold;color:{c3};">72</div></div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:12px;text-align:center;"><div style="font-size:11px;opacity:0.6;">延期</div><div style="font-size:22px;font-weight:bold;color:{c4};">8</div></div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:12px;text-align:center;"><div style="font-size:11px;opacity:0.6;">完成率</div><div style="font-size:22px;font-weight:bold;color:{c5};">62%</div></div>
            </div>
            <div style="flex:1;display:grid;grid-template-columns:1fr 1fr;gap:14px;min-height:0;">
                <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;display:flex;flex-direction:column;overflow:hidden;">
                    <div style="font-weight:bold;margin-bottom:12px;">项目甘特图</div>
                    <div style="flex:1;overflow:auto;display:flex;flex-direction:column;gap:8px;">
                        {''.join([
                            f'<div style="display:flex;align-items:center;gap:10px;font-size:13px;"><div style="width:100px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{task}</div><div style="flex:1;height:22px;background:rgba(255,255,255,0.04);border-radius:4px;position:relative;"><div style="position:absolute;left:{i*8}%;width:{30+(i*12)%45}%;height:100%;background:{color};border-radius:4px;opacity:0.8;"></div></div><span style="width:40px;text-align:right;opacity:0.6;">{i+1}周</span></div>'
                            for i, (task, color) in enumerate(zip(
                                ["需求分析","架构设计","核心开发","接口联调","测试验证","性能优化","部署上线","文档编写","培训推广","运维监控"],
                                [c1,c2,c3,c1,c2,c4,c3,c1,c5,c2]
                            ))
                        ])}
                    </div>
                </div>
                <div style="display:flex;flex-direction:column;gap:14px;">
                    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;flex:1;overflow:hidden;">
                        <div style="font-weight:bold;margin-bottom:12px;">看板</div>
                        <div style="display:flex;gap:10px;height:calc(100% - 30px);">
                            <div style="flex:1;background:rgba(255,255,255,0.03);border-radius:8px;padding:10px;display:flex;flex-direction:column;gap:8px;">
                                <div style="font-size:12px;opacity:0.6;text-align:center;">待处理 8</div>
                                {''.join([f'<div style="padding:10px;background:rgba(255,255,255,0.05);border-radius:6px;font-size:12px;border-left:3px solid {c4};">任务 #{i+1001}<br/><span style="opacity:0.5;">P{i%3+1}</span></div>' for i in range(3)])}
                            </div>
                            <div style="flex:1;background:rgba(255,255,255,0.03);border-radius:8px;padding:10px;display:flex;flex-direction:column;gap:8px;">
                                <div style="font-size:12px;opacity:0.6;text-align:center;">进行中 5</div>
                                {''.join([f'<div style="padding:10px;background:rgba(255,255,255,0.05);border-radius:6px;font-size:12px;border-left:3px solid {c2};">任务 #{i+1004}<br/><span style="opacity:0.5;">开发中</span></div>' for i in range(3)])}
                            </div>
                            <div style="flex:1;background:rgba(255,255,255,0.03);border-radius:8px;padding:10px;display:flex;flex-direction:column;gap:8px;">
                                <div style="font-size:12px;opacity:0.6;text-align:center;">已完成 12</div>
                                {''.join([f'<div style="padding:10px;background:rgba(255,255,255,0.05);border-radius:6px;font-size:12px;border-left:3px solid {c3};">任务 #{i+1007}<br/><span style="opacity:0.5;">已验收</span></div>' for i in range(3)])}
                            </div>
                        </div>
                    </div>
                    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;">
                        <div style="font-weight:bold;margin-bottom:10px;">里程碑</div>
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            {''.join([f'<div style="text-align:center;"><div style="width:40px;height:40px;border-radius:50%;background:{c1 if i<2 else c3 if i==2 else c4};display:flex;align-items:center;justify-content:center;margin:0 auto;font-size:16px;">{"✓" if i<2 else "⋯" if i==2 else "○"}</div><div style="font-size:11px;margin-top:6px;opacity:0.7;">{m}</div></div>' for i, m in enumerate(["MVP","v1.0","v2.0","GA","v3.0"])])}
                        </div>
                    </div>
                </div>
            </div>
        </div>''',

        # 8. AI Lab: 模型卡 + 训练曲线 + 数据集
        f'''<div style="height:100%;display:flex;flex-direction:column;padding:30px;font-size:15px;gap:14px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-size:28px;font-weight:bold;">{name} AI实验室</div>
                <div style="display:flex;gap:8px;"><span style="padding:6px 12px;background:{c1};border-radius:6px;font-size:13px;">🚀 启动训练</span></div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;">
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;text-align:center;"><div style="font-size:11px;opacity:0.6;">训练轮次</div><div style="font-size:22px;font-weight:bold;color:{c1};">Epoch 142</div></div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;text-align:center;"><div style="font-size:11px;opacity:0.6;">Loss</div><div style="font-size:22px;font-weight:bold;color:{c2};">0.0234</div></div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;text-align:center;"><div style="font-size:11px;opacity:0.6;">Accuracy</div><div style="font-size:22px;font-weight:bold;color:{c3};">96.82%</div></div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px;text-align:center;"><div style="font-size:11px;opacity:0.6;">GPU利用率</div><div style="font-size:22px;font-weight:bold;color:{c4};">94%</div></div>
            </div>
            <div style="flex:1;display:grid;grid-template-columns:1.2fr 1fr;gap:14px;min-height:0;">
                <div style="display:flex;flex-direction:column;gap:14px;">
                    <div style="flex:1;background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;display:flex;flex-direction:column;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:10px;"><span style="font-weight:bold;">训练 Loss 曲线</span><span style="font-size:12px;opacity:0.5;">Batch / Loss</span></div>
                        <div style="flex:1;position:relative;">
                            <svg style="width:100%;height:100%;" viewBox="0 0 600 200" preserveAspectRatio="none">
                                <polyline points="{' '.join([f'{i*4},{180-int(160*(1-0.95/(1+i*0.05)))}' for i in range(150)])}" fill="none" stroke="{c1}" stroke-width="2"/>
                                <polyline points="{' '.join([f'{i*4},{180-int(160*(1-0.92/(1+i*0.03)))}' for i in range(150)])}" fill="none" stroke="{c2}" stroke-width="2" stroke-dasharray="4,4"/>
                            </svg>
                        </div>
                        <div style="display:flex;gap:20px;font-size:12px;justify-content:center;margin-top:6px;">
                            <span style="display:flex;align-items:center;gap:4px;"><div style="width:12px;height:3px;background:{c1};"></div>Train Loss</span>
                            <span style="display:flex;align-items:center;gap:4px;"><div style="width:12px;height:3px;background:{c2};"></div>Val Loss</span>
                        </div>
                    </div>
                    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;">
                        <div style="font-weight:bold;margin-bottom:10px;">超参数配置</div>
                        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;font-size:13px;">
                            <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:6px;"><div style="opacity:0.5;font-size:11px;">Learning Rate</div><div style="font-weight:bold;">1e-4</div></div>
                            <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:6px;"><div style="opacity:0.5;font-size:11px;">Batch Size</div><div style="font-weight:bold;">256</div></div>
                            <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:6px;"><div style="opacity:0.5;font-size:11px;">Optimizer</div><div style="font-weight:bold;">AdamW</div></div>
                            <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:6px;"><div style="opacity:0.5;font-size:11px;">Scheduler</div><div style="font-weight:bold;">Cosine</div></div>
                            <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:6px;"><div style="opacity:0.5;font-size:11px;">Dropout</div><div style="font-weight:bold;">0.15</div></div>
                            <div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:6px;"><div style="opacity:0.5;font-size:11px;">Weight Decay</div><div style="font-weight:bold;">0.01</div></div>
                        </div>
                    </div>
                </div>
                <div style="display:flex;flex-direction:column;gap:14px;">
                    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;flex:1;overflow:hidden;">
                        <div style="font-weight:bold;margin-bottom:10px;">GPU 资源监控</div>
                        <div style="display:flex;flex-direction:column;gap:10px;">
                            {''.join([f'<div><div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px;"><span>GPU-{i}</span><span>{[94,87,92,78][i%4]}%</span></div><div style="height:8px;background:rgba(255,255,255,0.06);border-radius:4px;"><div style="width:{[94,87,92,78][i%4]}%;height:100%;background:{c1 if i%4==0 else c2 if i%4==1 else c3 if i%4==2 else c4};border-radius:4px;"></div></div></div>' for i in range(4)])}
                        </div>
                        <div style="margin-top:14px;font-weight:bold;margin-bottom:8px;">实验记录</div>
                        <div style="display:flex;flex-direction:column;gap:6px;font-size:12px;overflow:auto;">
                            <div style="display:flex;justify-content:space-between;padding:8px;background:rgba(255,255,255,0.04);border-radius:6px;"><span>Exp-042</span><span style="color:{c3};">✓ 96.8%</span></div>
                            <div style="display:flex;justify-content:space-between;padding:8px;background:rgba(255,255,255,0.04);border-radius:6px;"><span>Exp-041</span><span style="color:{c3};">✓ 95.2%</span></div>
                            <div style="display:flex;justify-content:space-between;padding:8px;background:rgba(255,255,255,0.04);border-radius:6px;"><span>Exp-040</span><span style="color:{c4};">✗ 91.3%</span></div>
                            <div style="display:flex;justify-content:space-between;padding:8px;background:rgba(255,255,255,0.04);border-radius:6px;"><span>Exp-039</span><span style="color:{c3};">✓ 94.7%</span></div>
                        </div>
                    </div>
                    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;">
                        <div style="font-weight:bold;margin-bottom:10px;">数据集概览</div>
                        <div style="display:flex;gap:10px;">
                            <div style="flex:1;padding:12px;background:rgba(255,255,255,0.04);border-radius:8px;text-align:center;"><div style="font-size:20px;font-weight:bold;color:{c1};">125K</div><div style="font-size:11px;opacity:0.6;">训练样本</div></div>
                            <div style="flex:1;padding:12px;background:rgba(255,255,255,0.04);border-radius:8px;text-align:center;"><div style="font-size:20px;font-weight:bold;color:{c2};">15K</div><div style="font-size:11px;opacity:0.6;">验证样本</div></div>
                            <div style="flex:1;padding:12px;background:rgba(255,255,255,0.04);border-radius:8px;text-align:center;"><div style="font-size:20px;font-weight:bold;color:{c3};">8.2GB</div><div style="font-size:11px;opacity:0.6;">数据总量</div></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>''',

        # 9. IoT Dashboard: 设备地图 + 传感器 + 控制
        f'''<div style="height:100%;display:flex;flex-direction:column;padding:30px;font-size:15px;gap:14px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-size:28px;font-weight:bold;">{name} 物联控制台</div>
                <div style="display:flex;gap:8px;">
                    <span style="padding:6px 12px;background:rgba(255,255,255,0.06);border-radius:6px;font-size:13px;">🟢 在线 142</span>
                    <span style="padding:6px 12px;background:rgba(255,255,255,0.06);border-radius:6px;font-size:13px;">🟡 待机 18</span>
                    <span style="padding:6px 12px;background:rgba(255,255,255,0.06);border-radius:6px;font-size:13px;">🔴 离线 3</span>
                </div>
            </div>
            <div style="flex:1;display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;min-height:0;">
                <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;display:flex;flex-direction:column;overflow:hidden;">
                    <div style="font-weight:bold;margin-bottom:10px;">设备状态分布</div>
                    <div style="flex:1;display:grid;grid-template-columns:repeat(3,1fr);gap:8px;overflow:auto;">
                        {''.join([f'<div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;text-align:center;"><div style="font-size:20px;margin-bottom:4px;">{["🌡","⚡","💧","🌪","📡","🔒","💡","🔊","📹","🚪","🖥","📟"][i%12]}</div><div style="font-size:12px;opacity:0.7;">Device-{i+1}</div><div style="width:8px;height:8px;background:{c1 if i%10!=0 else c3};border-radius:50%;margin:4px auto;"></div><div style="font-size:11px;">{["28°C","220V","45%","12m/s","-68dBm","已锁","开","65dB","录像","关闭","在线","OK"][i%12]}</div></div>' for i in range(15)])}
                    </div>
                </div>
                <div style="display:flex;flex-direction:column;gap:14px;">
                    <div style="flex:1;background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;display:flex;flex-direction:column;">
                        <div style="font-weight:bold;margin-bottom:10px;">传感器读数趋势</div>
                        <div style="flex:1;display:flex;flex-direction:column;gap:10px;justify-content:center;">
                            {''.join([f'<div><div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px;"><span>{label}</span><span>{val}</span></div><div style="height:40px;display:flex;align-items:flex-end;gap:2px;">{''.join([f'<div style="flex:1;background:{c1 if j%3==0 else c2 if j%3==1 else c3};border-radius:1px;height:{15+int((j*17+i*23)%85)}%;"></div>' for j in range(20)])}</div></div>' for i, (label, val) in enumerate([("温度", "28.4°C"), ("湿度", "62%"), ("电压", "220.2V"), ("振动", "0.04g")])])}
                        </div>
                    </div>
                </div>
                <div style="display:flex;flex-direction:column;gap:14px;">
                    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;">
                        <div style="font-weight:bold;margin-bottom:10px;">快捷控制</div>
                        <div style="display:flex;flex-direction:column;gap:8px;">
                            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;"><span>主电源</span><div style="width:40px;height:22px;background:{c1};border-radius:11px;position:relative;"><div style="width:18px;height:18px;background:#fff;border-radius:50%;position:absolute;top:2px;right:2px;"></div></div></div>
                            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;"><span>照明系统</span><div style="width:40px;height:22px;background:{c1};border-radius:11px;position:relative;"><div style="width:18px;height:18px;background:#fff;border-radius:50%;position:absolute;top:2px;right:2px;"></div></div></div>
                            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;"><span>安防模式</span><div style="width:40px;height:22px;background:rgba(255,255,255,0.1);border-radius:11px;position:relative;"><div style="width:18px;height:18px;background:#fff;border-radius:50%;position:absolute;top:2px;left:2px;"></div></div></div>
                            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;"><span>节能模式</span><div style="width:40px;height:22px;background:{c1};border-radius:11px;position:relative;"><div style="width:18px;height:18px;background:#fff;border-radius:50%;position:absolute;top:2px;right:2px;"></div></div></div>
                        </div>
                    </div>
                    <div style="flex:1;background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;display:flex;flex-direction:column;gap:8px;overflow:hidden;">
                        <div style="font-weight:bold;margin-bottom:4px;">告警日志</div>
                        <div style="overflow:auto;display:flex;flex-direction:column;gap:6px;font-size:12px;">
                            <div style="padding:8px;background:rgba(255,255,255,0.04);border-radius:6px;border-left:3px solid {c3};"><span style="opacity:0.6;">14:32</span> 区域A温度超过阈值</div>
                            <div style="padding:8px;background:rgba(255,255,255,0.04);border-radius:6px;border-left:3px solid {c3};"><span style="opacity:0.6;">14:28</span> Device-07 信号弱</div>
                            <div style="padding:8px;background:rgba(255,255,255,0.04);border-radius:6px;border-left:3px solid {c1};"><span style="opacity:0.6;">14:15</span> 定时巡检完成</div>
                            <div style="padding:8px;background:rgba(255,255,255,0.04);border-radius:6px;border-left:3px solid {c3};"><span style="opacity:0.6;">14:02</span> 备用电源切换</div>
                            <div style="padding:8px;background:rgba(255,255,255,0.04);border-radius:6px;border-left:3px solid {c1};"><span style="opacity:0.6;">13:45</span> 固件更新成功</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>''',
    ]

    return f'''<div style="width:1920px;height:1080px;background:{theme["bg"]};color:{theme["text"]};font-family:'Microsoft YaHei',sans-serif;overflow:hidden;">
    {layouts[index % len(layouts)]}
</div>'''



# Chart dispatch map
CHART_FUNCTIONS = {
    "图1-1": lambda d, t: org_chart(d, t),
    "图1-2": lambda d, t: strategy_roadmap(d, t),
    "图1-3": lambda d, t: swot(d, t),
    "图1-4": lambda d, t: porter_six(d, t),
    "图1-5": lambda d, t: rd_roadmap(d, t),
    "图1-6": lambda d, t: product_matrix(d, t),
    "图1-7": lambda d, t: layered_arch(d, t, "service_arch", "服务体系架构"),
    "图1-8": lambda d, t: funnel(d, t),
    "图1-9": lambda d, t: business_canvas(d, t),
    "图2-1": lambda d, t: flowchart(d, t, "industry_chain", "行业产业链"),
    "图2-2": lambda d, t: market_growth(d, t),
    "图2-3": lambda d, t: policy_timeline(d, t),
    "图2-4": lambda d, t: layered_arch(d, t, "product_func_arch", "产品功能架构"),
    "图2-5": lambda d, t: layered_arch(d, t, "tech_arch", "系统技术架构"),
    "图2-6": lambda d, t: flowchart(d, t, "algorithm_flow", "核心算法流程"),
    "图2-7": lambda d, t: product_screenshot(d, t, 0),
    "图2-8": lambda d, t: product_screenshot(d, t, 1),
    "图2-9": lambda d, t: product_screenshot(d, t, 2),
    "图2-10": lambda d, t: product_screenshot(d, t, 3),
    "图2-11": lambda d, t: personas(d, t),
    "图2-12": lambda d, t: customer_radar(d, t),
    "图2-13": lambda d, t: product_comparison(d, t),
    "图2-14": lambda d, t: product_screenshot(d, t, 4),
    "图2-15": lambda d, t: effect_bar(d, t),
    "图2-16": lambda d, t: market_share(d, t),
    "图2-17": lambda d, t: quadrant(d, t, "competition_scatter", "行业竞争格局"),
    "图2-18": lambda d, t: revenue_donut(d, t),
    "图2-19": lambda d, t: revenue_growth(d, t),
    "图2-20": lambda d, t: quadrant(d, t, "competition_matrix", "竞争格局矩阵"),
    "图2-21": lambda d, t: customer_radar(d, t),
    "图3-1": lambda d, t: funding_use(d, t),
    "图3-2": lambda d, t: financing_milestone(d, t),
    "图4-1": lambda d, t: risk_matrix(d, t),
}

FIG_TO_FILENAME = {
    "图1-1": "图1_1.png", "图1-2": "图1_2.png", "图1-3": "图1_3.png", "图1-4": "图1_4.png",
    "图1-5": "图1_5.png", "图1-6": "图1_6.png", "图1-7": "图1_7.png", "图1-8": "图1_8.png",
    "图1-9": "图1_9.png", "图2-1": "图2_1.png", "图2-2": "图2_2.png", "图2-3": "图2_3.png",
    "图2-4": "图2_4.png", "图2-5": "图2_5.png", "图2-6": "图2_6.png", "图2-7": "图2_7.png",
    "图2-8": "图2_8.png", "图2-9": "图2_9.png", "图2-10": "图2_10.png", "图2-11": "图2_11.png",
    "图2-12": "图2_12.png", "图2-13": "图2_13.png", "图2-14": "图2_14.png", "图2-15": "图2_15.png",
    "图2-16": "图2_16.png", "图2-17": "图2_17.png", "图2-18": "图2_18.png", "图2-19": "图2_19.png",
    "图2-20": "图2_20.png", "图2-21": "图2_21.png", "图3-1": "图3_1.png", "图3-2": "图3_2.png",
    "图4-1": "图4_1.png",
}
