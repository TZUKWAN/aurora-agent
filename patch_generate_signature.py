import os
filepath = "D:/SophiaAgentWork/aurora-agent/aurora/business_plan/generator.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'def generate(self, project_info: Dict, competition_id: str = "internet_plus") -> Dict:',
    'def generate(self, project_info: Dict, competition_id: str = "internet_plus", session_id: str = None) -> Dict:'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
