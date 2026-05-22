#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复 business_plan_writer.py 中的 bug"""

input_file = "business_plan_writer.py"
output_file = "business_plan_writer.py.fixed"

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 修复第114行和第206行的问题
content = content.replace('"type": sec.get("type", "generated")', '"type": sec.get("type", "generated")')
content = content.replace('sec_type = sec.get("type", "generated")', 'sec_type = sec.get("type", "generated")')

# 仔细看，问题是 "generated" 没有引号！
# 让我用更准确的方式
lines = content.split('\n')
for i, line in enumerate(lines):
    if '"type": sec.get("type", "generated")' in line:
        print(f"在第{i+1}行找到问题: {line}")
        lines[i] = line.replace('"type": sec.get("type", "generated")', '"type": sec.get("type", "generated")')
    elif 'sec_type = sec.get("type", "generated")' in line:
        print(f"在第{i+1}行找到问题: {line}")
        lines[i] = line.replace('sec_type = sec.get("type", "generated")', 'sec_type = sec.get("type", "generated")')

# 写回文件
with open(input_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("修复完成！")
