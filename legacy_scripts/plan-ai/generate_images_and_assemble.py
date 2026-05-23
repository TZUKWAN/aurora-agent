#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_images_and_assemble.py
为49个项目的商业计划书批量生成图片并插入到DOCX文档的正确位置。

图片分布：
  第一章 (9张):  企业概况图、发展战略路线图、SWOT分析图、组织架构图、产品矩阵图等
  第二章 (61张): 产业链图、市场趋势图、产品架构图、功能截图(30张)、客户画像图、
                  竞争格局图、产品界面展示图(30张)、技术架构图(10张)等
  第三章 (2张):  资金用途图、融资里程碑图
  第四章 (1张):  风险矩阵图

使用方法：
  python generate_images_and_assemble.py [--project-index 0] [--skip-screenshots] [--skip-charts] [--skip-assemble]
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

# ---------------------------------------------------------------------------
# 路径配置
# ---------------------------------------------------------------------------
BASE_DIR = Path(r"D:\计划书AI")
EXCEL_PATH = BASE_DIR / "省补贴项目清单.xlsx"
OUTPUT_DIR = BASE_DIR / "output_v2"

SCREENSHOT_SCRIPT = Path(
    r"C:\Users\lauze\.claude\skills\business-plan-writer"
    r"\subskills\bpw-product-screenshots\scripts\screenshot.py"
)
CHART_SCRIPT = Path(
    r"C:\Users\lauze\.claude\skills\business-plan-writer\scripts\chart_generator.py"
)

# ---------------------------------------------------------------------------
# 图片编号 -> 图片类型映射
# 每个占位符（如 "图 1-1"）对应一种图片，key 为 "章-序号"
# ---------------------------------------------------------------------------

# 第一章: 图 1-1 ~ 图 1-9
CH1_MAP = {
    "1-1": {"type": "architecture", "title_key": "企业概况展示"},
    "1-2": {"type": "gantt",        "title_key": "发展战略路线图"},
    "1-3": {"type": "competition",  "title_key": "波特六力模型分析图"},
    "1-4": {"type": "swot",         "title_key": "SWOT分析矩阵图"},
    "1-5": {"type": "architecture", "title_key": "研发规划架构图"},
    "1-6": {"type": "architecture", "title_key": "产品矩阵图"},
    "1-7": {"type": "architecture", "title_key": "服务体系架构图"},
    "1-8": {"type": "architecture", "title_key": "营销渠道架构图"},
    "1-9": {"type": "architecture", "title_key": "组织架构图"},
}

# 第二章: 图 2-1 ~ 图 2-21 (图表类)
CH2_CHART_MAP = {
    "2-1":  {"type": "architecture",  "title_key": "行业产业链图谱"},
    "2-2":  {"type": "architecture",  "title_key": "市场规模增长趋势图"},
    "2-3":  {"type": "architecture",  "title_key": "市场趋势分析图"},
    "2-4":  {"type": "architecture",  "title_key": "产品功能架构图"},
    "2-5":  {"type": "architecture",  "title_key": "系统技术架构图"},
    "2-6":  {"type": "architecture",  "title_key": "核心模块架构图"},
    "2-7":  {"type": "architecture",  "title_key": "功能模块1架构图"},
    "2-8":  {"type": "architecture",  "title_key": "功能模块2架构图"},
    "2-9":  {"type": "architecture",  "title_key": "功能模块3架构图"},
    "2-10": {"type": "architecture",  "title_key": "客户分类架构图"},
    "2-11": {"type": "architecture",  "title_key": "目标客户画像图"},
    "2-12": {"type": "architecture",  "title_key": "产品优势对比图"},
    "2-13": {"type": "architecture",  "title_key": "服务体系架构图"},
    "2-14": {"type": "architecture",  "title_key": "应用案例展示图"},
    "2-15": {"type": "architecture",  "title_key": "案例效果对比图"},
    "2-16": {"type": "architecture",  "title_key": "市场占有率分析图"},
    "2-17": {"type": "architecture",  "title_key": "市场增长趋势图"},
    "2-18": {"type": "architecture",  "title_key": "收入构成分析图"},
    "2-19": {"type": "architecture",  "title_key": "收入趋势预测图"},
    "2-20": {"type": "competition",   "title_key": "竞争格局矩阵图"},
    "2-21": {"type": "competition",   "title_key": "竞争对手分析图"},
}

# 第二章: 图 2-22 ~ 图 2-51 为产品界面展示图 (30张, 使用截图)
# 第二章: 图 2-52 ~ 图 2-61 为技术架构图集 (10张)

