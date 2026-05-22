import re

with open('charts.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace dark background colors with light ones
replacements = [
    ('rgba(255,255,255,0.08)', '#f0f0f0'),
    ('rgba(255,255,255,0.1)', '#f5f5f5'),
    ('rgba(255,255,255,0.06)', '#eeeeee'),
    ('rgba(255,255,255,0.05)', '#f0f0f0'),
    ('rgba(255,255,255,0.15)', '#e8e8e8'),
    ('rgba(255,255,255,0.2)', '#d0d0d0'),
    ('rgba(255,255,255,0.12)', '#e8e8e8'),
    ('rgba(255,255,255,0.25)', '#d5d5d5'),
    ('rgba(255,255,255,0.03)', '#fafafa'),
    ('rgba(255,255,255,0.5)', '#cccccc'),
    ('rgba(255,255,255,0.3)', '#e0e0e0'),
    ('rgba(255,255,255,0.7)', '#b0b0b0'),
    ('rgba(0,0,0,0.15)', '#e8e8e8'),
    ('rgba(0,0,0,0.2)', '#e0e0e0'),
    ('color:#fff;', 'color:#333;'),
    ('color:#fff">', 'color:#333">'),
    ('color:#e0e0e0', 'color:#333'),
    ('color:#f0f0f0', 'color:#333'),
    ('color:#dfe6e9', 'color:#333'),
    ('color:#ecf0f1', 'color:#333'),
    ('color:#b2bec3', 'color:#666'),
    ('color:#dcdde1', 'color:#333'),
]

for old, new in replacements:
    content = content.replace(old, new)

with open('charts.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Color replacements done')
