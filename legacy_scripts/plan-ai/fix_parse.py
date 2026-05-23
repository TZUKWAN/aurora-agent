#!/usr/bin/env python3
# -*- coding: utf-8 -*-
path = r'C:\Users\lauze\.claude\skills\business-plan-writer\scripts\parse_outline.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = lines[:63]
new_lines.append('    re.compile(\n')
new_lines.append('        r"^(其中|项\\s+目|货币资金|交易性金融|应收|预付|存货|流动资产|非流动资产|"\n')
new_lines.append('        r"资产总计|短期借款|应付|预收|应付职工|应交税费|流动负债|非流动负债|负债合计|"\n')
new_lines.append('        r"实收资本|资本公积|盈余公积|未分配利润|所有者权益|销售商品|收到.*现金|支付.*现金|"\n')
new_lines.append('        r"经营活动|投资活动|筹资活动|汇率变动|现金及现金等价物|期初|期末|营业收入|"\n')
new_lines.append('        r"营业成本|税金及附加|销售费用|管理费用|财务费用|资产减值|公允价值|投资收益|"\n')
new_lines.append('        r"营业利润|营业外收入|营业外支出|利润总额|所得税费用|净利润|每股收益|稀释每股收益)"\n')
new_lines.append('    ),\n')
new_lines.extend(lines[65:])

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('fixed')
