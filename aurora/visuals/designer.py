"""Visual Designer Agent for generating dynamic HTML/CSS components."""

import json
import logging
from typing import Dict, Optional
import os

from aurora.config import load_config
from aurora.agent import AuroraAgent

logger = logging.getLogger(__name__)

class VisualDesigner:
    """Agent that generates distinct HTML designs for plan sections."""

    DESIGNER_PROMPT = """你是一个顶级的全栈视觉工程师与商业图表专家。
你的任务是为极简或极具科技感的商业计划书，直接编写一个超级美观、自成一格的单文件完整 HTML(包含内联 CSS 和必要的纯净 JS)。这会被无头浏览器直接渲染截图并插入到最终的 Word 中。

核心铁律：
1. 【绝对不要模板化】每一次颜色、布局、字体、边框圆角、阴影都必须随机且独特（比如有时候深色科技风，有时候拟态化Apple风，有时候极简报纸风）。
2. 【输出纯净代码】仅输出一段由 ```html 包裹的代码，不要有任何多余的 Markdown 解释、寒暄或前言后语。
3. 【自包含、直接可运行】所有需要的库必须用可靠的 CDN 引入（如 ECharts, Tailwind 等，但直接手写好看的原生 CSS更好，更稳定）。
4. 【高对比度与留白】这是要截图插入 Word 的，所以字号必须大、边距必须足，图表数据要有视觉冲击力。背景色需与设计搭配（深色图搭配白字，浅色图搭配深灰色字）。

根据我给你的【所属章节】与【项目信息】，决定你要画什么：
- 如果是【product_service】(产品与服务)：请用 CSS 捏一个极其漂亮的假想产品 UI（或手机端框截，或大屏数据面板，或实物图的 CSS 抽象）。
- 如果是【business_model】(商业模式)：请运用有连接线的架构图、流程结构图，或者复杂的 CSS Grid 排列价值主张与收入机制环节。
- 如果是【financial_analysis】(财务分析) / 【market_analysis】(市场分析)：务必内嵌 ECharts(https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js) 绘制震撼的折线图、柱状图或饼图，图表要加上深邃的标题、网格线和漂亮的渐变色区域。

项目信息：
{project_info}

当前绘制区块所属章节：{section_id}
"""

    def __init__(self, agent_runner=None):
        """Initialize with either an existing agent or create a fresh caller."""
        self.config = load_config()
        self.agent_runner = agent_runner
        
        # If no external runner provided, we instantiate a very lightweight OpenAI/LiteLLM client
        if not self.agent_runner:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.config.llm.api_key,
                    base_url=self.config.llm.base_url
                )
            except Exception as e:
                logger.error(f"Failed to init OpenAI client for designer: {e}")
                self.client = None

    def generate_html(self, project_info: Dict, section_id: str) -> Optional[str]:
        """Generate HTML string for a specific section."""
        if not self.client:
            return None
            
        prompt = self.DESIGNER_PROMPT.format(
            project_info=json.dumps(project_info, ensure_ascii=False, indent=2),
            section_id=section_id
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.llm.model_name,
                messages=[
                    {"role": "system", "content": "You are a world-class HTML/CSS/UI generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7 # Bring some creativity for unique designs
            )
            
            content = response.choices[0].message.content
            
            # Extract HTML block if enclosed in markdown
            if "```html" in content:
                content = content.split("```html")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
                
            return content
        except Exception as e:
            logger.error(f"Failed to generate HTML design: {e}")
            return None
