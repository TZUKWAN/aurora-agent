"""Entry point for AuroraAgent CLI."""

import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        _run_mcp_server()
    else:
        from aurora.cli import main as cli_main
        cli_main()


def _run_mcp_server():
    """Run the MCP server via stdio."""
    from aurora.mcp_server import create_mcp_server
    server = create_mcp_server()
    server.run()


if __name__ == "__main__":
    main()
