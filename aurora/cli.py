"""CLI interface for AuroraAgent."""

import asyncio
import logging
from argparse import ArgumentParser

from aurora.agent import AuroraAgent
from aurora.config import load_config


async def chat():
    """Run interactive chat mode."""
    config = load_config()
    agent = AuroraAgent(config)
    
    print("=" * 60)
    print("          AuroraAgent - 大学生创新创业竞赛AI助手")
    print("=" * 60)
    print("欢迎使用 AuroraAgent！我可以帮助您：")
    print("  - 查询竞赛信息")
    print("  - 智能匹配参赛赛道")
    print("  - 生成商业计划书")
    print("  - 模拟评审评估")
    print("  - 生成路演PPT和脚本")
    print("  - 模拟答辩练习")
    print("\n输入 'quit' 或 'exit' 退出")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n您：")
            
            if user_input.lower() in ["quit", "exit", "退出"]:
                print("感谢使用 AuroraAgent！祝您竞赛顺利！")
                break
            
            if not user_input.strip():
                continue
            
            print("AuroraAgent：思考中...")
            response = await agent.run(user_input)
            print(f"\nAuroraAgent：{response}")
            
        except KeyboardInterrupt:
            print("\n感谢使用 AuroraAgent！")
            break
        except Exception as e:
            print(f"发生错误：{e}")


def main():
    """Main entry point."""
    parser = ArgumentParser(prog="aurora", description="AuroraAgent CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    subparsers.add_parser("chat", help="Start interactive chat")
    
    args = parser.parse_args()
    
    if args.command == "chat":
        asyncio.run(chat())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
