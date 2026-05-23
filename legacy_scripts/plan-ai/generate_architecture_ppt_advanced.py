#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制启动 Microsoft Office PowerPoint，绘制复杂、专业、顶刊级别的智言平台技术架构图。
莫兰迪配色，扁平化设计，元素丰富，逻辑严密。
"""

import win32com.client
import subprocess
import time
import os
import math

OFFICE_PPT_EXE = r'C:\Program Files\Microsoft Office\Root\Office16\POWERPNT.EXE'
OUTPUT_PNG = os.path.abspath(r'academic_diagrams_run\architecture.png')

# 莫兰迪配色 (BGR)
PALETTE = {
    'bg': 0xEBEDF8,         # f8edeb 米白背景
    'border': 0xAF9A8E,     # 8e9aaf 灰蓝边框
    'user': 0xD3C0CB,       # cbc0d3 淡紫
    'gateway': 0xA4B7B7,    # b7b7a4 卡其
    'biz': 0xDCE2D8,        # d8e2dc 薄荷绿
    'model': 0xAF9A8E,      # 8e9aaf 灰蓝
    'data': 0xD7D3EF,       # efd3d7 粉
    'infra': 0x92A3A2,      # a2a392 橄榄灰
    'side': 0xDBE4EC,       # ece4db 暖灰
    'dark_text': 0x2D2D2D,  # 深灰文字
    'light_text': 0xFFFFFF, # 白色文字
    'accent_line': 0x8E9AAF,# 强调线
}

PX2PT = 0.75  # 像素转点
SW, SH = 1920 * PX2PT, 1080 * PX2PT

def kill_ppt_processes():
    subprocess.run(['taskkill', '/F', '/IM', 'POWERPNT.EXE'], capture_output=True)
    subprocess.run(['taskkill', '/F', '/IM', 'wpp.exe'], capture_output=True)
    time.sleep(1)

def get_office_powerpoint():
    kill_ppt_processes()
    proc = subprocess.Popen([OFFICE_PPT_EXE, '/Automation'])
    ppt = None
    for _ in range(15):
        time.sleep(1)
        try:
            ppt = win32com.client.GetActiveObject("PowerPoint.Application")
            break
        except Exception:
            pass
    if ppt is None:
        raise RuntimeError("无法连接到 Office PowerPoint，启动失败")
    if ppt.Version not in ("16.0", "15.0", "14.0"):
        raise RuntimeError(f"启动的不是 Microsoft Office PowerPoint，版本号：{ppt.Version}")
    return ppt, proc

def set_font(tr, is_english=False, size=12, bold=False, color=None):
    """设置字体：中文微软雅黑，英文 Arial"""
    if is_english:
        tr.Font.Name = "Arial"
        tr.Font.NameFarEast = "Microsoft YaHei"
    else:
        tr.Font.Name = "Microsoft YaHei"
        tr.Font.NameAscii = "Arial"
    tr.Font.Size = size
    tr.Font.Bold = bold
    if color is not None:
        tr.Font.Color.RGB = color

def add_rect(slide, left, top, width, height, fill_rgb, line_rgb=None, line_width=1, text="", text_color=None, font_size=12, bold=False, rounded=False):
    shape_type = 5 if rounded else 1  # msoShapeRoundedRectangle or msoShapeRectangle
    shape = slide.Shapes.AddShape(shape_type, left, top, width, height)
    shape.Fill.ForeColor.RGB = fill_rgb
    shape.Fill.Visible = True
    shape.Fill.Solid()
    if line_rgb is not None:
        shape.Line.ForeColor.RGB = line_rgb
        shape.Line.Weight = line_width
        shape.Line.Visible = True
    else:
        shape.Line.Visible = False
    if text:
        tf = shape.TextFrame
        tf.TextRange.Text = text
        tc = text_color if text_color is not None else PALETTE['dark_text']
        set_font(tf.TextRange, is_english=False, size=font_size, bold=bold, color=tc)
        tf.TextRange.ParagraphFormat.Alignment = 2  # ppAlignCenter
        tf.VerticalAnchor = 3  # msoAnchorMiddle
        tf.MarginLeft = 4 * PX2PT
        tf.MarginRight = 4 * PX2PT
        tf.MarginTop = 4 * PX2PT
        tf.MarginBottom = 4 * PX2PT
    return shape

def add_textbox(slide, left, top, width, height, text, font_size=10, bold=False, color=None, align=2):
    shape = slide.Shapes.AddTextbox(1, left, top, width, height)
    tf = shape.TextFrame
    tf.TextRange.Text = text
    tc = color if color is not None else PALETTE['dark_text']
    set_font(tf.TextRange, is_english=False, size=font_size, bold=bold, color=tc)
    tf.TextRange.ParagraphFormat.Alignment = align
    tf.VerticalAnchor = 3
    return shape

def add_dashed_group(slide, left, top, width, height, label=""):
    """添加虚线分组框"""
    shape = slide.Shapes.AddShape(1, left, top, width, height)
    shape.Fill.ForeColor.RGB = 0xFFFFFF
    shape.Fill.Transparency = 0.9
    shape.Fill.Visible = True
    shape.Line.ForeColor.RGB = PALETTE['border']
    shape.Line.Weight = 1.5
    shape.Line.Visible = True
    shape.Line.DashStyle = 2  # msoLineDash
    if label:
        # 在左上角添加标签
        add_textbox(slide, left + 8*PX2PT, top - 10*PX2PT, 120*PX2PT, 16*PX2PT,
                   label, font_size=9, bold=True, color=PALETTE['border'], align=1)
    return shape

def add_arrow(slide, x1, y1, x2, y2, dashed=False, double_headed=False, color=None):
    """添加箭头连线"""
    color = color or PALETTE['accent_line']
    if abs(x2 - x1) < 1 or abs(y2 - y1) < 1:
        # 直线
        line = slide.Shapes.AddConnector(1, x1, y1, x2, y2)
    else:
        # 折线
        line = slide.Shapes.AddConnector(2, x1, y1, x2, y2)  # msoConnectorElbow
    line.Line.EndArrowheadStyle = 5  # msoArrowheadTriangle
    if double_headed:
        line.Line.BeginArrowheadStyle = 5
    line.Line.ForeColor.RGB = color
    line.Line.Weight = 1.5
    if dashed:
        line.Line.DashStyle = 2  # msoLineDash
    return line

def add_curved_feedback(slide, left, top, height):
    """添加弯曲的反馈箭头（用曲线连接器）"""
    line = slide.Shapes.AddConnector(3, left, top, left, top + height)  # msoConnectorCurve
    line.Line.EndArrowheadStyle = 5
    line.Line.ForeColor.RGB = PALETTE['border']
    line.Line.Weight = 1.5
    line.Line.DashStyle = 2
    return line

def main():
    ppt, proc = get_office_powerpoint()
    ppt.Visible = True
    
    prs = ppt.Presentations.Add()
    # 设置幻灯片大小为 1920x1080 (16:9)
    # 在 PowerPoint VBA 中，PageSetup.SlideSize = ppSlideSizeCustom 然后设置宽度和高度
    # 注意 PageSetup 宽度单位是点，1920 像素 = 1440 点 (1920*0.75)
    prs.PageSetup.SlideSize = 7  # ppSlideSizeCustom
    prs.PageSetup.SlideWidth = SW
    prs.PageSetup.SlideHeight = SH
    
    slide = prs.Slides.Add(1, 6)  # Blank
    
    # ===== 背景 =====
    bg = slide.Shapes.AddShape(1, 0, 0, SW, SH)
    bg.Fill.ForeColor.RGB = PALETTE['bg']
    bg.Line.Visible = False
    bg.ZOrder(1)  # SendToBack
    
    # ===== 标题 =====
    title_box = add_textbox(slide, 0, 18*PX2PT, SW, 40*PX2PT,
                           "智言大模型服务平台技术架构与数据流框架",
                           font_size=28, bold=True, color=PALETTE['dark_text'], align=2)
    
    # ===== 布局参数 =====
    main_left = 200 * PX2PT
    main_right = 1660 * PX2PT
    main_width = main_right - main_left
    side_width = 160 * PX2PT
    
    layer_y = 100 * PX2PT
    layer_h = 125 * PX2PT
    layer_gap = 20 * PX2PT
    box_gap = 12 * PX2PT
    
    # ===== 图例 (右上角) =====
    legend_x = 1480 * PX2PT
    legend_y = 70 * PX2PT
    add_rect(slide, legend_x, legend_y, 16*PX2PT, 10*PX2PT, PALETTE['accent_line'], line_rgb=PALETTE['accent_line'], text="")
    add_textbox(slide, legend_x + 20*PX2PT, legend_y - 2*PX2PT, 60*PX2PT, 14*PX2PT, "数据流", font_size=9)
    add_arrow(slide, legend_x, legend_y + 20*PX2PT, legend_x + 16*PX2PT, legend_y + 20*PX2PT, dashed=True)
    add_textbox(slide, legend_x + 20*PX2PT, legend_y + 18*PX2PT, 60*PX2PT, 14*PX2PT, "控制流", font_size=9)
    add_curved_feedback(slide, legend_x + 8*PX2PT, legend_y + 40*PX2PT, 14*PX2PT)
    add_textbox(slide, legend_x + 20*PX2PT, legend_y + 38*PX2PT, 60*PX2PT, 14*PX2PT, "反馈流", font_size=9)
    
    # ===== 1. 用户接入层 =====
    y1 = layer_y
    add_dashed_group(slide, main_left - 10*PX2PT, y1 - 10*PX2PT, main_width + 20*PX2PT, layer_h + 20*PX2PT, "Layer 1 用户接入层")
    user_items = [
        ("Web客户端\nWeb Portal", PALETTE['user']),
        ("移动小程序\nMini Program", PALETTE['user']),
        ("Open API\nRESTful/gRPC", PALETTE['user']),
        ("管理后台\nAdmin Console", PALETTE['user']),
    ]
    box_w = (main_width - 3*box_gap) / 4
    for i, (txt, color) in enumerate(user_items):
        left = main_left + i * (box_w + box_gap)
        add_rect(slide, left, y1, box_w, 70*PX2PT, color, line_rgb=0xFFFFFF, line_width=2,
                text=txt, text_color=PALETTE['light_text'], font_size=12, bold=True, rounded=True)
    # 协议标签
    proto_labels = ["HTTPS/SSL", "OAuth 2.0", "JWT Token", "WS/WSS"]
    for i, label in enumerate(proto_labels):
        left = main_left + i * (box_w + box_gap) + box_w/2 - 35*PX2PT
        add_rect(slide, left, y1 + 76*PX2PT, 70*PX2PT, 20*PX2PT, 0xF5F5F5, line_rgb=0xCCCCCC,
                text=label, text_color=PALETTE['dark_text'], font_size=9, rounded=True)
    
    # ===== 2. 网关与调度层 =====
    y2 = y1 + layer_h + layer_gap
    add_dashed_group(slide, main_left - 10*PX2PT, y2 - 10*PX2PT, main_width + 20*PX2PT, layer_h + 20*PX2PT, "Layer 2 网关与调度层")
    gw_items = [
        ("API Gateway\n统一接入网关", PALETTE['gateway']),
        ("Load Balancer\n动态负载均衡", PALETTE['gateway']),
        ("Auth Center\n身份鉴权中心", PALETTE['gateway']),
        ("Rate Limiter\n流量限速器", PALETTE['gateway']),
    ]
    for i, (txt, color) in enumerate(gw_items):
        left = main_left + i * (box_w + box_gap)
        add_rect(slide, left, y2, box_w, 70*PX2PT, color, line_rgb=0xFFFFFF, line_width=2,
                text=txt, text_color=PALETTE['light_text'], font_size=12, bold=True, rounded=True)
    gw_sub = ["灰度路由", "熔断降级", "请求鉴权", "限流控制"]
    for i, label in enumerate(gw_sub):
        left = main_left + i * (box_w + box_gap) + box_w/2 - 35*PX2PT
        add_rect(slide, left, y2 + 76*PX2PT, 70*PX2PT, 20*PX2PT, 0xF5F5F5, line_rgb=0xCCCCCC,
                text=label, text_color=PALETTE['dark_text'], font_size=9, rounded=True)
    
    # ===== 3. 业务应用中心 =====
    y3 = y2 + layer_h + layer_gap
    add_dashed_group(slide, main_left - 10*PX2PT, y3 - 10*PX2PT, main_width + 20*PX2PT, layer_h + 30*PX2PT, "Layer 3 业务应用中心")
    biz_modules = [
        ("智能客服中心", "多轮对话\n意图识别\n情感分析", PALETTE['biz']),
        ("知识问答中心", "文档解析\n语义检索\n答案生成", PALETTE['biz']),
        ("内容生成中心", "文案创作\n代码生成\n报表生成", PALETTE['biz']),
        ("数据分析中心", "文本挖掘\n趋势预测\n可视化", PALETTE['biz']),
    ]
    for i, (title, subs, color) in enumerate(biz_modules):
        left = main_left + i * (box_w + box_gap)
        # 主框
        add_rect(slide, left, y3, box_w, 55*PX2PT, color, line_rgb=0xFFFFFF, line_width=2,
                text=title, text_color=PALETTE['dark_text'], font_size=13, bold=True, rounded=True)
        # 子框（3个小框横向排列）
        sub_box_w = (box_w - 2*4*PX2PT) / 3
        for j, sub in enumerate(subs.split("\n")):
            add_rect(slide, left + j*(sub_box_w + 4*PX2PT), y3 + 58*PX2PT, sub_box_w, 32*PX2PT,
                    0xF0F0F0, line_rgb=color, line_width=1,
                    text=sub, text_color=PALETTE['dark_text'], font_size=8, rounded=True)
        # 服务标签
        tags = ["SaaS", "PaaS", "API", "BI"]
        add_rect(slide, left + box_w - 35*PX2PT, y3 - 6*PX2PT, 35*PX2PT, 14*PX2PT,
                0xFFFFFF, line_rgb=color, line_width=1,
                text=tags[i], text_color=color, font_size=8, rounded=True)
    
    # ===== 4. 模型引擎层 =====
    y4 = y3 + layer_h + layer_gap + 10*PX2PT
    model_h = 110 * PX2PT
    add_dashed_group(slide, main_left - 10*PX2PT, y4 - 10*PX2PT, main_width + 20*PX2PT, model_h + 20*PX2PT, "Layer 4 模型引擎层")
    model_items = [
        ("基座大模型\nPre-training & CL", PALETTE['model']),
        ("领域微调\nLoRA / SFT / PT", PALETTE['model']),
        ("RAG检索增强\nVector Index / RR", PALETTE['model']),
        ("推理加速\nQuant / Batch / Cache", PALETTE['model']),
        ("模型评估\nAuto-eval / A-B Test", PALETTE['model']),
        ("模型监控\nDrift / Degradation", PALETTE['model']),
    ]
    m_box_w = (main_width - 5*box_gap) / 6
    for i, (txt, color) in enumerate(model_items):
        left = main_left + i * (m_box_w + box_gap)
        add_rect(slide, left, y4, m_box_w, model_h, color, line_rgb=0xFFFFFF, line_width=2,
                text=txt, text_color=PALETTE['light_text'], font_size=10, bold=True, rounded=True)
    
    # ===== 5. 数据资源层 =====
    y5 = y4 + model_h + layer_gap
    data_h = 90 * PX2PT
    add_dashed_group(slide, main_left - 10*PX2PT, y5 - 10*PX2PT, main_width + 20*PX2PT, data_h + 20*PX2PT, "Layer 5 数据资源层")
    data_items = [
        ("行业知识库\n结构化/非结构化", PALETTE['data']),
        ("训练数据集\n清洗/标注/增强", PALETTE['data']),
        ("向量数据库\nEmbedding/相似度", PALETTE['data']),
        ("数据治理平台\n脱敏/合规/血缘", PALETTE['data']),
    ]
    d_box_w = (main_width - 3*box_gap) / 4
    for i, (txt, color) in enumerate(data_items):
        left = main_left + i * (d_box_w + box_gap)
        add_rect(slide, left, y5, d_box_w, data_h, color, line_rgb=0xFFFFFF, line_width=2,
                text=txt, text_color=PALETTE['dark_text'], font_size=11, bold=True, rounded=True)
    
    # ===== 6. 基础设施层 =====
    y6 = y5 + data_h + layer_gap
    infra_h = 85 * PX2PT
    add_dashed_group(slide, main_left - 10*PX2PT, y6 - 10*PX2PT, main_width + 20*PX2PT, infra_h + 20*PX2PT, "Layer 6 基础设施层")
    infra_items = [
        ("国产化算力\n昇腾/GPU混合调度", PALETTE['infra']),
        ("容器编排\nK8s/Docker弹性伸缩", PALETTE['infra']),
        ("安全网关\n防火墙/零信任架构", PALETTE['infra']),
        ("监控运维\nPrometheus/Grafana", PALETTE['infra']),
        ("网络隔离\nVPC/子网/安全组", PALETTE['infra']),
    ]
    i_box_w = (main_width - 4*box_gap) / 5
    for i, (txt, color) in enumerate(infra_items):
        left = main_left + i * (i_box_w + box_gap)
        add_rect(slide, left, y6, i_box_w, infra_h, color, line_rgb=0xFFFFFF, line_width=2,
                text=txt, text_color=PALETTE['light_text'], font_size=10, bold=True, rounded=True)
    
    # ===== 左侧：部署域 =====
    side_left = 20 * PX2PT
    side_y_start = y3
    side_h_total = (y6 + infra_h) - y3
    add_dashed_group(slide, side_left, side_y_start - 10*PX2PT, side_width + 20*PX2PT, side_h_total + 20*PX2PT, "部署域")
    deploy_items = ["公有云", "私有云", "混合云", "边缘节点"]
    dep_h = (side_h_total - 3*box_gap) / 4
    for i, txt in enumerate(deploy_items):
        top = side_y_start + i * (dep_h + box_gap)
        add_rect(slide, side_left + 10*PX2PT, top, side_width, dep_h, PALETTE['side'],
                line_rgb=PALETTE['border'], line_width=1.5,
                text=txt, text_color=PALETTE['dark_text'], font_size=11, bold=True, rounded=True)
    # 部署域连接到基础设施层
    for i in range(4):
        top = side_y_start + i * (dep_h + box_gap) + dep_h/2
        add_arrow(slide, side_left + side_width + 10*PX2PT, top, main_left - 10*PX2PT, y6 + infra_h/2, dashed=True)
    
    # ===== 右侧：安全与治理体系 =====
    sec_left = 1700 * PX2PT
    add_dashed_group(slide, sec_left - 10*PX2PT, y1 - 10*PX2PT, side_width + 20*PX2PT, (y6 + infra_h) - y1 + 20*PX2PT, "安全治理")
    sec_items = [
        ("实时监控", y1 + 20*PX2PT),
        ("合规审计", y2 + 20*PX2PT),
        ("权限管理", y3 + 40*PX2PT),
        ("数据加密", y4 + 30*PX2PT),
        ("访问控制", y5 + 20*PX2PT),
        ("日志溯源", y6 + 20*PX2PT),
    ]
    for txt, top in sec_items:
        add_rect(slide, sec_left, top, side_width, 36*PX2PT, PALETTE['side'],
                line_rgb=PALETTE['border'], line_width=1.5,
                text=txt, text_color=PALETTE['dark_text'], font_size=10, bold=True, rounded=True)
        # 横向虚线连接到各层
        add_arrow(slide, sec_left - 10*PX2PT, top + 18*PX2PT, main_right + 10*PX2PT, top + 18*PX2PT, dashed=True)
    
    # ===== 主数据流（纵向实线箭头） =====
    cx = main_left + main_width / 2
    # 1->2
    add_arrow(slide, cx, y1 + 96*PX2PT, cx, y2)
    # 2->3
    add_arrow(slide, cx, y2 + 96*PX2PT, cx, y3)
    # 3->4
    add_arrow(slide, cx, y3 + 90*PX2PT, cx, y4)
    # 4->5
    add_arrow(slide, cx, y4 + model_h, cx, y5)
    # 5->6
    add_arrow(slide, cx, y5 + data_h, cx, y6)
    
    # ===== 反馈流（虚线，从下到上） =====
    fb_x = main_left + main_width / 2 + 180*PX2PT
    add_arrow(slide, fb_x, y6, fb_x, y5 + data_h, dashed=True)
    add_arrow(slide, fb_x, y5, fb_x, y4 + model_h, dashed=True)
    add_arrow(slide, fb_x, y4, fb_x, y3 + 90*PX2PT, dashed=True)
    # 标签
    add_textbox(slide, fb_x + 8*PX2PT, (y4 + y3)/2 + 20*PX2PT, 40*PX2PT, 40*PX2PT,
               "模型\n反馈", font_size=9, color=PALETTE['border'], align=1)
    
    # ===== 推理返回流（从模型层到业务层，双向） =====
    ret_x = main_left + main_width / 2 - 180*PX2PT
    add_arrow(slide, ret_x, y4, ret_x, y3 + 90*PX2PT, dashed=False, double_headed=True)
    add_textbox(slide, ret_x - 35*PX2PT, (y4 + y3)/2 + 20*PX2PT, 30*PX2PT, 40*PX2PT,
               "推理\n结果", font_size=9, color=PALETTE['accent_line'], align=1)
    
    # ===== 底部标注 =====
    add_textbox(slide, 0, SH - 28*PX2PT, SW, 20*PX2PT,
               "图 1  智言大模型服务平台整体技术架构与数据流向示意图",
               font_size=11, bold=False, color=PALETTE['dark_text'], align=2)
    
    # ===== 导出 PNG =====
    os.makedirs(os.path.dirname(OUTPUT_PNG), exist_ok=True)
    # 导出整个幻灯片
    prs.SaveAs(os.path.abspath(r'academic_diagrams_run\architecture_ppt_source.pptx'), 24)
    slide.Export(OUTPUT_PNG, "PNG", 2560, 1440)
    print(f"Exported architecture diagram to: {OUTPUT_PNG}")
    
    # 清理
    prs.Close()
    ppt.Quit()
    proc.kill()
    time.sleep(1)
    kill_ppt_processes()
    print("Done.")

if __name__ == "__main__":
    main()
