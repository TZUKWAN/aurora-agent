import json

with open('outline_with_prompts.json','r',encoding='utf-8') as f:
    data = json.load(f)

sections = data['sections']

# 修正一些特殊 section
for sec in sections:
    if sec['id'] == 62 and sec['title'] == '现金流量表':
        sec['prompt'] = '请为我撰写本项目现金流量表的分析说明，阐述经营活动、投资活动与筹资活动对企业现金流的影响，并分析未来现金流趋势与风险。字数不少于800字。'
    if sec['id'] == 20 and sec['title'] == '核心技术':
        sec['prompt'] = '请为我撰写本项目的核心技术总览，系统介绍项目所依赖的关键技术体系、技术来源、技术成熟度及未来演进方向。字数不少于1200字。'
    if sec['id'] == 28 and sec['title'] == '市场分析':
        sec['prompt'] = '请为我撰写本项目的市场分析总论，概述市场整体规模、增长趋势、竞争格局及项目所处的市场机会。字数不少于1200字。'
    if sec['id'] == 36 and sec['title'] == '竞品分析':
        sec['prompt'] = '请为我撰写本项目的竞品分析总论，识别主要竞争力量并简要概述竞争态势。字数不少于1000字。'
    if sec['id'] == 39 and sec['title'] == '运营管理':
        sec['prompt'] = '请为我撰写本项目的运营管理体系，包括组织架构、核心流程、质量管理与绩效考核机制。字数不少于1200字。'
    if sec['id'] == 49 and sec['title'] == '营销战略':
        sec['prompt'] = '请为我撰写本项目的整体营销战略，包括品牌定位、传播策略、渠道规划及资源配置。字数不少于1200字。'
    if sec['id'] == 54 and sec['title'] == '营销渠道与方法':
        sec['prompt'] = '请为我撰写本项目的营销渠道与方法总论，概述线上、线下及经销商渠道的整体布局思路。字数不少于1000字。'
    if sec['id'] == 66 and sec['title'] == '风险分析':
        sec['prompt'] = '请为我撰写本项目的风险分析总论，系统概述项目面临的主要风险类型及整体风险管理框架。字数不少于1000字。'
    if sec['type'] == 'table':
        # table 类型的 prompt 保持不变，但后续生成时要求写 400-600 字说明
        pass

# 分 4 批
batch_size = 19
for i in range(4):
    batch = sections[i*batch_size:(i+1)*batch_size]
    with open(f'batch_long_{i+1}.json','w',encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
    print(f'Batch {i+1}: {len(batch)} sections')

print('Done')
