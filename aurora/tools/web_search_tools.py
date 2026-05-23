"""Web Search Tools for Real Market and Policy Data using DDG."""

import logging
from typing import Dict, List, Any
try:
    from ddgs import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False

from aurora.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)

def search_market_data(query: str, max_results: int = 3) -> str:
    """
    Search real-time web for market size, policies, or competitor info.
    Use this to get accurate CAGR, market caps, or regulatory guidelines.
    """
    if not HAS_DDGS:
        return "Search tool unavailable (requires ddgs). Use estimated plausible data."
        
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"Title: {r.get('title')}\nSource: {r.get('href')}\nSummary: {r.get('body')}")
                
        if not results:
            return "No results found."
            
        header = f"--- Real Web Search Results for '{query}' ---\n"
        return header + "\n\n".join(results)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return f"Search error: {str(e)}"

def _register_tools(registry: ToolRegistry):
    registry.register(
        name="search_market_data",
        description="Search real-time web for market size, policies, or competitor info. Requires internet.",
        func=search_market_data,
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Specific search query e.g. '2024 新能源汽车 市场规模 CAGR'"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results (1-5)"
                }
            },
            "required": ["query"]
        }
    )
