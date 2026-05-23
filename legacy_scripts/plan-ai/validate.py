import json

with open('content_small_4c.json', encoding='utf-8') as f:
    data = json.load(f)

forbidden = ['首先','其次','再次','最后','重构','重建','颠覆','填补空白','——','如何','何以','为何']
issues = []
for sec in data['sections']:
    for w in forbidden:
        if w in sec['content']:
            issues.append(f'Found forbidden word {w} in section {sec["id"]}')
    if '"' in sec['content']:
        issues.append(f'Found quote in section {sec["id"]}')

if issues:
    for i in issues:
        print(i)
else:
    print('No forbidden words or quotes found.')
