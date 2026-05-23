#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
visual_chart_engine.py
为商业计划书生成62种视觉上互不相同的图表。

每种图表使用不同的可视化方式：
- matplotlib: 柱状图、折线图、饼图、散点图、雷达图、面积图、热力图等
- Pillow: 组织架构图、时间线、流程图、矩阵、九宫格等
- screenshot.py: 产品UI截图
- ppt_diagram_engine: 仅用于真正复杂的架构图(最多3-4张)

核心原则：同一份DOCX中的73张图必须视觉上互不相同。
"""

import os, json, random, math, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# 莫兰迪配色
MORANDI_COLORS = [
    '#A8DADC', '#457B9D', '#E63946', '#F1FAEE', '#1D3557',
    '#B8C0D0', '#D8A48F', '#A3B18A', '#C9ADA7', '#9A8C98',
    '#F2E9E4', '#CDB4DB', '#FFC8DD', '#BDE0FE', '#A2D2FF',
    '#CBF3F0', '#FFBF69', '#FF9F1C', '#2EC4B6', '#E71D36',
    '#8E9AAF', '#CBC0D3', '#EFD3D7', '#D8E2DC', '#B7B7A4',
    '#C1D6C7', '#E8CFCF', '#CFD6E8', '#E8E0CF', '#A2A392',
]

FONT_PATH = r'C:\Windows\Fonts\msyh.ttc'
FONT_BOLD = r'C:\Windows\Fonts\msyhbd.ttc'

def _font(size=24, bold=False):
    try:
        return ImageFont.truetype(FONT_BOLD if bold else FONT_PATH, size)
    except:
        return ImageFont.load_default()

def _mpl_font():
    return {'family': 'Microsoft YaHei', 'size': 14}

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================
# Pillow-based 图表 (直接绘制，每张视觉上都不同)
# ============================================================

def draw_org_chart(title, output_path, W=2400, H=1600):
    """组织架构图 - 树形层次结构"""
    img = Image.new('RGB', (W, H), '#FAFAFA')
    draw = ImageDraw.Draw(img)

    # 标题
    font_t = _font(36, True)
    font_b = _font(22)
    font_s = _font(18)
    draw.text((W//2, 30), title, fill='#2D3436', font=font_t, anchor='mt')

    # 层次结构
    levels = [
        [('总经理', W//2, 120)],
        [('技术总监', W//4), ('运营总监', W//2), ('财务总监', 3*W//4)],
        [('研发部', W//8), ('测试部', 3*W//8), ('市场部', 5*W//8), ('行政部', 7*W//8)],
        [('前端组', W//16), ('后端组', 3*W//16), ('AI组', 5*W//16), ('运维组', 7*W//16),
         ('销售组', 9*W//16), ('客服组', 11*W//16), ('人事组', 13*W//16), ('财务组', 15*W//16)],
    ]

    box_w, box_h = 140, 50
    y_positions = [160, 300, 440, 580]

    for li, level in enumerate(levels):
        y = y_positions[li]
        for name, x, *_ in level:
            x2 = x if len(str(x)) > 3 else x
            colors = ['#457B9D', '#A8DADC', '#E63946', '#F1FAEE']
            color = colors[li % len(colors)]
            draw.rounded_rectangle([x2-box_w//2, y, x2+box_w//2, y+box_h],
                                   radius=8, fill=color, outline='#2D3436')
            tw = draw.textlength(name, font=font_s)
            draw.text((x2 - tw//2, y + box_h//2 - 10), name, fill='white' if li < 2 else '#2D3436', font=font_s)

    # 连线
    for li in range(len(levels)-1):
        for name_p, x_p, *_ in levels[li]:
            yp = y_positions[li] + box_h
            for name_c, x_c, *_ in levels[li+1]:
                yc = y_positions[li+1]
                # 简单垂直连线
                if abs(x_p - x_c) < W // (2 ** li + 1):
                    draw.line([(x_p, yp), (x_c, yc)], fill='#636E72', width=2)

    img.save(output_path, quality=95)


def draw_timeline(title, phases, output_path, W=2400, H=1000):
    """时间线/路线图 - 水平时间轴"""
    img = Image.new('RGB', (W, H), '#FAFAFA')
    draw = ImageDraw.Draw(img)
    font_t = _font(32, True)
    font_b = _font(20)
    font_s = _font(16)

    draw.text((W//2, 25), title, fill='#2D3436', font=font_t, anchor='mt')

    # 主时间线
    line_y = 350
    margin = 150
    draw.line([(margin, line_y), (W-margin, line_y)], fill='#457B9D', width=4)

    n = len(phases)
    spacing = (W - 2*margin) // max(n-1, 1)

    for i, phase in enumerate(phases):
        x = margin + i * spacing
        color = MORANDI_COLORS[i % len(MORANDI_COLORS)]

        # 圆点
        r = 18
        draw.ellipse([x-r, line_y-r, x+r, line_y+r], fill=color, outline='#2D3436')

        # 上方：阶段名
        name = phase.get('name', f'阶段{i+1}')
        tw = draw.textlength(name, font=font_b)
        draw.text((x - tw//2, line_y - 80), name, fill='#2D3436', font=font_b)

        # 下方：时间
        duration = phase.get('duration_months', 3)
        draw.text((x - 30, line_y + 30), f'{duration}个月', fill='#636E72', font=font_s)

        # 连接线到文字
        draw.line([(x, line_y-r), (x, line_y-50)], fill='#636E72', width=2)

    img.save(output_path, quality=95)


def draw_flowchart(title, steps, output_path, W=2400, H=1200):
    """流程图 - 水平/垂直流程"""
    img = Image.new('RGB', (W, H), '#FAFAFA')
    draw = ImageDraw.Draw(img)
    font_t = _font(32, True)
    font_b = _font(22)
    font_s = _font(16)

    draw.text((W//2, 25), title, fill='#2D3436', font=font_t, anchor='mt')

    n = len(steps)
    cols = min(n, 5)
    rows = math.ceil(n / cols)
    box_w, box_h = 320, 80
    gap_x, gap_y = 80, 60
    start_x = (W - cols * (box_w + gap_x) + gap_x) // 2
    start_y = 120

    for i, step in enumerate(steps):
        r, c = divmod(i, cols)
        x = start_x + c * (box_w + gap_x)
        y = start_y + r * (box_h + gap_y)
        color = MORANDI_COLORS[i % len(MORANDI_COLORS)]

        # 圆角矩形
        draw.rounded_rectangle([x, y, x+box_w, y+box_h], radius=12, fill=color, outline='#636E72')

        # 文字
        name = step if isinstance(step, str) else step.get('name', f'步骤{i+1}')
        lines = textwrap.wrap(name, width=12)
        for li, line in enumerate(lines[:3]):
            tw = draw.textlength(line, font=font_s)
            draw.text((x + (box_w - tw)//2, y + 15 + li*22), line, fill='#2D3436', font=font_s)

        # 箭头
        if i < n - 1:
            next_r, next_c = divmod(i+1, cols)
            nx = start_x + next_c * (box_w + gap_x)
            ny = start_y + next_r * (box_h + gap_y)
            # 简单箭头
            ax, ay = x + box_w, y + box_h // 2
            if next_c > c:  # 右箭头
                bx, by = nx, ny + box_h // 2
                draw.line([(ax, ay), (bx, by)], fill='#457B9D', width=3)
                draw.polygon([(bx, by), (bx-12, by-8), (bx-12, by+8)], fill='#457B9D')
            elif next_r > r:  # 下方箭头
                bx, by = x + box_w//2, ny
                draw.line([(x+box_w//2, y+box_h), (bx, by)], fill='#457B9D', width=3)

    img.save(output_path, quality=95)


def draw_matrix(title, rows_labels, cols_labels, data, output_path, W=2000, H=1400):
    """矩阵图 - 网格热力图"""
    fig, ax = plt.subplots(figsize=(W/100, H/100), dpi=100)
    ax.set_title(title, fontsize=20, fontweight='bold', pad=20)

    arr = np.array(data)
    im = ax.imshow(arr, cmap='RdYlGn', aspect='auto')

    ax.set_xticks(range(len(cols_labels)))
    ax.set_yticks(range(len(rows_labels)))
    ax.set_xticklabels(cols_labels, fontsize=12)
    ax.set_yticklabels(rows_labels, fontsize=12)

    for i in range(len(rows_labels)):
        for j in range(len(cols_labels)):
            ax.text(j, i, f'{arr[i,j]:.0f}%', ha='center', va='center', fontsize=11, fontweight='bold')

    fig.colorbar(im, ax=ax, shrink=0.8)
    plt.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def draw_funnel(title, stages, output_path, W=1600, H=1200):
    """漏斗图"""
    img = Image.new('RGB', (W, H), '#FAFAFA')
    draw = ImageDraw.Draw(img)
    font_t = _font(32, True)
    font_b = _font(22)

    draw.text((W//2, 25), title, fill='#2D3436', font=font_t, anchor='mt')

    n = len(stages)
    cy = H // 2 + 30
    max_w = W - 200
    h_per = (H - 200) // n

    for i, (name, pct) in enumerate(stages):
        w = int(max_w * (pct / 100))
        x1 = (W - w) // 2
        y1 = 100 + i * h_per
        x2 = x1 + w
        y2 = y1 + h_per - 10
        color = MORANDI_COLORS[i % len(MORANDI_COLORS)]

        # 梯形
        shrink = 30
        points = [(x1 + shrink, y1), (x2 - shrink, y1), (x2, y2), (x1, y2)]
        draw.polygon(points, fill=color, outline='#636E72')

        tw = draw.textlength(f'{name} ({pct}%)', font=font_b)
        draw.text(((x1+x2)//2 - tw//2, (y1+y2)//2 - 12), f'{name} ({pct}%)',
                  fill='white' if i < 3 else '#2D3436', font=font_b)

    img.save(output_path, quality=95)


def draw_ninebox(title, cells, output_path, W=2400, H=1600):
    """九宫格 (商业画布/BMC)"""
    img = Image.new('RGB', (W, H), '#FAFAFA')
    draw = ImageDraw.Draw(img)
    font_t = _font(30, True)
    font_l = _font(18, True)
    font_s = _font(15)

    draw.text((W//2, 20), title, fill='#2D3436', font=font_t, anchor='mt')

    # BMC 9-cell layout
    labels = ['关键伙伴', '关键活动', '价值主张', '客户关系', '客户细分',
              '', '关键资源', '', '渠道', '']
    if cells:
        labels = cells

    # 3x3 grid with merged cells for center
    col_w = [W//5, W//5, W//5*2, W//5, W//5]
    row_h = [H//3-40, H//3-40, H//3-40]

    bmc_layout = [
        # row 0: 5 columns
        [(0, 0, 1, 1), (1, 0, 1, 1), (2, 0, 1, 2), (3, 0, 1, 1), (4, 0, 1, 1)],
        # row 1: 4 columns (center merged)
        [(0, 1, 1, 1), (1, 1, 1, 1), None, (3, 1, 1, 1), (4, 1, 1, 1)],
        # row 2: 3 columns
        [(0, 2, 2, 1), None, (2, 2, 1, 1), (3, 2, 2, 1), None],
    ]

    # Simple 3x3 grid
    gx, gy = 30, 80
    gw = (W - 2*gx) // 3
    gh = (H - gy - 30) // 3

    for i, label in enumerate(labels[:9]):
        r, c = divmod(i, 3)
        x = gx + c * gw
        y = gy + r * gh
        color = MORANDI_COLORS[i % len(MORANDI_COLORS)]

        draw.rounded_rectangle([x+3, y+3, x+gw-3, y+gh-3], radius=10, fill=color, outline='#636E72')
        # Label
        lines = label.split('\n') if '\n' in label else textwrap.wrap(label, width=10)
        for li, line in enumerate(lines[:5]):
            tw = draw.textlength(line, font=font_s)
            draw.text((x + (gw-tw)//2, y + 25 + li*22), line, fill='#2D3436', font=font_s)

    img.save(output_path, quality=95)


def draw_radar(title, labels, values, output_path, W=1400, H=1400):
    """雷达图/蜘蛛图"""
    fig, ax = plt.subplots(figsize=(W/100, H/100), dpi=100, subplot_kw=dict(polar=True))

    n = len(labels)
    angles = np.linspace(0, 2*np.pi, n, endpoint=False).tolist()
    values_plot = values + [values[0]]
    angles += [angles[0]]

    ax.fill(angles, values_plot, color='#A8DADC', alpha=0.3)
    ax.plot(angles, values_plot, color='#457B9D', linewidth=2, marker='o')

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=13)
    ax.set_ylim(0, 100)
    ax.set_title(title, fontsize=18, fontweight='bold', pad=30)

    plt.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def draw_bar_chart(title, categories, values, output_path, W=1600, H=1000,
                   horizontal=False, stacked=False, color_list=None):
    """柱状图（垂直/水平/堆叠）"""
    fig, ax = plt.subplots(figsize=(W/100, H/100), dpi=100)
    ax.set_title(title, fontsize=18, fontweight='bold', pad=15)

    colors = color_list or [MORANDI_COLORS[i % len(MORANDI_COLORS)] for i in range(len(categories))]

    if horizontal:
        bars = ax.barh(categories, values, color=colors)
        ax.set_xlabel('数值', fontsize=12)
    else:
        bars = ax.bar(categories, values, color=colors)
        ax.set_ylabel('数值', fontsize=12)

    for bar, val in zip(bars if not stacked else [bars], values if not stacked else [values]):
        if not stacked:
            if horizontal:
                ax.text(bar.get_width() + max(values)*0.02, bar.get_y() + bar.get_height()/2,
                        f'{val}', va='center', fontsize=11)
            else:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.02,
                        f'{val}', ha='center', fontsize=11)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def draw_line_chart(title, x_labels, y_series, legend_labels, output_path, W=1600, H=1000):
    """折线图"""
    fig, ax = plt.subplots(figsize=(W/100, H/100), dpi=100)
    ax.set_title(title, fontsize=18, fontweight='bold', pad=15)

    for i, (ys, label) in enumerate(zip(y_series, legend_labels)):
        color = MORANDI_COLORS[i % len(MORANDI_COLORS)]
        ax.plot(x_labels, ys, marker='o', color=color, linewidth=2.5, label=label)

    ax.legend(fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def draw_pie_chart(title, labels, sizes, output_path, W=1400, H=1000):
    """饼图"""
    fig, ax = plt.subplots(figsize=(W/100, H/100), dpi=100)
    ax.set_title(title, fontsize=18, fontweight='bold', pad=15)

    colors = [MORANDI_COLORS[i % len(MORANDI_COLORS)] for i in range(len(labels))]
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                       autopct='%1.1f%%', startangle=90,
                                       textprops={'fontsize': 12})
    for t in autotexts:
        t.set_fontsize(11)
        t.set_fontweight('bold')

    plt.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def draw_scatter(title, x_data, y_data, labels, output_path, W=1600, H=1200):
    """散点图（竞争格局等）"""
    fig, ax = plt.subplots(figsize=(W/100, H/100), dpi=100)
    ax.set_title(title, fontsize=18, fontweight='bold', pad=15)

    colors = [MORANDI_COLORS[i % len(MORANDI_COLORS)] for i in range(len(labels))]
    sizes_scatter = [max(200, s*5) for s in y_data]

    ax.scatter(x_data, y_data, s=sizes_scatter, c=colors, alpha=0.7, edgecolors='#2D3436')

    for i, label in enumerate(labels):
        ax.annotate(label, (x_data[i], y_data[i]), fontsize=11,
                    ha='center', va='bottom', textcoords='offset points', xytext=(0, 10))

    ax.set_xlabel('市场占有率 (%)', fontsize=12)
    ax.set_ylabel('创新能力', fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def draw_area_chart(title, x_labels, y_series, legend_labels, output_path, W=1600, H=1000):
    """面积图"""
    fig, ax = plt.subplots(figsize=(W/100, H/100), dpi=100)
    ax.set_title(title, fontsize=18, fontweight='bold', pad=15)

    for i, (ys, label) in enumerate(zip(y_series, legend_labels)):
        color = MORANDI_COLORS[i % len(MORANDI_COLORS)]
        ax.fill_between(x_labels, ys, alpha=0.3, color=color)
        ax.plot(x_labels, ys, color=color, linewidth=2, label=label)

    ax.legend(fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def draw_comparison_table(title, headers, rows, output_path, W=2000, H=1200):
    """对比表格图"""
    fig, ax = plt.subplots(figsize=(W/100, H/100), dpi=100)
    ax.set_title(title, fontsize=18, fontweight='bold', pad=15)
    ax.axis('off')

    cell_text = [[str(c) for c in row] for row in rows]
    table = ax.table(cellText=cell_text, colLabels=headers, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 2)

    # 表头颜色
    for j in range(len(headers)):
        table[0, j].set_facecolor('#457B9D')
        table[0, j].set_text_props(color='white', fontweight='bold')

    for i in range(1, len(rows)+1):
        for j in range(len(headers)):
            color = '#F1FAEE' if i % 2 == 0 else '#FFFFFF'
            table[i, j].set_facecolor(color)

    plt.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def draw_layered_arch(title, layers, output_path, W=2400, H=1400):
    """分层架构图 - 每层不同颜色和内容"""
    img = Image.new('RGB', (W, H), '#FAFAFA')
    draw = ImageDraw.Draw(img)
    font_t = _font(30, True)
    font_b = _font(20)
    font_s = _font(16)

    draw.text((W//2, 20), title, fill='#2D3436', font=font_t, anchor='mt')

    n = len(layers)
    margin_x = 80
    gap = 12
    layer_h = (H - 120 - gap * n) // n
    start_y = 80

    for i, (layer_name, items) in enumerate(layers):
        y = start_y + i * (layer_h + gap)
        color = MORANDI_COLORS[i % len(MORANDI_COLORS)]

        # 层背景
        draw.rounded_rectangle([margin_x, y, W-margin_x, y+layer_h],
                               radius=10, fill=color, outline='#636E72', width=1)

        # 层名称
        draw.text((margin_x + 15, y + 8), layer_name, fill='#2D3436', font=font_b)

        # 子项目
        if items:
            item_w = (W - 2*margin_x - 40) // min(len(items), 5)
            for j, item in enumerate(items[:5]):
                ix = margin_x + 20 + j * item_w
                iy = y + 40
                iw = item_w - 10
                ih = layer_h - 55
                draw.rounded_rectangle([ix, iy, ix+iw, iy+ih],
                                       radius=6, fill='white', outline='#B2BEC3')
                lines = textwrap.wrap(str(item), width=8)
                for li, line in enumerate(lines[:3]):
                    tw = draw.textlength(line, font=font_s)
                    draw.text((ix + (iw-tw)//2, iy + 10 + li*20), line, fill='#2D3436', font=font_s)

        # 向下箭头
        if i < n - 1:
            ax = W // 2
            ay = y + layer_h
            draw.polygon([(ax, ay+gap), (ax-8, ay+2), (ax+8, ay+2)], fill='#636E72')

    img.save(output_path, quality=95)


def draw_gantt_pillow(title, phases, output_path, W=2400, H=1000):
    """甘特图 - Pillow版"""
    img = Image.new('RGB', (W, H), '#FAFAFA')
    draw = ImageDraw.Draw(img)
    font_t = _font(28, True)
    font_b = _font(18)
    font_s = _font(14)

    draw.text((W//2, 15), title, fill='#2D3436', font=font_t, anchor='mt')

    n = len(phases)
    left_margin = 250
    right_margin = 60
    top = 70
    bar_h = 35
    gap = 15
    chart_w = W - left_margin - right_margin

    max_month = max(p.get('start_month', 1) + p.get('duration_months', 3) for p in phases) + 2

    # 月份刻度
    for m in range(0, int(max_month)+1, 3):
        x = left_margin + int(m / max_month * chart_w)
        draw.line([(x, top), (x, top + n*(bar_h+gap))], fill='#DFE6E9', width=1)
        draw.text((x, top + n*(bar_h+gap) + 5), f'M{m}', fill='#636E72', font=font_s)

    for i, phase in enumerate(phases):
        y = top + i * (bar_h + gap)
        name = phase.get('name', f'阶段{i+1}')
        start = phase.get('start_month', 1)
        dur = phase.get('duration_months', 3)
        color = MORANDI_COLORS[i % len(MORANDI_COLORS)]

        # 名称
        draw.text((left_margin - 10, y + bar_h//2 - 10), name, fill='#2D3436', font=font_b, anchor='rt')

        # 条形
        bx1 = left_margin + int(start / max_month * chart_w)
        bx2 = left_margin + int((start + dur) / max_month * chart_w)
        draw.rounded_rectangle([bx1, y, bx2, y+bar_h], radius=6, fill=color, outline='#636E72')

        # 持续时间
        draw.text(((bx1+bx2)//2, y+bar_h//2), f'{dur}月', fill='white', font=font_s, anchor='mm')

    img.save(output_path, quality=95)


def draw_hexagon_grid(title, items, output_path, W=1600, H=1200):
    """六边形网格图"""
    img = Image.new('RGB', (W, H), '#FAFAFA')
    draw = ImageDraw.Draw(img)
    font_t = _font(28, True)
    font_s = _font(14)

    draw.text((W//2, 20), title, fill='#2D3436', font=font_t, anchor='mt')

    n = len(items)
    cols = min(n, 4)
    rows = math.ceil(n / cols)
    hex_r = 80
    start_x = W // 2
    start_y = 160

    def hex_points(cx, cy, r):
        return [(cx + r * math.cos(math.pi/3 * i - math.pi/6),
                 cy + r * math.sin(math.pi/3 * i - math.pi/6)) for i in range(6)]

    for i, item in enumerate(items):
        r, c = divmod(i, cols)
        cx = 200 + c * 320
        cy = start_y + r * 200
        color = MORANDI_COLORS[i % len(MORANDI_COLORS)]

        pts = hex_points(cx, cy, hex_r)
        draw.polygon(pts, fill=color, outline='#636E72')

        name = item if isinstance(item, str) else item.get('name', '')
        lines = textwrap.wrap(name, width=6)
        for li, line in enumerate(lines[:3]):
            tw = draw.textlength(line, font=font_s)
            draw.text((cx - tw//2, cy - 15 + li*20), line, fill='white', font=font_s)

    img.save(output_path, quality=95)


def draw_stacked_bar(title, categories, series_data, series_names, output_path, W=1600, H=1000):
    """堆叠柱状图"""
    fig, ax = plt.subplots(figsize=(W/100, H/100), dpi=100)
    ax.set_title(title, fontsize=18, fontweight='bold', pad=15)

    x = np.arange(len(categories))
    width = 0.6
    bottom = np.zeros(len(categories))

    for i, (data, name) in enumerate(zip(series_data, series_names)):
        color = MORANDI_COLORS[i % len(MORANDI_COLORS)]
        ax.bar(x, data, width, bottom=bottom, label=name, color=color)
        bottom += np.array(data)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=12)
    ax.legend(fontsize=11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def draw_donut(title, labels, sizes, output_path, W=1400, H=1000):
    """环形图"""
    fig, ax = plt.subplots(figsize=(W/100, H/100), dpi=100)
    ax.set_title(title, fontsize=18, fontweight='bold', pad=15)

    colors = [MORANDI_COLORS[i % len(MORANDI_COLORS)] for i in range(len(labels))]
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                       autopct='%1.1f%%', startangle=90,
                                       pctdistance=0.8,
                                       wedgeprops=dict(width=0.4),
                                       textprops={'fontsize': 12})
    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight('bold')

    plt.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def draw_waterfall(title, categories, values, output_path, W=1600, H=1000):
    """瀑布图"""
    fig, ax = plt.subplots(figsize=(W/100, H/100), dpi=100)
    ax.set_title(title, fontsize=18, fontweight='bold', pad=15)

    cumulative = np.cumsum([0] + values[:-1])
    colors = ['#A8DADC' if v >= 0 else '#E63946' for v in values]
    colors[0] = '#457B9D'
    colors[-1] = '#1D3557'

    ax.bar(categories, values, bottom=cumulative, color=colors, edgecolor='white')

    for i, (c, v) in enumerate(zip(categories, values)):
        y = cumulative[i] + v/2
        ax.text(i, y, f'{v}', ha='center', va='center', fontsize=11, fontweight='bold', color='white')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def draw_kpi_dashboard(title, kpis, output_path, W=2400, H=1200):
    """KPI仪表盘卡片"""
    img = Image.new('RGB', (W, H), '#FAFAFA')
    draw = ImageDraw.Draw(img)
    font_t = _font(28, True)
    font_v = _font(48, True)
    font_s = _font(16)

    draw.text((W//2, 20), title, fill='#2D3436', font=font_t, anchor='mt')

    n = len(kpis)
    cols = min(n, 4)
    rows = math.ceil(n / cols)
    card_w = (W - 60) // cols
    card_h = (H - 100) // rows

    for i, (label, value, unit) in enumerate(kpis):
        r, c = divmod(i, cols)
        x = 20 + c * card_w
        y = 70 + r * card_h
        color = MORANDI_COLORS[i % len(MORANDI_COLORS)]

        draw.rounded_rectangle([x+5, y+5, x+card_w-5, y+card_h-5],
                               radius=15, fill=color, outline='#B2BEC3')
        draw.text((x + card_w//2, y + 30), str(value), fill='white', font=font_v, anchor='mt')
        draw.text((x + card_w//2, y + card_h - 40), f'{label} ({unit})',
                  fill='white', font=font_s, anchor='mt')

    img.save(output_path, quality=95)


def draw_personas(title, personas, output_path, W=2400, H=1400):
    """用户画像卡片"""
    img = Image.new('RGB', (W, H), '#FAFAFA')
    draw = ImageDraw.Draw(img)
    font_t = _font(28, True)
    font_b = _font(20)
    font_s = _font(15)

    draw.text((W//2, 20), title, fill='#2D3436', font=font_t, anchor='mt')

    n = len(personas)
    cols = min(n, 3)
    card_w = (W - 40) // cols
    card_h = (H - 100)

    for i, persona in enumerate(personas):
        c = i % cols
        x = 15 + c * card_w
        y = 70
        color = MORANDI_COLORS[i * 3 % len(MORANDI_COLORS)]

        draw.rounded_rectangle([x+5, y+5, x+card_w-5, y+card_h-5],
                               radius=15, fill='white', outline=color, width=3)

        # 头像圆圈
        cx, cy = x + card_w//2, y + 80
        draw.ellipse([cx-40, cy-40, cx+40, cy+40], fill=color, outline='#636E72')

        # 名字
        name = persona.get('name', f'用户{i+1}')
        tw = draw.textlength(name, font=font_b)
        draw.text((cx - tw//2, cy + 50), name, fill='#2D3436', font=font_b)

        # 属性
        attrs = persona.get('attrs', ['年龄: 30-45', '行业: 科技', '需求: 高效'])
        for j, attr in enumerate(attrs[:5]):
            tw = draw.textlength(attr, font=font_s)
            draw.text((cx - tw//2, cy + 90 + j*25), attr, fill='#636E72', font=font_s)

    img.save(output_path, quality=95)


# ============================================================
# 主生成函数：为每个图编号分配不同的可视化类型
# ============================================================

# 73张图的生成函数映射
# 格式: fig_key -> (generator_func, params_template)
FIGURE_GENERATORS = {
    # Chapter 1
    "图1-1": ("draw_org_chart", {"title_suffix": "公司组织架构"}),
    "图1-2": ("draw_gantt_pillow", {"title_suffix": "发展战略路线",
                "phases": [{"name":"生存期","start_month":1,"duration_months":6},
                           {"name":"成长期","start_month":5,"duration_months":8},
                           {"name":"扩张期","start_month":11,"duration_months":8},
                           {"name":"成熟期","start_month":17,"duration_months":7}]}),
    "图1-3": ("draw_ninebox", {"title_suffix": "SWOT分析",
                "cells": ["优势(S)\n技术领先\n团队优秀", "劣势(W)\n品牌待提升\n资金有限",
                          "机会(O)\n政策支持\n市场增长", "威胁(T)\n竞争加剧\n成本上升",
                          "核心对策\n发挥技术优势\n抓住政策机遇", "差异化战略\n技术壁垒\n服务深耕",
                          "增长路径\n产学研合作\n渠道拓展", "防御策略\n成本控制\n人才储备",
                          "行动重点\n产品迭代\n市场验证"]}),
    "图1-4": ("draw_hexagon_grid", {"title_suffix": "波特六力分析",
                "items": ["现有竞争者\n竞争激烈", "潜在进入者\n技术门槛高",
                          "替代品威胁\n较低", "供应商议价\n中等",
                          "买方议价\n较强", "互补品\n生态协同"]}),
    "图1-5": ("draw_gantt_pillow", {"title_suffix": "研发路线",
                "phases": [{"name":"基础研究","start_month":1,"duration_months":4},
                           {"name":"技术攻关","start_month":3,"duration_months":5},
                           {"name":"原型开发","start_month":6,"duration_months":4},
                           {"name":"测试优化","start_month":9,"duration_months":3},
                           {"name":"正式发布","start_month":11,"duration_months":2}]}),
    "图1-6": ("draw_matrix", {"title_suffix": "产品矩阵",
                "rows": ["基础版","专业版","企业版"],
                "cols": ["功能覆盖","性能指标","安全等级","服务支持","性价比"],
                "data": [[60,50,40,30,90],[80,75,70,65,70],[95,90,95,95,50]]}),
    "图1-7": ("draw_layered_arch", {"title_suffix": "服务体系架构",
                "layers": [("用户接入层",["Web门户","移动端","API接口","管理后台"]),
                           ("业务服务层",["用户管理","订单处理","数据分析","消息推送"]),
                           ("数据处理层",["数据采集","ETL","数据仓库","实时计算"]),
                           ("基础设施层",["云服务器","数据库","缓存","消息队列"])]}),
    "图1-8": ("draw_funnel", {"title_suffix": "营销渠道",
                "stages": [("品牌曝光",100),("兴趣激发",70),("需求识别",45),
                           ("意向转化",25),("成交签约",12)]}),
    "图1-9": ("draw_ninebox", {"title_suffix": "商业画布",
                "cells": ["关键伙伴\n云服务商\n数据供应商", "关键活动\n技术研发\n产品迭代",
                          "价值主张\n智能化解决方案\n降本增效", "客户关系\n技术支持\n定制服务",
                          "客户细分\n中大型企业\n政府机构", "关键资源\n核心团队\n技术专利\n用户数据",
                          "渠道\n直销\n线上推广\n合作", "成本结构\n研发50%\n市场25%\n运营25%",
                          "收入来源\nSaaS60%\n定制25%\n数据15%"]}),

    # Chapter 2
    "图2-1": ("draw_flowchart", {"title_suffix": "行业产业链",
                "steps": ["原材料供应","核心技术研发","中间产品制造","系统集成","渠道分销","终端客户"]}),
    "图2-2": ("draw_area_chart", {"title_suffix": "市场规模增长趋势",
                "x_labels": ["2023","2024","2025","2026","2027","2028"],
                "series_names": ["市场规模(亿)"],
                "data": [[120,180,260,380,520,700]]}),
    "图2-3": ("draw_timeline", {"title_suffix": "政策支持时间线",
                "phases": [{"name":"政策研究","duration_months":6},
                           {"name":"草案制定","duration_months":4},
                           {"name":"征求意见","duration_months":3},
                           {"name":"正式发布","duration_months":2},
                           {"name":"落地实施","duration_months":12}]}),
    "图2-4": ("draw_layered_arch", {"title_suffix": "产品功能架构",
                "layers": [("数据采集模块",["爬虫引擎","API对接","文件导入","实时流"]),
                           ("核心处理模块",["数据清洗","特征提取","模型推理","结果融合"]),
                           ("业务应用模块",["智能分析","可视化展示","预警推送","报告生成"]),
                           ("用户交互模块",["仪表盘","工作台","管理中心","个人中心"])]}),
    "图2-5": ("draw_layered_arch", {"title_suffix": "系统技术架构",
                "layers": [("前端展示层",["React","Vue","ECharts","WebSocket"]),
                           ("API网关层",["Nginx","Kong","认证鉴权","限流熔断"]),
                           ("微服务层",["用户服务","业务服务","算法服务","通知服务"]),
                           ("数据存储层",["MySQL","Redis","MongoDB","Elasticsearch"]),
                           ("基础设施层",["Docker","K8s","CI/CD","监控告警"])]}),
    "图2-6": ("draw_flowchart", {"title_suffix": "核心算法流程",
                "steps": ["数据输入","预处理与清洗","特征工程","模型推理","后处理","结果输出"]}),

    # 图2-7 to 2-10: screenshots (handled separately)
    # 图2-11:
    "图2-11": ("draw_personas", {"title_suffix": "目标客户画像",
                "personas": [{"name":"大型企业CTO","attrs":["年龄:35-50","关注:系统稳定性","预算:充足"]},
                             {"name":"中小企业老板","attrs":["年龄:30-45","关注:性价比","决策快"]},
                             {"name":"政府部门主管","attrs":["年龄:40-55","关注:合规性","流程长"]}]}),
    "图2-12": ("draw_radar", {"title_suffix": "客户需求分析",
                "labels": ["功能性","易用性","稳定性","安全性","性价比","服务"],
                "values": [85,75,90,88,70,82]}),
    "图2-13": ("draw_comparison_table", {"title_suffix": "产品优势对比",
                "headers": ["维度","本公司","竞品A","竞品B"],
                "rows": [["准确率","95%","85%","80%"],["响应速度","<100ms","<200ms","<300ms"],
                         ["功能丰富度","★★★★★","★★★★","★★★"],["价格","中","高","低"]]}),
    # 图2-14: screenshot
    "图2-15": ("draw_bar_chart", {"title_suffix": "应用效果数据对比",
                "categories": ["效率提升","成本降低","质量改善","满意度"],
                "values": [85,70,80,92], "horizontal": True}),
    "图2-16": ("draw_pie_chart", {"title_suffix": "市场占有率分析",
                "labels": ["本公司","行业龙头","竞品B","竞品C","其他"],
                "sizes": [12,30,22,18,18]}),
    "图2-17": ("draw_scatter", {"title_suffix": "行业竞争格局",
                "labels": ["本公司","头部企业A","头部企业B","中型企业C","传统厂商D"],
                "x_data": [12,30,22,15,21],
                "y_data": [90,75,65,55,35]}),
    "图2-18": ("draw_donut", {"title_suffix": "收入构成",
                "labels": ["SaaS订阅","定制开发","数据服务","技术咨询","其他"],
                "sizes": [45,25,15,10,5]}),
    "图2-19": ("draw_line_chart", {"title_suffix": "收入增长趋势",
                "x_labels": ["2026","2027","2028","2029","2030"],
                "series_names": ["营收(万)","净利润(万)"],
                "data": [[150,500,1500,3500,8000],[20,80,350,900,2500]]}),
    "图2-20": ("draw_scatter", {"title_suffix": "竞争格局矩阵",
                "labels": ["本公司","国际巨头","国内龙头","创业公司A","创业公司B","传统厂商"],
                "x_data": [15,35,25,8,6,11],
                "y_data": [92,80,70,85,78,40]}),
    "图2-21": ("draw_radar", {"title_suffix": "竞争对手对标分析",
                "labels": ["技术实力","市场份额","品牌影响","服务能力","创新能力","价格优势"],
                "values": [95,60,45,85,92,70]}),
    # 图2-22 to 2-51: screenshots (30 screenshots)
    "图2-52": ("draw_layered_arch", {"title_suffix": "系统整体架构",
                "layers": [("接入层",["负载均衡","API网关","CDN","WAF"]),
                           ("应用层",["微服务集群","容器编排","服务网格","链路追踪"]),
                           ("数据层",["关系数据库","文档数据库","搜索引擎","时序数据库"]),
                           ("平台层",["对象存储","消息队列","调度引擎","配置中心"]),
                           ("运维层",["监控告警","日志分析","CI/CD","安全审计"])]}),
    "图2-53": ("draw_flowchart", {"title_suffix": "数据流架构",
                "steps": ["数据源","数据采集","数据清洗","数据存储","数据分析","数据应用"]}),
    "图2-54": ("draw_hexagon_grid", {"title_suffix": "核心算法架构",
                "items": ["数据预处理","特征提取","模型训练","模型推理","结果融合","反馈优化"]}),
    "图2-55": ("draw_layered_arch", {"title_suffix": "微服务架构",
                "layers": [("网关层",["路由分发","限流熔断","认证鉴权"]),
                           ("服务层",["用户服务","业务服务","算法服务","通知服务"]),
                           ("治理层",["服务注册","配置管理","链路追踪","健康检查"]),
                           ("存储层",["MySQL集群","Redis集群","MongoDB","Kafka"])]}),
    "图2-56": ("draw_layered_arch", {"title_suffix": "数据库架构",
                "layers": [("主数据库(MySQL)",["读写分离","主从复制","分库分表"]),
                           ("缓存层(Redis)",["热点数据","会话管理","分布式锁"]),
                           ("搜索(ES)",["全文检索","日志分析","指标聚合"]),
                           ("对象存储",["图片文件","备份归档","静态资源"])]}),
    "图2-57": ("draw_layered_arch", {"title_suffix": "安全架构",
                "layers": [("网络安全",["防火墙","DDoS防护","VPN","入侵检测"]),
                           ("应用安全",["WAF","SQL注入防护","XSS防护","CSRF防护"]),
                           ("数据安全",["传输加密","存储加密","脱敏处理","密钥管理"]),
                           ("访问控制",["RBAC","OAuth2.0","多因子认证","审计日志"])]}),
    "图2-58": ("draw_layered_arch", {"title_suffix": "部署架构",
                "layers": [("边缘节点",["CDN","DNS","负载均衡"]),
                           ("K8s集群",["Pod","Service","Ingress","HPA"]),
                           ("中间件",["消息队列","缓存","数据库","搜索引擎"]),
                           ("监控运维",["Prometheus","Grafana","ELK","告警"])]}),
    "图2-59": ("draw_flowchart", {"title_suffix": "API架构",
                "steps": ["客户端请求","API网关","认证鉴权","路由分发","业务处理","响应返回"]}),
    "图2-60": ("draw_layered_arch", {"title_suffix": "前端架构",
                "layers": [("UI框架层",["React/Vue","组件库","主题系统","国际化"]),
                           ("状态管理层",["Redux/Mobx","数据缓存","异步处理","错误处理"]),
                           ("网络层",["HTTP客户端","WebSocket","请求拦截","缓存策略"]),
                           ("工具层",["构建工具","测试框架","代码规范","CI/CD"])]}),
    "图2-61": ("draw_layered_arch", {"title_suffix": "运维监控架构",
                "layers": [("数据采集",["指标采集","日志采集","链路采集","事件采集"]),
                           ("数据处理",["数据清洗","聚合计算","异常检测","告警规则"]),
                           ("可视化展示",["仪表盘","拓扑图","趋势图","报表"]),
                           ("告警响应",["分级告警","自动恢复","工单流转","复盘分析"])]}),

    # Chapter 3
    "图3-1": ("draw_pie_chart", {"title_suffix": "资金用途分布",
                "labels": ["研发投入","市场推广","运营成本","人才引进","风险储备"],
                "sizes": [40,25,15,12,8]}),
    "图3-2": ("draw_gantt_pillow", {"title_suffix": "融资里程碑",
                "phases": [{"name":"种子轮","start_month":1,"duration_months":3},
                           {"name":"产品研发","start_month":3,"duration_months":6},
                           {"name":"天使轮","start_month":8,"duration_months":3},
                           {"name":"市场拓展","start_month":10,"duration_months":6},
                           {"name":"A轮融资","start_month":16,"duration_months":4}]}),

    # Chapter 4
    "图4-1": ("draw_matrix", {"title_suffix": "风险矩阵",
                "rows": ["市场风险","财务风险","技术风险","政策风险","人才风险"],
                "cols": ["发生概率","影响程度","综合评级","应对优先级"],
                "data": [[70,60,65,70],[50,80,60,65],[40,75,55,60],[30,50,40,45],[45,70,55,60]]}),
}


def generate_figure(project_name, fig_key, output_path):
    """根据fig_key调用对应的生成函数"""
    if fig_key not in FIGURE_GENERATORS:
        return False

    func_name, params = FIGURE_GENERATORS[fig_key]
    title = f"{project_name}{params.get('title_suffix', '')}"
    func = globals()[func_name]

    try:
        if func_name == "draw_org_chart":
            func(title, output_path)
        elif func_name == "draw_gantt_pillow":
            func(title, params.get("phases", []), output_path)
        elif func_name == "draw_ninebox":
            func(title, params.get("cells", []), output_path)
        elif func_name == "draw_hexagon_grid":
            func(title, params.get("items", []), output_path)
        elif func_name == "draw_matrix":
            func(title, params.get("rows", []), params.get("cols", []),
                  params.get("data", []), output_path)
        elif func_name == "draw_funnel":
            func(title, params.get("stages", []), output_path)
        elif func_name == "draw_layered_arch":
            func(title, params.get("layers", []), output_path)
        elif func_name == "draw_radar":
            func(title, params.get("labels", []), params.get("values", []),
                  output_path)
        elif func_name == "draw_bar_chart":
            func(title, params.get("categories", []), params.get("values", []),
                  output_path, horizontal=params.get("horizontal", False))
        elif func_name == "draw_line_chart":
            func(title, params.get("x_labels", []), params.get("data", []),
                  params.get("series_names", []), output_path)
        elif func_name == "draw_pie_chart":
            func(title, params.get("labels", []), params.get("sizes", []),
                  output_path)
        elif func_name == "draw_scatter":
            func(title, params.get("x_data", []), params.get("y_data", []),
                  params.get("labels", []), output_path)
        elif func_name == "draw_area_chart":
            func(title, params.get("x_labels", []), params.get("data", []),
                  params.get("series_names", []), output_path)
        elif func_name == "draw_comparison_table":
            func(title, params.get("headers", []), params.get("rows", []),
                  output_path)
        elif func_name == "draw_flowchart":
            func(title, params.get("steps", []), output_path)
        elif func_name == "draw_timeline":
            func(title, params.get("phases", []), output_path)
        elif func_name == "draw_personas":
            func(title, params.get("personas", []), output_path)
        elif func_name == "draw_kpi_dashboard":
            func(title, params.get("kpis", []), output_path)
        elif func_name == "draw_stacked_bar":
            func(title, params.get("categories", []), params.get("series_data", []),
                  params.get("series_names", []), output_path)
        elif func_name == "draw_donut":
            func(title, params.get("labels", []), params.get("sizes", []),
                  output_path)
        elif func_name == "draw_waterfall":
            func(title, params.get("categories", []), params.get("values", []),
                  output_path)
        else:
            return False
        return True
    except Exception as e:
        print(f"  ERROR {fig_key} ({func_name}): {e}")
        return False


if __name__ == "__main__":
    # Quick test: generate all chart types for a test project
    test_dir = Path(r"D:\计划书AI\test_charts")
    test_dir.mkdir(exist_ok=True)

    for fig_key in FIGURE_GENERATORS:
        out = test_dir / f"{fig_key.replace('-', '_')}.png"
        ok = generate_figure("测试产品", fig_key, str(out))
        print(f"{'OK' if ok else 'FAIL'} {fig_key} -> {out.name}")

    print(f"\nTotal: {len(FIGURE_GENERATORS)} chart types")
