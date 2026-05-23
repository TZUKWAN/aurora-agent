import os
import sys

# 注入你给的 Zhipu API 环境配置
os.environ["AURORA_API_KEY"] = "a683b3076098052127efb398131f91a6.P0ra5oXeAo0U8ZVZ"
os.environ["AURORA_BASE_URL"] = "https://open.bigmodel.cn/api/paas/v4/"
os.environ["AURORA_MODEL"] = "glm-4.7-flash"
# 如果有些代码是通过 OPENAI_ 前缀读的，也同时塞一份做兼容确保一次性过
os.environ["OPENAI_API_KEY"] = os.environ["AURORA_API_KEY"]
os.environ["OPENAI_BASE_URL"] = os.environ["AURORA_BASE_URL"]

sys.path.insert(0, "/d/SophiaAgentWork/aurora-agent")

from aurora.business_plan.generator import BusinessPlanGenerator

project_info = {
    "name": "Aurora极光云评测",
    "technology": "基于大语言模型多智能体架构与无头浏览器的前端智能生成引擎",
    "problem": "大学生创新创业大赛中，技术型团队缺乏将硬核技术转化为高维商业逻辑排版文档与漂亮UI数据图表的能力，频遭评委打压。",
    "solution": "提供一站式AI教头系统，内置真实财务推演物理沙盘与动态HTML图文混排视觉模块，输入想法秒出带高清插图的金奖计划书。",
    "target_market": "每年上千万参加互联网+、挑战杯及三创赛的高校创新团队、双创学院",
    "stage": "MVP系统已闭环验证，核心代码完成架构集成",
    "team_background": "全栈极客开发团队，具备深厚的大模型 Agent 编排经验与复杂的网络环境穿透攻坚能力",
    "funding": "200万人民币",
    "track": "青年红色筑梦之旅赛道"
}

print("====== 正在激活 AuroraAgent 核心管道 ======")
print("正在使用模型: glm-4.7-flash")

try:
    bpg = BusinessPlanGenerator()
    
    # 开始走生成逻辑 (包括会调用刚才我写的 FinancialEngine和 VisualDesigner)
    plan = bpg.generate(project_info, competition_id="internet_plus", session_id="zhipu_sample_001")
    
    output_file = "Sample_Aurora_BusinessPlan.docx"
    print("\n正在启动 DOCX 混排引擎与无头浏览器出图模块，请稍候(这会消耗大模型API)...")
    res = bpg.export_to_docx(plan, output_file)
    
    if res.get("success"):
        print(f"\nSUCCESS: 成功！计划书大纲及图表截图已装配完成，文件落地: {output_file}")
    else:
        print(f"\nERROR: 生成出错了: {res}")

except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"\nERROR: 系统启动失败: {str(e)}")
