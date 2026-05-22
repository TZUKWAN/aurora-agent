import json
from pathlib import Path

all_sections = []
files = [
    'content_small_1a.json',
    'content_small_1b.json',
    'content_small_1c.json',
    'content_small_2a.json',
    'content_small_2b.json',
    'content_small_2c.json',
    'content_small_3a.json',
    'content_small_3b.json',
    'content_small_3c.json',
    'content_small_4a.json',
    'content_small_4b.json',
    'content_small_4c.json',
]

for f in files:
    data = json.loads(Path(f).read_text(encoding='utf-8'))
    # 有些子 agent 返回的是 list，有些是 dict with sections key
    if isinstance(data, list):
        sections = data
    else:
        sections = data.get('sections', [])
    all_sections.extend(sections)
    print(f'{f}: {len(sections)} sections')

# 按 id 排序
all_sections.sort(key=lambda s: s['id'])

# 确保 id 连续且数量正确
ids = [s['id'] for s in all_sections]
print(f'Total sections: {len(all_sections)}, IDs: {min(ids)}-{max(ids)}')

output = {"sections": all_sections}
Path('content_all_merged.json').write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')

# 统计字数
total_chars = sum(len(s['content']) for s in all_sections)
print(f'Total Chinese characters: {total_chars}')
print(f'Average per section: {total_chars / len(all_sections):.0f}')
