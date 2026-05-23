import json

with open('D:\\计划书AI\\content_small_2b.json', encoding='utf-8') as f:
    data = json.load(f)

all_text = ''.join(s['content'] for s in data['sections'])

forbidden = ['首先', '其次', '再次', '最后', '重构', '重建', '颠覆', '填补空白', '——', '如何', '何以', '为何', '"', '“', '”']
found = []
for w in forbidden:
    if w in all_text:
        found.append(w)

if found:
    print('Found forbidden:', found)
else:
    print('No forbidden words found.')

print('File is valid JSON with', len(data['sections']), 'sections')

# Also verify first sentences of section 27
s27 = data['sections'][0]['content']
paras = [p for p in s27.split('\n\n') if p.strip()]
print('Section 27 paragraphs:', len(paras))
for i, p in enumerate(paras):
    first_sentence = p.split('。')[0] + '。'
    print(f'  Para {i+1} first sentence ({len(first_sentence)} chars): {first_sentence}')
