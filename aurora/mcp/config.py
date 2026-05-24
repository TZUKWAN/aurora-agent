"""MCP server configuration."""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class MCPServerConfig:
    """Configuration for the MCP server."""

    name: str = "aurora-agent"
    version: str = "1.0.0"
    protocol_version: str = "2024-11-05"
    enabled_tools: List[str] = field(default_factory=list)  # empty = all tools
    disabled_tools: List[str] = field(default_factory=list)


def load_mcp_config() -> MCPServerConfig:
    """Load MCP config from environment variables or defaults."""
    config = MCPServerConfig()
    disabled = os.environ.get("AURORA_MCP_DISABLED_TOOLS", "")
    if disabled:
        config.disabled_tools = [t.strip() for t in disabled.split(",") if t.strip()]
    return config
