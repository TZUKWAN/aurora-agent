#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制启动 Microsoft Office PowerPoint，绘制智言平台技术架构图，并导出为高清 PNG。
"""

import win32com.client
import subprocess
import time
import os

OFFICE_PPT_EXE = r'C:\Program Files\Microsoft Office\Root\Office16\POWERPNT.EXE'
OUTPUT_PNG = os.path.abspath(r'academic_diagrams_run\architecture_ppt.png')

def get_office_powerpoint():
    subprocess.run(['taskkill', '/F', '/IM', 'POWERPNT.EXE'], capture_output=True)
    subprocess.run(['taskkill', '/F', '/IM', 'wpp.exe'], capture_output=True)
    time.sleep(1)
    proc = subprocess.Popen([OFFICE_PPT_EXE, '/Automation'])
    time.sleep(3)
    ppt = win32com.client.GetActiveObject("PowerPoint.Application")
    if ppt.Version not in ("16.0", "15.0", "14.0"):
        raise RuntimeError(f"启动的不是 Microsoft Office PowerPoint，版本号：{ppt.Version}")
    return ppt, proc

def add_rounded_rect(slide, left, top, width, height, rgb, text):
    """添加圆角矩形并设置文本"""
    shape = slide.Shapes.AddShape(5, left, top, width, height)  # 5 = msoShapeRoundedRectangle
    shape.Fill.ForeColor.RGB = rgb
    shape.Fill.Visible = True
    shape.Fill.Solid()
    shape.Line.ForeColor.RGB = 0xFFFFFF  # 白色边框
    shape.Line.Weight = 2
    shape.Line.Visible = True
    
    tf = shape.TextFrame
    tf.TextRange.Text = text
    tf.TextRange.Font.Name = "Microsoft YaHei"
    tf.TextRange.Font.Size = 18
    tf.TextRange.Font.Color.RGB = 0xFFFFFF  # 白色文字
    tf.TextRange.ParagraphFormat.Alignment = 2  # ppAlignCenter
    tf.VerticalAnchor = 3  # msoAnchorMiddle
    return shape

def add_arrow(slide, x1, y1, x2, y2):
    """添加带箭头的直线"""
    line = slide.Shapes.AddConnector(1, x1, y1, x2, y2)  # 1 = msoConnectorStraight
    line.Line.EndArrowheadStyle = 5  # msoArrowheadTriangle
    line.Line.ForeColor.RGB = 0x333333
    line.Line.Weight = 2
    return line

def main():
    ppt, proc = get_office_powerpoint()
    ppt.Visible = True
    
    prs = ppt.Presentations.Add()
    # 设置幻灯片尺寸 16:9 (1280x720 单位是磅? 不，Add 默认是 960x540 点，我们用 1280x720 像素导出)
    # 先添加空白幻灯片
    slide = prs.Slides.Add(1, 6)  # 6 = ppLayoutBlank
    
    # 配色
    colors = {
        'primary': 0x794E1F,    # #1f4e79 -> BGR
        'secondary': 0xD59B5B,  # #5b9bd5 -> BGR
        'accent': 0x47AD70,     # #70ad47 -> BGR
        'neutral': 0xA5A5A5,    # #a5a5a5 -> BGR
    }
    
    # 幻灯片宽高 (单位：点，96 DPI 下 1 像素 ≈ 0.75 点，但 Export 是按像素)
    # 我们直接用像素值作为形状坐标，因为 Export 时按像素走；但在 VBA 中坐标单位是点 (Points)，1 像素 = 0.75 点
    px_to_pt = 0.75
    sw = 1280 * px_to_pt
    sh = 720 * px_to_pt
    
    # 添加背景
    bg = slide.Shapes.AddShape(1, 0, 0, sw, sh)  # 1 = msoShapeRectangle
    bg.Fill.ForeColor.RGB = 0xFFFFFF
    bg.Line.Visible = False
    # 移到最底层
    bg.ZOrder(1)  # msoSendToBack
    
    # 标题
    title = slide.Shapes.AddTextbox(1, 40 * px_to_pt, 30 * px_to_pt, 1200 * px_to_pt, 40 * px_to_pt)
    title.TextFrame.TextRange.Text = "智言平台技术架构"
    title.TextFrame.TextRange.Font.Name = "Microsoft YaHei"
    title.TextFrame.TextRange.Font.Size = 32
    title.TextFrame.TextRange.Font.Bold = True
    title.TextFrame.TextRange.Font.Color.RGB = 0x1E293B
    title.TextFrame.TextRange.ParagraphFormat.Alignment = 2  # center
    
    # 四层架构数据
    layers = [
        ("用户交互层", "Web端 | 小程序 | API接口 | 管理后台", colors['primary']),
        ("业务应用层", "智能客服 | 知识问答 | 内容生成 | 数据分析", colors['secondary']),
        ("模型引擎层", "基座大模型 | 领域微调 | RAG检索 | 推理加速", colors['accent']),
        ("基础设施层", "国产化算力 | 容器编排 | 安全网关 | 监控运维", colors['neutral']),
    ]
    
    box_w = 1100 * px_to_pt
    box_h = 95 * px_to_pt
    start_y = 110 * px_to_pt
    gap_y = 30 * px_to_pt
    center_x = sw / 2
    
    shapes_list = []
    for i, (name, comps, color) in enumerate(layers):
        left = center_x - box_w / 2
        top = start_y + i * (box_h + gap_y)
        
        # 主框
        shape = add_rounded_rect(slide, left, top, box_w, box_h, color, name)
        shapes_list.append(shape)
        
        # 子组件（放在主框内部下方，小字）
        comp_shape = slide.Shapes.AddTextbox(1, left, top + 52 * px_to_pt, box_w, 36 * px_to_pt)
        comp_shape.TextFrame.TextRange.Text = comps
        comp_shape.TextFrame.TextRange.Font.Name = "Microsoft YaHei"
        comp_shape.TextFrame.TextRange.Font.Size = 14
        comp_shape.TextFrame.TextRange.Font.Color.RGB = 0xFFFFFF
        comp_shape.TextFrame.TextRange.ParagraphFormat.Alignment = 2
        comp_shape.TextFrame.VerticalAnchor = 3
    
    # 添加连接箭头
    for i in range(len(shapes_list) - 1):
        s1 = shapes_list[i]
        s2 = shapes_list[i + 1]
        x1 = s1.Left + s1.Width / 2
        y1 = s1.Top + s1.Height
        x2 = s2.Left + s2.Width / 2
        y2 = s2.Top
        add_arrow(slide, x1, y1, x2, y2)
    
    # 导出为 PNG
    os.makedirs(os.path.dirname(OUTPUT_PNG), exist_ok=True)
    # Slide.Export(FileName, FilterName, ScaleWidth, ScaleHeight)
    slide.Export(OUTPUT_PNG, "PNG", 1920, 1080)
    print(f"Architecture diagram exported to: {OUTPUT_PNG}")
    
    # 保存一个副本
    prs.SaveAs(os.path.abspath(r'academic_diagrams_run\architecture_ppt.pptx'), 24)
    
    # 清理
    prs.Close()
    ppt.Quit()
    proc.kill()
    time.sleep(1)
    subprocess.run(['taskkill', '/F', '/IM', 'POWERPNT.EXE'], capture_output=True)
    subprocess.run(['taskkill', '/F', '/IM', 'wpp.exe'], capture_output=True)
    print("Done.")

if __name__ == "__main__":
    main()
