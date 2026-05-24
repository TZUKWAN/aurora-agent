"""Parse natural language input into structured ProjectInfo."""

import json
import logging
import os

from aurora.models.project import ProjectInfo

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """Extract structured project information from the user's description.
Return a JSON object with these fields (leave empty if not mentioned):
- project_name: Project name
- technology: Core technology
- problem: Problem being solved
- solution: Proposed solution
- product: Product/service name
- target_market: Target audience/market
- business_model: Business model
- team_background: Team background
- innovation: Innovation points
- social_impact: Social impact
- funding: Funding needed
- team_size: Team size
- revenue_model: How it makes money
- market_size: Market size estimate
- stage: Project stage
- milestones: Key achievements
- intellectual_property: Patents/IP

User description:
{user_input}

Return ONLY the JSON object, no other text."""


def parse_project_input(user_input: str, config=None) -> ProjectInfo:
    """Extract structured ProjectInfo from natural language input.

    Tries LLM extraction first, falls back to simple keyword extraction.
    """
    # Try LLM-based extraction
    info = _llm_extract(user_input, config)
    if info:
        return info

    # Fallback: simple keyword extraction
    return _keyword_extract(user_input)


def _llm_extract(user_input: str, config=None) -> ProjectInfo | None:
    """Use LLM to extract project info from text."""
    try:
        if config is None:
            from aurora.config import load_config
            config = load_config()

        api_key = config.model.api_key or os.environ.get("AURORA_API_KEY")
        base_url = config.model.base_url or os.environ.get("AURORA_BASE_URL")
        if not api_key:
            return None

        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)
        model_name = config.model.name or os.environ.get("AURORA_MODEL", "glm-4.7-flash")

        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You extract structured data. Return only valid JSON."},
                {"role": "user", "content": EXTRACTION_PROMPT.format(user_input=user_input)},
            ],
            temperature=0.3,
            max_tokens=1024,
        )

        content = resp.choices[0].message.content or ""
        if not content.strip():
            rc = getattr(resp.choices[0].message, 'reasoning_content', None)
            if rc and rc.strip():
                content = rc

        # Strip markdown code blocks if present
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        data = json.loads(content)
        return ProjectInfo.from_dict(data)

    except Exception as e:
        logger.debug(f"LLM extraction failed: {e}")
        return None


def _keyword_extract(user_input: str) -> ProjectInfo:
    """Simple keyword-based extraction as fallback."""
    info = ProjectInfo()
    text = user_input.lower()

    # Best-effort extraction from common patterns
    if "ai" in text or "人工智能" in text:
        info.technology = "AI/人工智能"
    if "教育" in text or "education" in text:
        info.target_market = "教育"
    if "k-12" in text or "k12" in text:
        info.target_market = "K-12学生"
    if "大模型" in text or "llm" in text:
        info.technology = "大语言模型"

    return info
