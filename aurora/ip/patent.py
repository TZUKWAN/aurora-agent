"""专利申请辅助."""

from typing import Dict, List


class PatentAssistant:
    """专利申请辅助工具."""

    def generate_tech_disclosure(self, invention_info: Dict) -> str:
        name = invention_info.get("invention_name", "发明名称")
        field = invention_info.get("technical_field", "技术领域")
        background = invention_info.get("background", "现有技术存在的问题")
        solution = invention_info.get("solution", "本发明的解决方案")
        effects = invention_info.get("effects", "有益效果")

        return f"""# 技术交底书

## 发明名称
{name}

## 技术领域
{field}

## 背景技术
{background}

## 发明内容
{solution}

## 有益效果
{effects}

## 具体实施方式
[请补充具体实施例]
"""

    def generate_claims_draft(self, invention_info: Dict) -> List[str]:
        return [
            f"1. 一种{invention_info.get('invention_name', '方法/装置')}，其特征在于...",
            "2. 根据权利要求1所述的方法，其特征在于...",
            "3. 根据权利要求1或2所述的方法，其特征在于...",
        ]

    def check_patentability(self, invention_info: Dict) -> Dict:
        return {
            "novelty": "建议进行专利检索确认",
            "inventiveness": "需评估与现有技术的区别",
            "practicality": "具备工业实用性",
            "recommendation": "建议申请发明专利",
        }
