import json

with open('outline_with_prompts.json','r',encoding='utf-8') as f:
    data = json.load(f)

sections = data['sections']

# Batch 1 (1-19)
b1a = sections[0:6]   # 1-6
b1b = sections[6:13]  # 7-13
b1c = sections[13:19] # 14-19

# Batch 4 (58-76)
b4a = sections[57:64] # 58-64
b4b = sections[64:71] # 65-71
b4c = sections[71:76] # 72-76

for name, batch in [
    ('batch_small_1a.json', b1a),
    ('batch_small_1b.json', b1b),
    ('batch_small_1c.json', b1c),
    ('batch_small_4a.json', b4a),
    ('batch_small_4b.json', b4b),
    ('batch_small_4c.json', b4c),
]:
    with open(name, 'w', encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
    print(f'{name}: {len(batch)} sections')
