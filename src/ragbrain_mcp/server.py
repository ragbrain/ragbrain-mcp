#!/usr/bin/env python3
"""RAGBrain MCP Server.

This module provides the main entry point for the RAGBrain MCP server,
which exposes RAGBrain knowledge base functionality to Claude Desktop.

Tools available:
    - ragbrain_list_namespaces: List all namespaces with document counts
    - ragbrain_search: Semantic search in the knowledge base
    - ragbrain_browse_namespace: List documents in a namespace
    - ragbrain_get_document: Get full document content

Usage:
    # As a command-line tool (after pip install)
    ragbrain-mcp

    # Or run directly
    python -m ragbrain_mcp.server

Environment Variables:
    RAGBRAIN_URL: URL of the RAGBrain API (default: http://localhost:8000)
    RAGBRAIN_TIMEOUT: Request timeout in seconds (default: 60)
    RAGBRAIN_LOG_LEVEL: Logging level (default: INFO)
"""

import asyncio
import logging
import sys

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

from .client import RAGBrainClient
from .config import Settings, get_settings
from .tools import ToolHandler, get_tool_definitions

# Module-level logger
logger = logging.getLogger("ragbrain-mcp")


def configure_logging(level: str) -> None:
    """Configure logging for the MCP server.

    Args:
        level: Logging level string (DEBUG, INFO, WARNING, ERROR).
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


def create_server(settings: Settings) -> tuple[Server, RAGBrainClient, ToolHandler]:
    """Create and configure the MCP server.

    Args:
        settings: Server configuration settings.

    Returns:
        Tuple of (server, client, tool_handler).
    """
    server = Server("ragbrain")
    client = RAGBrainClient(settings)
    tool_handler = ToolHandler(client, settings)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """Return available MCP tools."""
        return get_tool_definitions()

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list:
        """Handle tool calls from MCP client."""
        return await tool_handler.handle(name, arguments)

    return server, client, tool_handler


async def check_health(client: RAGBrainClient, url: str) -> None:
    """Check RAGBrain API health on startup.

    Args:
        client: RAGBrain API client.
        url: URL being checked (for logging).
    """
    try:
        health = client.health_check()
        status = health.get("status", "unknown")
        logger.info(f"RAGBrain health check: {status}")
    except Exception as e:
        logger.warning(f"Could not connect to RAGBrain at {url}: {e}")
        logger.warning("Server will start but tools may fail until RAGBrain is available")


async def run_server() -> None:
    """Run the MCP server with stdio transport."""
    settings = get_settings()
    configure_logging(settings.log_level)

    logger.info(f"Starting RAGBrain MCP server (connecting to {settings.url})")

    server, client, _ = create_server(settings)

    # Check health on startup
    await check_health(client, settings.url)

    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
    finally:
        client.close()


def main() -> None:
    """Main entry point for the ragbrain-mcp command."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
