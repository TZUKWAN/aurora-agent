import json

with open('outline_with_prompts.json','r',encoding='utf-8') as f:
    data = json.load(f)

sections = data['sections']

# Batch 2 (20-38) -> 3 small batches
b2a = sections[19:26]  # 20-26
b2b = sections[26:32]  # 27-32
b2c = sections[32:38]  # 33-38

# Batch 3 (39-57) -> 3 small batches
b3a = sections[38:45]  # 39-45
b3b = sections[45:51]  # 46-51
b3c = sections[51:57]  # 52-57

for name, batch in [
    ('batch_small_2a.json', b2a),
    ('batch_small_2b.json', b2b),
    ('batch_small_2c.json', b2c),
    ('batch_small_3a.json', b3a),
    ('batch_small_3b.json', b3b),
    ('batch_small_3c.json', b3c),
]:
    with open(name, 'w', encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
    print(f'{name}: {len(batch)} sections')
