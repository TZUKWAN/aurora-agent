"""Visual Designer Agent for generating dynamic HTML/CSS components."""

import json
import logging
import os
from typing import Dict, Optional

from aurora.config import load_config

logger = logging.getLogger(__name__)

class VisualDesigner:
    """Agent that generates distinct HTML designs for plan sections."""

    DESIGNER_PROMPT = """你是一个顶级的全栈视觉工程师与商业图表专家。
你的任务是为极简或极具科技感的商业计划书，直接编写一个超级美观、自成一格的单文件完整 HTML(包含内联 CSS 和必要的纯净 JS)。这会被无头浏览器直接渲染截图并插入到最终的 Word 中。

核心铁律：
1. 【绝对不要模板化】每一次颜色、布局、字体、边框圆角、阴影都必须随机且独特。
2. 【输出纯净代码】仅输出一段由 ```html 包裹的代码，不要有任何多余的 Markdown 解释。
3. 【自包含】所需库用CDN引入，或者纯用CSS写布局。
4. 【高对比度与留白】这是要截图的，字号必须大、边距必须足。

项目信息：
{project_info}

当前绘制区块所属章节：{section_id}
"""

    def __init__(self, agent_runner=None):
        self.config = load_config()
        self.agent_runner = agent_runner
        
        if not self.agent_runner:
            try:
                from openai import OpenAI
                # 修复: config.model (而不是 config.llm)
                self.client = OpenAI(
                    api_key=self.config.model.api_key or os.environ.get("AURORA_API_KEY"),
                    base_url=self.config.model.base_url or os.environ.get("AURORA_BASE_URL")
                )
                self.model_name = self.config.model.name or os.environ.get("AURORA_MODEL", "glm-4.7-flash")
            except Exception as e:
                logger.error(f"Failed to init OpenAI client for designer: {e}")
                self.client = None

    def generate_html(self, project_info: Dict, section_id: str) -> Optional[str]:
        if not self.client:
            return None
            
        prompt = self.DESIGNER_PROMPT.format(
            project_info=json.dumps(project_info, ensure_ascii=False, indent=2),
            section_id=section_id
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a world-class HTML/CSS/UI generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content or ""
            if not content.strip():
                rc = getattr(response.choices[0].message, 'reasoning_content', None)
                if rc and rc.strip():
                    content = rc
            
            if "```html" in content:
                content = content.split("```html")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
                
            return content
        except Exception as e:
            logger.error(f"Failed to generate HTML design: {e}")
            return None
