"""
测试脚本：验证 market 和 visualization 模块
"""
import sys
import os

sys.path.insert(0, r"D:\aurora-agent-temp\aurora-agent")

output_dir = r"D:\aurora-agent-temp\aurora-agent\test_output"
os.makedirs(output_dir, exist_ok=True)

print("=" * 60)
print("测试 1: CompetitorAnalyzer")
print("=" * 60)

from aurora.market.competitor import CompetitorAnalyzer

analyzer = CompetitorAnalyzer(
    self_info={
        "name": "极光智能",
        "description": "AI驱动的商业分析平台",
        "target_users": "中小企业",
        "features": {
            "AI分析": True,
            "数据可视化": True,
            "报告生成": True,
            "竞品监控": True,
            "多语言": False,
            "API接口": True,
        },
        "pricing": {"基础版": 99, "专业版": 299, "企业版": 999},
        "brand_score": 75,
        "user_satisfaction": 82,
        "market_share": 15,
    }
)

analyzer.add_competitor(
    "竞品A",
    {
        "description": "老牌数据分析公司",
        "features": {"AI分析": True, "数据可视化": True, "报告生成": True, "竞品监控": False, "多语言": True, "API接口": True},
        "pricing": {"基础版": 199, "专业版": 499, "企业版": 1499},
        "brand_score": 90,
        "user_satisfaction": 78,
        "market_share": 35,
        "target_users": "大型企业",
    },
)
analyzer.add_competitor(
    "竞品B",
    {
        "description": "新兴AI创业公司",
        "features": {"AI分析": True, "数据可视化": False, "报告生成": True, "竞品监控": True, "多语言": False, "API接口": False},
        "pricing": {"基础版": 49, "专业版": 149, "企业版": 499},
        "brand_score": 60,
        "user_satisfaction": 85,
        "market_share": 10,
        "target_users": "个人开发者",
    },
)

features = ["AI分析", "数据可视化", "报告生成", "竞品监控", "多语言", "API接口"]
fc = analyzer.compare_features(features)
print("功能对比矩阵:", fc["summary"])

pc = analyzer.compare_pricing()
print("价格对比统计:", pc["summary"])

diff = analyzer.differentiation_analysis()
print("差异化分析 - 独有优势:", diff["unique_strengths"])
print("差异化分析 - 差距:", diff["gaps"])
print("差异化评分:", diff["differentiation_score"])

report = analyzer.generate_report()
print("报告长度:", len(report), "字符")

excel_path = os.path.join(output_dir, "competitor_matrix.xlsx")
analyzer.export_matrix_excel(excel_path)
print(f"Excel已导出: {excel_path}")

map_path = os.path.join(output_dir, "positioning_map.png")
analyzer.plot_positioning_map("brand_score", "user_satisfaction", map_path, "品牌评分", "用户满意度")
print(f"定位图已导出: {map_path}")

print("\n" + "=" * 60)
print("测试 2: SWOTAnalyzer")
print("=" * 60)

from aurora.market.swot import SWOTAnalyzer

swot = SWOTAnalyzer(project_info={"name": "极光智能", "industry": "SaaS/AI"})

swot.set_factors(
    strengths=[
        {"text": "AI算法领先", "weight": 8, "importance": 9},
        {"text": "价格优势明显", "weight": 7, "importance": 8},
        {"text": "用户体验优秀", "weight": 6, "importance": 7},
        "团队技术背景强",
    ],
    weaknesses=[
        {"text": "品牌知名度低", "weight": 8, "importance": 8},
        {"text": "资金有限", "weight": 7, "importance": 7},
        "销售渠道不完善",
    ],
    opportunities=[
        {"text": "AI市场快速增长", "weight": 9, "importance": 9},
        {"text": "政策支持力度大", "weight": 6, "importance": 6},
        "中小企业数字化需求旺盛",
    ],
    threats=[
        {"text": "巨头入场竞争", "weight": 8, "importance": 9},
        {"text": "技术迭代快", "weight": 7, "importance": 7},
        "数据安全法规趋严",
    ],
)

analysis = swot.analyze()
print("SWOT分析 - 总因素数:", analysis["summary"]["total_factors"])
print("SWOT分析 - 定位:", analysis["summary"]["overall_position"])

