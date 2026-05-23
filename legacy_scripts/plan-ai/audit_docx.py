#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""审计所有DOCX中的图片占位符情况"""
import json
import re
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn

BASE = Path(r"D:\计划书AI\output_v2")
projects = json.loads((BASE / "projects_list.json").read_text(encoding="utf-8"))

def find_docx(name):
    for f in BASE.glob("*.docx"):
        if name in f.name and not f.name.startswith("~"):
            return f
    return None

def audit_docx(project):
    path = find_docx(project["name"])
    if not path:
        return None
    doc = Document(str(path))
    results = {"fig_captions": [], "images": 0, "empty_paras_before_fig": 0}
    paras = doc.paragraphs
    for i, p in enumerate(paras):
        text = p.text.strip()
        # 图注
        m = re.match(r'^(图\d+-\d+)\s', text)
        if m:
            fig_key = m.group(1)
            has_img = False
            if i > 0:
                prev = paras[i-1]
                has_img = any(r._element.findall(qn('w:drawing')) for r in prev.runs)
            results["fig_captions"].append({"fig": fig_key, "has_image": has_img})
            if i > 0 and not paras[i-1].text.strip():
                results["empty_paras_before_fig"] += 1
        # 任意段落中的图片
        if any(r._element.findall(qn('w:drawing')) for r in p.runs):
            results["images"] += 1
    return results

print("=" * 80)
all_figs = set()
problematic = []
for p in projects:
    r = audit_docx(p)
    if not r:
        problematic.append((p["name"], "DOCX not found"))
        continue
    figs = [x["fig"] for x in r["fig_captions"]]
    missing = [x["fig"] for x in r["fig_captions"] if not x["has_image"]]
    all_figs.update(figs)
    if missing:
        problematic.append((p["name"], missing))
    print(f"{p['name']:12s}: {len(r['fig_captions'])} fig captions, {r['images']} images, missing: {missing if missing else 'None'}")

print("\n" + "=" * 80)
print(f"All unique figure keys across 49 docs: {sorted(all_figs)}")
print(f"\nProjects with missing images: {len(problematic)}")
for name, issue in problematic[:10]:
    print(f"  {name}: {issue}")
