#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pptx_to_png.py
用PowerPoint COM将每个PPT的38页导出为PNG
每3个项目重启一次PowerPoint，避免RPC崩溃
"""
import os
import sys
import json
import time
import subprocess
from pathlib import Path
import win32com.client

BASE_DIR = Path(r"D:\计划书AI")
PPTX_DIR = BASE_DIR / "output_v2" / "charts_pptx"
IMAGE_BASE = BASE_DIR / "output_v2" / "images"
PROJECTS_PATH = BASE_DIR / "output_v2" / "projects_list.json"

# 幻灯片序号 -> 图号文件名 (batch_insert_images.py 使用 图1_1.png 格式)
SLIDE_TO_FIG = {
    1:  "图1_1",   2:  "图1_2",   3:  "图1_3",   4:  "图1_4",
    5:  "图1_5",   6:  "图1_6",   7:  "图1_7",   8:  "图1_8",
    9:  "图1_9",   10: "图2_1",   11: "图2_2",   12: "图2_3",
    13: "图2_4",   14: "图2_5",   15: "图2_6",   16: "图2_11",
    17: "图2_12",  18: "图2_13",  19: "图2_15",  20: "图2_16",
    21: "图2_17",  22: "图2_18",  23: "图2_19",  24: "图2_20",
    25: "图2_21",  26: "图2_52",  27: "图2_55",  28: "图2_56",
    29: "图2_57",  30: "图2_58",  31: "图2_60",  32: "图2_61",
    33: "图2_53",  34: "图2_59",  35: "图2_54",  36: "图3_1",
    37: "图3_2",   38: "图4_1",
}

def kill_powerpoint():
    """强制结束所有PowerPoint进程"""
    subprocess.run(["taskkill", "/F", "/IM", "POWERPNT.EXE"], capture_output=True)
    time.sleep(1)

def start_powerpoint():
    """启动PowerPoint COM并返回应用对象"""
    ppt = win32com.client.Dispatch("PowerPoint.Application")
    try:
        ppt.Visible = False
    except Exception:
        pass
    try:
        ppt.DisplayAlerts = False
    except Exception:
        pass
    return ppt

def export_pptx(pptx_path, img_dir, ppt):
    """导出单个PPT的所有slide为PNG"""
    abs_pptx = str(pptx_path.resolve())
    presentation = ppt.Presentations.Open(abs_pptx, WithWindow=False)
    total_slides = presentation.Slides.Count

    for slide_idx in range(1, total_slides + 1):
        fig_name = SLIDE_TO_FIG.get(slide_idx)
        if not fig_name:
            continue
        out_path = img_dir / f"{fig_name}.png"
        slide = presentation.Slides(slide_idx)
        slide.Export(str(out_path), "PNG", 1920, 1080)

    presentation.Close()
    return total_slides

def process_batch(projects_batch, ppt):
    results = []
    for p in projects_batch:
        pptx_path = PPTX_DIR / f"p{p['idx']}_{p['name']}.pptx"
        if not pptx_path.exists():
            results.append((p, 0, "PPT不存在"))
            continue
        img_dir = IMAGE_BASE / f"p{p['idx']}"
        img_dir.mkdir(parents=True, exist_ok=True)
        try:
            count = export_pptx(pptx_path, img_dir, ppt)
            results.append((p, count, None))
        except Exception as e:
            results.append((p, 0, str(e)))
    return results

def main():
    projects = json.loads(PROJECTS_PATH.read_text(encoding="utf-8"))
    total = len(projects)
    batch_size = 3

    start_time = time.time()
    exported_total = 0

    for batch_start in range(0, total, batch_size):
        batch = projects[batch_start:batch_start + batch_size]
        batch_num = batch_start // batch_size + 1
        total_batches = (total + batch_size - 1) // batch_size

        # 启动PowerPoint
        kill_powerpoint()
        ppt = start_powerpoint()

        try:
            for p in batch:
                pptx_path = PPTX_DIR / f"p{p['idx']}_{p['name']}.pptx"
                if not pptx_path.exists():
                    print(f"  [{p['idx']+1}/{total}] {p['name']}: PPT不存在")
                    continue

                img_dir = IMAGE_BASE / f"p{p['idx']}"
                img_dir.mkdir(parents=True, exist_ok=True)

                t0 = time.time()
                try:
                    count = export_pptx(pptx_path, img_dir, ppt)
                    elapsed = time.time() - t0
                    exported_total += count
                    print(f"  [{p['idx']+1}/{total}] {p['name']}: {count}张导出 ({elapsed:.1f}s)")
                except Exception as e:
                    print(f"  [{p['idx']+1}/{total}] {p['name']} ERROR: {e}")
        finally:
            # 关闭PowerPoint
            try:
                ppt.Quit()
            except Exception:
                pass
            kill_powerpoint()

    total_elapsed = time.time() - start_time
    print(f"\n完成: {total}个项目, 共导出 {exported_total} 张PNG, 耗时 {total_elapsed:.1f}s")

if __name__ == "__main__":
    main()