CH2_TECH_MAP = {
    "2-52": {"type": "architecture", "title_key": "系统整体架构图"},
    "2-53": {"type": "architecture", "title_key": "数据流架构图"},
    "2-54": {"type": "architecture", "title_key": "核心算法架构图"},
    "2-55": {"type": "architecture", "title_key": "微服务架构图"},
    "2-56": {"type": "architecture", "title_key": "数据库架构图"},
    "2-57": {"type": "architecture", "title_key": "安全架构图"},
    "2-58": {"type": "architecture", "title_key": "部署架构图"},
    "2-59": {"type": "architecture", "title_key": "API架构图"},
    "2-60": {"type": "architecture", "title_key": "前端架构图"},
    "2-61": {"type": "architecture", "title_key": "运维监控架构图"},
}

# 第三章: 图 3-1 ~ 图 3-2
CH3_MAP = {
    "3-1": {"type": "architecture", "title_key": "资金用途分布图"},
    "3-2": {"type": "gantt",        "title_key": "融资里程碑规划图"},
}

# 第四章: 图 4-1
CH4_MAP = {
    "4-1": {"type": "swot",  "title_key": "风险矩阵分析图"},
}

# 合并所有图表类映射（不含截图）
ALL_CHART_MAP = {}
ALL_CHART_MAP.update(CH1_MAP)
ALL_CHART_MAP.update(CH2_CHART_MAP)
ALL_CHART_MAP.update(CH2_TECH_MAP)
ALL_CHART_MAP.update(CH3_MAP)
ALL_CHART_MAP.update(CH4_MAP)


# ---------------------------------------------------------------------------
# 1. 读取项目清单
# ---------------------------------------------------------------------------
def load_project_list():
    """从Excel读取49个项目"""
    try:
        import openpyxl
    except ImportError:
        print("[ERROR] 缺少 openpyxl，请运行 pip install openpyxl")
        sys.exit(1)

    wb = openpyxl.load_workbook(str(EXCEL_PATH))
    ws = wb.active
    projects = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        title = row[0]
        if not title:
            continue
        desc = row[1] or ""
        company = row[2] or ""
        legal_person = row[3] or ""
        projects.append({
            "title": str(title).strip(),
            "desc": str(desc).strip(),
            "company": str(company).strip(),
            "legal_person": str(legal_person).strip(),
        })
    print(f"[INFO] 从清单读取到 {len(projects)} 个项目")
    return projects


def find_docx_for_project(project_title):
    """根据项目标题找到对应的DOCX文件"""
    # 项目标题格式: "智灵视界——基于少样本学习的..."
    # DOCX文件名格式: "【智灵视界——基于少样本学习的...】湖北省大学生创业扶持项目商业计划书.docx"
    target = f"【{project_title}】"
    for f in os.listdir(str(OUTPUT_DIR)):
        if f.endswith(".docx") and not f.startswith("~"):
            if target in f:
                return OUTPUT_DIR / f
    return None


def get_product_name(project_title):
    """从标题中提取产品名（破折号之前的部分）"""
    for sep in ["——", "—", "–", "-"]:
        if sep in project_title:
            return project_title.split(sep)[0].strip()
    return project_title[:6]


