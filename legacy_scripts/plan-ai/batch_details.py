import json
with open('D:\\计划书AI\\batch_4.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for item in data:
    print(f"\n=== ID {item['id']}: {item['title']} ===")
    print(f"type: {item.get('type','')}")
    print(f"prompt: {item.get('prompt','')[:500] if item.get('prompt') else '(empty)'}")
    if item.get('fixed_text'):
        print(f"fixed_text: {item['fixed_text'][:300]}...")
    print(f"placeholders: {item.get('placeholders',[])}")
