#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean up orphaned images from DOCX files.
An orphaned image is one that exists in word/media/ but is not referenced
by any document part (document, headers, footers, etc.).
"""
import os
import re
import shutil
import time
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

BASE_DIR = Path(r"D:\计划书AI")
OUTPUT_DIR = BASE_DIR / "output_v2"
TMP_DIR = BASE_DIR / "tmp_docx_cleanup"

# Namespaces
NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}
RID_EMBED = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'


def get_all_embed_references(zip_file):
    """Find all embed rIds referenced in all XML parts."""
    embeds = set()
    
    for item in zip_file.namelist():
        if not item.endswith('.xml') and not item.endswith('.rels'):
            continue
        
        try:
            content = zip_file.read(item)
            root = ET.fromstring(content)
            for blip in root.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
                embed = blip.get(RID_EMBED)
                if embed:
                    embeds.add(embed)
        except ET.ParseError:
            pass
    
    return embeds


def cleanup_docx(docx_path):
    """Remove orphaned images and their relationships from a DOCX."""
    with zipfile.ZipFile(docx_path, 'r') as zin:
        embeds = get_all_embed_references(zin)
        
        # Parse all .rels files
        rels_files = {}
        for item in zin.namelist():
            if item.endswith('.rels'):
                rels_files[item] = zin.read(item).decode('utf-8')
        
        # For each rels file, find image relationships and check if referenced
        # Map: rels_file -> set of rIds to keep
        keep_rids = {}
        orphaned_media = set()
        
        for rels_path, rels_content in rels_files.items():
            keep_rids[rels_path] = set()
            # Parse relationships
            root = ET.fromstring(rels_content)
            for rel in root.iter('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                rid = rel.get('Id')
                target = rel.get('Target')
                rel_type = rel.get('Type', '')
                
                if 'image' in rel_type:
                    if rid in embeds:
                        keep_rids[rels_path].add(rid)
                    else:
                        # Orphaned image relationship
                        media_file = target.replace('../', '').replace('media/', '')
                        orphaned_media.add(media_file)
                else:
                    keep_rids[rels_path].add(rid)
        
        if not orphaned_media:
            return 0, 0
        
        # Create cleaned DOCX
        tmp_path = TMP_DIR / docx_path.name
        tmp_path.parent.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.namelist():
                if item.startswith('word/media/') and item.replace('word/media/', '') in orphaned_media:
                    continue  # Skip orphaned media
                
                if item.endswith('.rels'):
                    # Filter out orphaned relationships
                    rels_content = rels_files[item]
                    root = ET.fromstring(rels_content)
                    new_root = ET.Element('{http://schemas.openxmlformats.org/package/2006/relationships}Relationships')
                    for rel in root.iter('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                        rid = rel.get('Id')
                        if rid in keep_rids[item]:
                            new_root.append(rel)
                    
                    # Write modified rels
                    ET.register_namespace('', 'http://schemas.openxmlformats.org/package/2006/relationships')
                    new_content = ET.tostring(new_root, encoding='UTF-8', xml_declaration=True)
                    zout.writestr(item, new_content)
                else:
                    zout.writestr(item, zin.read(item))
    
    # Replace original with cleaned version
    old_size = docx_path.stat().st_size
    shutil.move(str(tmp_path), str(docx_path))
    new_size = docx_path.stat().st_size
    
    return len(orphaned_media), old_size - new_size


def main():
    print("=" * 60)
    print(" 清理 orphaned 图片")
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