# ---------------------------------------------------------------------------
# 2. 生成产品截图 (32张)
# ---------------------------------------------------------------------------
def generate_product_screenshots(project_name, project_desc, output_dir):
    """为项目生成32张产品截图"""
    images_dir = output_dir / "screenshots"
    images_dir.mkdir(parents=True, exist_ok=True)

    # 创建 project.json 供 screenshot.py 使用
    project_info = {
        "product_name": project_name,
        "company_name": project_name + "科技",
        "project_desc": project_desc,
    }
    json_path = images_dir / "project.json"
    json_path.write_text(
        json.dumps(project_info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    cmd = [
        sys.executable, str(SCREENSHOT_SCRIPT),
        "--input", str(json_path),
        "--output-dir", str(images_dir),
        "--count", "32",
    ]
    print(f"  [截图] 生成 {project_name} 的产品截图 -> {images_dir}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            print(f"  [WARN] 截图生成返回码 {result.returncode}: {result.stderr[:200]}")
        else:
            print(f"  [截图] 完成")
    except subprocess.TimeoutExpired:
        print(f"  [WARN] 截图生成超时 (10分钟)")
    except Exception as e:
        print(f"  [WARN] 截图生成异常: {e}")

    return images_dir


# ---------------------------------------------------------------------------
# 3. 生成各类图表
# ---------------------------------------------------------------------------
def _create_chart_json(output_dir, fig_key, chart_type, project_name):
    """为图表生成创建输入JSON"""
    json_dir = output_dir / "chart_json"
    json_dir.mkdir(parents=True, exist_ok=True)
    json_path = json_dir / f"{fig_key}.json"

    if chart_type == "swot":
        data = {
            "s": "自主研发核心技术\n产学研深度合作\n轻量化部署方案\n数据安全可控",
            "w": "品牌知名度较低\n团队规模有限\n市场渠道待拓展\n商业化经验不足",
            "o": "数字化转型加速\n国产替代政策利好\n行业垂直需求增长\n技术壁垒持续提升",
            "t": "头部厂商竞争加剧\n开源方案冲击市场\n合规监管趋严\n人才争夺激烈",
        }
    elif chart_type == "gantt":
        data = {
            "phases": [
                {"name": "技术研发", "start_month": 1, "duration_months": 6,
                 "milestones": ["基座开发", "领域微调"]},
                {"name": "产品开发", "start_month": 4, "duration_months": 6,
                 "milestones": ["内测上线", "迭代优化"]},
                {"name": "市场推广", "start_month": 7, "duration_months": 7,
                 "milestones": ["试点推广", "品牌发布"]},
                {"name": "规模运营", "start_month": 10, "duration_months": 9,
                 "milestones": ["付费转化", "生态拓展"]},
                {"name": "生态构建", "start_month": 16, "duration_months": 9,
                 "milestones": ["平台开放", "行业拓展"]},
            ]
        }
    elif chart_type == "competition":
        data = {
            "players": [
                {"name": project_name, "x": 8, "y": 8.5, "size": 90,
                 "color": 0x8E9AAF, "desc": "细分领域\n轻量化方案"},
                {"name": "头部云厂商", "x": 9, "y": 4, "size": 110,
                 "color": 0xA5A5A5, "desc": "通用平台\n生态壁垒高"},
                {"name": "垂直初创A", "x": 5.5, "y": 7.5, "size": 70,
                 "color": 0xB7B7A4, "desc": "垂直深耕\n品牌弱"},
                {"name": "垂直初创B", "x": 4, "y": 6, "size": 65,
                 "color": 0xB7B7A4, "desc": "垂直深耕\n渠道弱"},
                {"name": "开源集成商", "x": 4, "y": 2.5, "size": 75,
                 "color": 0xA2A392, "desc": "灵活低成本\n维护门槛高"},
            ]
        }
    elif chart_type == "architecture":
        data = {"title": f"{project_name} 系统架构与数据流框架"}
    elif chart_type == "bmc":
        data = {
            "kp": "高校实验室\n算力供应商\n渠道伙伴",
            "ka": "模型训练\n产品开发\n客户成功",
            "kr": "技术团队\n专利资产\n行业数据",
            "vp": "低成本垂直大模型服务\n私有化部署\n数据安全",
            "cr": "顾问式服务\n社群运营\n培训支持",
            "ch": "直销团队\n代理商\nAPI平台",
            "cs": "中小企业\n政务机构\n事业单位",
            "cst": "研发投入\n算力成本\n人力支出",
            "rs": "订阅费\nAPI调用费\n定制开发",
        }
    elif chart_type == "value_chain":
        data = {"nodes": [], "edges": []}
    else:
        data = {"title": project_name}

    json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return json_path


def generate_charts(project_name, project_desc, output_dir):
    """为项目生成所有图表图片"""
    charts_dir = output_dir / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    generated = {}
    for fig_key, info in ALL_CHART_MAP.items():
        chart_type = info["type"]
        title_key = info["title_key"]
        out_path = charts_dir / f"fig_{fig_key}_{chart_type}.png"

        if out_path.exists():
            generated[fig_key] = out_path
            continue

        json_path = _create_chart_json(output_dir, fig_key, chart_type, project_name)

        cmd = [
            sys.executable, str(CHART_SCRIPT),
            "--type", chart_type,
            "--input", str(json_path),
            "--output", str(out_path),
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                print(f"  [WARN] 图表 {fig_key} ({chart_type}) 生成失败: {result.stderr[:150]}")
            else:
                generated[fig_key] = out_path
        except subprocess.TimeoutExpired:
            print(f"  [WARN] 图表 {fig_key} ({chart_type}) 生成超时")
        except Exception as e:
            print(f"  [WARN] 图表 {fig_key} ({chart_type}) 异常: {e}")

        # PPT引擎频繁启停需要间隔
        time.sleep(2)

    print(f"  [图表] 成功生成 {len(generated)}/{len(ALL_CHART_MAP)} 张图表")
    return charts_dir, generated


# ---------------------------------------------------------------------------
# 4. 将图片插入DOCX
# ---------------------------------------------------------------------------
def insert_images_into_docx(docx_path, images_base_dir, screenshots_dir, charts_dir, chart_map, project_name):
    """
    将图片插入到DOCX的正确位置。

    策略：
    1. 遍历文档中的所有表格
    2. 识别包含"请插入图片"文字的占位表格
    3. 从表格标签中提取图片编号 (如 "图 1-1")
    4. 根据编号匹配对应的图片文件
    5. 用图片替换占位表格内容
    """
    try:
        from docx import Document
        from docx.shared import Cm, Pt, Inches, Emu
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
    except ImportError:
        print("[ERROR] 缺少 python-docx，请运行 pip install python-docx")
        return False

    if not docx_path.exists():
        print(f"  [ERROR] DOCX文件不存在: {docx_path}")
        return False

    doc = Document(str(docx_path))

    # 收集截图文件列表
    screenshot_files = sorted(screenshots_dir.glob("product_*.png")) if screenshots_dir.exists() else []

    inserted = 0
    skipped = 0

    for table in doc.tables:
        cell = table.rows[0].cells[0]
        cell_text = cell.text.strip()
        if "请插入图片" not in cell_text:
            continue

        # 提取图片编号: "【图 1-1 区域 - 请插入图片】" -> "1-1"
        match = re.search(r"图\s*(\d+-\d+)", cell_text)
        if not match:
            skipped += 1
            continue

        fig_key = match.group(1)  # e.g. "1-1"
        image_path = _resolve_image(fig_key, charts_dir, chart_map, screenshots_dir, screenshot_files)

        if not image_path or not Path(image_path).exists():
            skipped += 1
            continue

        # 清空单元格内容
        _clear_cell(cell)

        # 在单元格中插入图片
        try:
            _insert_image_to_cell(cell, str(image_path))
            inserted += 1
        except Exception as e:
            print(f"  [WARN] 插入图片 {fig_key} 失败: {e}")
            skipped += 1

    if inserted > 0:
        # 保存文档
        backup_path = docx_path.with_suffix(".docx.bak")
        if not backup_path.exists():
            shutil.copy2(str(docx_path), str(backup_path))
        doc.save(str(docx_path))
        print(f"  [组装] 插入 {inserted} 张图片，跳过 {skipped} 个占位，已保存")
    else:
        print(f"  [WARN] 未插入任何图片")

    return inserted > 0


def _resolve_image(fig_key, charts_dir, chart_map, screenshots_dir, screenshot_files):
    """根据图片编号解析图片路径"""
    # 优先从图表映射中查找（覆盖所有章节的图表类占位符）
    if fig_key in chart_map:
        return chart_map[fig_key]

    # 第二章产品截图: 2-22 ~ 2-51 (共30张)
    parts = fig_key.split("-")
    if len(parts) == 2 and parts[0] == "2":
        try:
            fig_num = int(parts[1])
            if 22 <= fig_num <= 51:
                idx = fig_num - 22  # 0-29
                if idx < len(screenshot_files):
                    return screenshot_files[idx]
        except ValueError:
            pass

    # 兜底: 在charts_dir中查找文件名包含fig_key的文件
    if charts_dir and charts_dir.exists():
        for f in charts_dir.iterdir():
            if f.is_file() and fig_key in f.name and f.suffix == ".png":
                return f

    return None


def _clear_cell(cell):
    """清空表格单元格内容"""
    tc = cell._tc
    for p in tc.findall(qn('w:p')):
        tc.remove(p)
    # 保留一个空段落
    new_p = OxmlElement('w:p')
    tc.append(new_p)


def _insert_image_to_cell(cell, image_path, width_cm=15):
    """在表格单元格中插入图片"""
    from docx.shared import Cm, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    paragraphs = cell.paragraphs
    if not paragraphs:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        new_p = OxmlElement('w:p')
        cell._tc.append(new_p)
        paragraphs = cell.paragraphs

    p = paragraphs[0]

    # 设置段落居中
    pPr = p._element.get_or_add_pPr()
    jc = OxmlElement('w:jc')
    jc.set(qn('w:val'), 'center')
    pPr.append(jc)

    # 添加图片
    run = p.add_run()
    run.add_picture(image_path, width=Cm(width_cm))


# ---------------------------------------------------------------------------
# 5. 单项目处理流程
# ---------------------------------------------------------------------------
def process_project(project, index, total, skip_screenshots=False, skip_charts=False, skip_assemble=False):
    """处理单个项目：生成图片 + 组装DOCX"""
    title = project["title"]
    desc = project["desc"]
    product_name = get_product_name(title)

    print(f"\n{'='*70}")
    print(f"[{index+1}/{total}] 处理项目: {title}")
    print(f"  产品名: {product_name}")
    print(f"{'='*70}")

    # 查找DOCX
    docx_path = find_docx_for_project(title)
    if not docx_path:
        print(f"  [ERROR] 未找到对应的DOCX文件，跳过")
        return False
    print(f"  DOCX: {docx_path.name}")

    # 创建图片输出目录
    images_dir = OUTPUT_DIR / "images" / f"project_{index+1:02d}"
    images_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: 生成产品截图
    screenshots_dir = images_dir / "screenshots"
    if not skip_screenshots:
        generate_product_screenshots(product_name, desc, images_dir)
    else:
        print(f"  [跳过] 截图生成")

    # Step 2: 生成图表
    chart_map_generated = {}
    charts_dir = images_dir / "charts"
    if not skip_charts:
        charts_dir, chart_map_generated = generate_charts(product_name, desc, images_dir)
    else:
        print(f"  [跳过] 图表生成")

    # Step 3: 组装DOCX
    if not skip_assemble:
        success = insert_images_into_docx(
            docx_path, images_dir, screenshots_dir, charts_dir,
            chart_map_generated, product_name
        )
        if success:
            print(f"  [OK] 项目 {index+1} 处理完成")
        else:
            print(f"  [WARN] 项目 {index+1} 组装未成功")
        return success
    else:
        print(f"  [跳过] DOCX组装")
        return True


# ---------------------------------------------------------------------------
# 6. 主流程
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="为49个项目批量生成图片并组装DOCX文档"
    )
    parser.add_argument(
        "--project-index", type=int, default=-1,
        help="只处理指定索引的项目 (0-based)，不指定则处理全部"
    )
    parser.add_argument(
        "--start-from", type=int, default=0,
        help="从指定索引开始处理 (0-based)"
    )
    parser.add_argument(
        "--skip-screenshots", action="store_true",
        help="跳过截图生成"
    )
    parser.add_argument(
        "--skip-charts", action="store_true",
        help="跳过图表生成"
    )
    parser.add_argument(
        "--skip-assemble", action="store_true",
        help="跳过DOCX组装"
    )
    args = parser.parse_args()

    print("=" * 70)
    print(" 商业计划书图片生成与文档组装工具")
    print("=" * 70)
    print(f" 项目清单: {EXCEL_PATH}")
    print(f" 输出目录: {OUTPUT_DIR}")
    print(f" 截图脚本: {SCREENSHOT_SCRIPT}")
    print(f" 图表脚本: {CHART_SCRIPT}")
    print()

    # 验证关键文件存在
    if not EXCEL_PATH.exists():
        print(f"[FATAL] 项目清单不存在: {EXCEL_PATH}")
        sys.exit(1)
    if not OUTPUT_DIR.exists():
        print(f"[FATAL] 输出目录不存在: {OUTPUT_DIR}")
        sys.exit(1)

    # 读取项目清单
    projects = load_project_list()
    if not projects:
        print("[FATAL] 未读取到任何项目")
        sys.exit(1)

    total = len(projects)
    success_count = 0
    fail_count = 0

    start_time = time.time()

    if args.project_index >= 0:
        # 处理单个项目
        idx = args.project_index
        if idx >= total:
            print(f"[FATAL] 项目索引 {idx} 超出范围 (共 {total} 个)")
            sys.exit(1)
        result = process_project(
            projects[idx], idx, total,
            skip_screenshots=args.skip_screenshots,
            skip_charts=args.skip_charts,
            skip_assemble=args.skip_assemble,
        )
        if result:
            success_count = 1
        else:
            fail_count = 1
    else:
        # 批量处理
        for idx in range(args.start_from, total):
            try:
                result = process_project(
                    projects[idx], idx, total,
                    skip_screenshots=args.skip_screenshots,
                    skip_charts=args.skip_charts,
                    skip_assemble=args.skip_assemble,
                )
                if result:
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                print(f"  [ERROR] 项目 {idx+1} 处理异常: {e}")
                traceback.print_exc()
                fail_count += 1

    elapsed = time.time() - start_time
    print(f"\n{'='*70}")
    print(f" 处理完成！")
    print(f" 成功: {success_count}, 失败: {fail_count}, 耗时: {elapsed:.1f}秒")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