tows = swot.generate_tows()
print("TOWS策略 - SO策略数:", len(tows["SO"]))
print("TOWS策略 - WO策略数:", len(tows["WO"]))

scores = swot.calculate_weighted_score()
print("加权评分:", scores["scores"])
print("IE矩阵:", scores["internal_external_matrix"]["quadrant"])

swot_path = os.path.join(output_dir, "swot_matrix.png")
swot.plot_swot_matrix(swot_path)
print(f"SWOT矩阵图已导出: {swot_path}")

tows_path = os.path.join(output_dir, "tows_matrix.png")
swot.plot_tows_matrix(tows_path)
print(f"TOWS矩阵图已导出: {tows_path}")

print("\n" + "=" * 60)
print("测试 3: ChartEngine")
print("=" * 60)

from aurora.visualization.charts import ChartEngine

engine = ChartEngine(theme="morandi")

# 柱状图
bar_path = os.path.join(output_dir, "bar_chart.png")
engine.bar_chart({"Q1": 120, "Q2": 180, "Q3": 150, "Q4": 220}, "季度销售额", bar_path, ylabel="万元")
print(f"柱状图已导出: {bar_path}")

# 折线图
line_path = os.path.join(output_dir, "line_chart.png")
engine.line_chart(
    {"2022年": [100, 120, 140, 160], "2023年": [130, 150, 180, 210], "2024年": [160, 190, 220, 250]},
    "年度趋势对比",
    line_path,
    xlabel="季度",
    x_ticks=["Q1", "Q2", "Q3", "Q4"],
)
print(f"折线图已导出: {line_path}")

# 饼图
pie_path = os.path.join(output_dir, "pie_chart.png")
engine.pie_chart({"产品A": 35, "产品B": 25, "产品C": 20, "产品D": 20}, "产品销售占比", pie_path, donut=True)
print(f"饼图已导出: {pie_path}")

# 雷达图
radar_path = os.path.join(output_dir, "radar_chart.png")
engine.radar_chart(
    {"自身产品": [85, 70, 90, 75, 80], "竞品平均": [70, 85, 65, 80, 75]},
    "能力对比雷达图",
    radar_path,
    categories=["技术", "价格", "服务", "品牌", "渠道"],
)
print(f"雷达图已导出: {radar_path}")

# 漏斗图
funnel_path = os.path.join(output_dir, "funnel_chart.png")
engine.funnel_chart({"访问": 10000, "注册": 5000, "激活": 3000, "付费": 1500, "复购": 800}, "用户转化漏斗", funnel_path)
print(f"漏斗图已导出: {funnel_path}")

# 甘特图
gantt_path = os.path.join(output_dir, "gantt_chart.png")
engine.gantt_chart(
    [
        {"name": "需求分析", "start": "2024-01-01", "end": "2024-01-15", "progress": 100},
        {"name": "产品设计", "start": "2024-01-10", "end": "2024-02-05", "progress": 80},
        {"name": "开发实现", "start": "2024-02-01", "end": "2024-03-20", "progress": 50},
        {"name": "测试验收", "start": "2024-03-15", "end": "2024-04-10", "progress": 20},
        {"name": "上线发布", "start": "2024-04-05", "end": "2024-04-20", "progress": 0},
    ],
    "项目进度甘特图",
    gantt_path,
)
print(f"甘特图已导出: {gantt_path}")

# 热力图
heatmap_path = os.path.join(output_dir, "heatmap.png")
engine.heatmap(
    [[85, 72, 90], [68, 88, 75], [92, 65, 80], [78, 82, 95]],
    {"x": ["技术", "市场", "运营"], "y": ["Q1", "Q2", "Q3", "Q4"]},
    heatmap_path,
    title="季度部门绩效热力图",
)
print(f"热力图已导出: {heatmap_path}")

# 测试商务主题
engine.set_theme("business")
business_path = os.path.join(output_dir, "business_bar.png")
engine.bar_chart({"A": 45, "B": 78, "C": 62, "D": 91}, "商务主题柱状图", business_path)
print(f"商务主题柱状图已导出: {business_path}")

print("\n" + "=" * 60)
print("所有测试通过！")
print(f"输出文件目录: {output_dir}")
print("=" * 60)
