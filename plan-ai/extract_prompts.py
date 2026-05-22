#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
from docx import Document
from pathlib import Path

# 读取 Word 文档
doc = Document('商业计划书大纲2026.docx')
paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

# 读取 outline
outline = json.loads(Path('outline_run.json').read_text(encoding='utf-8'))
sections = outline['sections']

# 提取 prompt 的启发式规则：包含特定关键词
prompt_keywords = [
    '请你为我', '请为我', '接下来，请你', '接下来，请',
    '请你分析', '请分析', '请撰写', '请设计',
    '这个问题看似简单', '让我们一步一步来'
]

def is_prompt(text):
    return any(kw in text for kw in prompt_keywords)

def is_table_row(text):
    # 有多个制表符或看起来像财务表格
    return text.count('\t') >= 3 or re.search(r'20\d{2}年度', text)

# 为每个 section 查找 prompt
# 策略：在 paragraphs 中找到 section title 的位置，然后收集后续属于该 section 的 prompt 段落
# 直到遇到下一个 section title
section_prompts = {}

# 先建立 title -> 出现次数映射，处理重复标题
title_counts = {}
for sec in sections:
    t = sec['title']
    title_counts[t] = title_counts.get(t, 0) + 1

# 建立 section 列表（包含重复）
sec_list = [(s['title'], s['id']) for s in sections]

# 在 paragraphs 中按顺序匹配标题
# 由于文档中有些标题重复出现，我们需要按顺序匹配
matched = []  # list of (para_idx, title, sec_id)
title_occurrence = {}  # track which occurrence we are at

for i, text in enumerate(paragraphs):
    # 尝试匹配 section title
    for sec_title, sec_id in sec_list:
        if text == sec_title or text.startswith(sec_title):
            # 记录该 title 的第几次出现
            key = (sec_title, sec_id)
            # 找到第一个还没匹配的相同 title
            # 简化：直接用顺序匹配，因为文档中的标题顺序应该与 outline 一致
            if len(matched) < len(sec_list):
                expected_title, expected_id = sec_list[len(matched)]
                if text == expected_title or text.startswith(expected_title):
                    matched.append((i, expected_title, expected_id))
            break

print(f"Matched {len(matched)} sections out of {len(sec_list)}")

# 提取每个 matched section 的 prompt
for idx, (para_idx, title, sid) in enumerate(matched):
    start = para_idx + 1
    end = matched[idx + 1][0] if idx + 1 < len(matched) else len(paragraphs)
    
    prompt_parts = []
    for j in range(start, end):
        text = paragraphs[j]
        if is_table_row(text):
            continue
        if text == title:
            continue
        # 如果文本是下一个标题的重复（如 "公司介绍" 后面又跟了一个 "公司介绍"），跳过
        if idx + 1 < len(matched) and text == matched[idx+1][1]:
            continue
        prompt_parts.append(text)
    
    # 合并 prompt
    full_prompt = '\n'.join(prompt_parts)
    section_prompts[sid] = full_prompt

# 更新 outline
for sec in sections:
    sec['prompt'] = section_prompts.get(sec['id'], '')

Path('outline_with_prompts.json').write_text(json.dumps(outline, ensure_ascii=False, indent=2), encoding='utf-8')

# 打印统计
for sec in sections[:10]:
    print(f"ID {sec['id']:02d} {sec['title']}: prompt_len={len(sec['prompt'])}")
print("...")
for sec in sections[-5:]:
    print(f"ID {sec['id']:02d} {sec['title']}: prompt_len={len(sec['prompt'])}")

print(f"\nSaved outline_with_prompts.json with {len(sections)} sections")
