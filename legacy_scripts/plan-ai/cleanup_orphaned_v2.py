#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean up orphaned images from DOCX files - version 2.
Removes any image files in word/media/ that are not referenced by any .rels file.
"""
import os
import re
import shutil
import time
import zipfile
from pathlib import Path

BASE_DIR = Path(r"D:\计划书AI")
OUTPUT_DIR = BASE_DIR / "output_v2"
TMP_DIR = BASE_DIR / "tmp_docx_cleanup_v2"


def cleanup_docx(docx_path):
    """Remove orphaned images from a DOCX file."""
    with zipfile.ZipFile(docx_path, 'r') as zin:
        # Find all referenced media files across all .rels files
        referenced_media = set()
        for item in zin.namelist():
            if not item.endswith('.rels'):
                continue
            content = zin.read(item).decode('utf-8')
            # Find all image targets
            targets = re.findall(r'Target="([^"]*media[^"]*)"', content)
            for t in targets:
                # Normalize path: ../media/image.png -> word/media/image.png
                if t.startswith('../'):
                    t = t[3:]  # Remove ../
                elif not t.startswith('word/'):
                    t = 'word/' + t
                referenced_media.add(t)
        
        # Find all media files in the zip
        all_media = set(f for f in zin.namelist() if f.startswith('word/media/'))
        orphaned = all_media - referenced_media
        
        if not orphaned:
            return 0, 0
        
        # Create cleaned DOCX
        tmp_path = TMP_DIR / docx_path.name
        tmp_path.parent.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.namelist():
                if item in orphaned:
                    continue  # Skip orphaned media
                zout.writestr(item, zin.read(item))
    
    # Replace original with cleaned version
    old_size = docx_path.stat().st_size
    shutil.move(str(tmp_path), str(docx_path))
    new_size = docx_path.stat().st_size
    
    return len(orphaned), old_size - new_size


def main():
    print("=" * 60)
    print(" 清理 orphaned 图片 v2")
    print("=" * 60)
    
    docx_files = [f for f in OUTPUT_DIR.glob('*.docx') if not f.name.startswith('~$')]
    total = len(docx_files)
    total_orphaned = 0
    total_saved = 0
    
    t_start = time.time()
    for i, docx_path in enumerate(docx_files):
        t0 = time.time()
        orphaned, saved = cleanup_docx(docx_path)
        elapsed = time.time() - t0
        total_orphaned += orphaned
        total_saved += saved
        if orphaned > 0:
            print(f"[{i+1}/{total}] {docx_path.name[:20]}...: 删除 {orphaned} 张 orphaned 图片, 节省 {saved/1024/1024:.1f}MB ({elapsed:.1f}s)")
        else:
            print(f"[{i+1}/{total}] {docx_path.name[:20]}...: 无需清理 ({elapsed:.1f}s)")
    
    total_elapsed = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"完成: {total}个文档, 共删除 {total_orphaned} 张 orphaned 图片")
    print(f"总计节省 {total_saved/1024/1024:.1f}MB")
    print(f"耗时 {total_elapsed:.1f}s")
    print(f"{'='*60}")
    
    # Cleanup temp dir
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)


if __name__ == "__main__":
    main()
