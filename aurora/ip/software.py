"""软件著作权辅助."""

from typing import Dict


class SoftwareCopyrightAssistant:
    """软件著作权申请辅助."""

    def generate_description(self, software_info: Dict) -> str:
        name = software_info.get("name", "软件名称")
        purpose = software_info.get("purpose", "软件用途")
        features = software_info.get("features", [])

        features_text = "\n".join(f"{i+1}. {f}" for i, f in enumerate(features))

        return f"""# 软件说明文档

## 软件名称
{name}

## 开发目的
{purpose}

## 主要功能
{features_text}

## 技术特点
- 采用模块化设计，易于维护和扩展
- 支持多平台运行
- 用户界面友好，操作简便

## 运行环境
- 操作系统：Windows/Linux/macOS
- 运行环境：Python 3.10+
"""

    def generate_source_code_sample(self, code: str, max_lines: int = 3000) -> str:
        lines = code.split("\n")
        if len(lines) > max_lines:
            # 取前1/3和后1/3
            head = lines[:max_lines // 3]
            tail = lines[-max_lines // 3:]
            return "\n".join(head) + "\n...\n" + "\n".join(tail)
        return code
