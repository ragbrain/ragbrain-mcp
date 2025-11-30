"""MCP tool definitions and handlers for RAGBrain.

This module defines the MCP tools exposed by the RAGBrain server and
contains the logic for handling tool calls.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any

import httpx
from mcp.types import TextContent, Tool

from .client import RAGBrainClient
from .config import Settings
from .formatters import (
    format_discover_results,
    format_document,
    format_document_list,
    format_namespace_list,
    format_namespace_tree,
    format_search_results,
)

logger = logging.getLogger("ragbrain-mcp")


# Tool name constants
TOOL_LIST_NAMESPACES = "ragbrain_list_namespaces"
TOOL_SEARCH = "ragbrain_search"
TOOL_BROWSE_NAMESPACE = "ragbrain_browse_namespace"
TOOL_GET_DOCUMENT = "ragbrain_get_document"
TOOL_DISCOVER_DOCUMENTS = "ragbrain_discover_documents"


@dataclass
class ToolError:
    """Represents an error that occurred during tool execution."""

    message: str

    def to_content(self) -> list[TextContent]:
        """Convert error to MCP TextContent."""
        return [TextContent(type="text", text=f"Error: {self.message}")]


def get_tool_definitions() -> list[Tool]:
    """Return the list of available MCP tools.

    Returns:
        List of Tool definitions for MCP.
    """
    return [
        Tool(
            name=TOOL_LIST_NAMESPACES,
            description=(
                "List all namespaces in the RAGBrain knowledge base. "
                "Returns namespace names, descriptions, document counts, and hierarchy. "
                "Use this to discover what knowledge areas are available."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "tree_view": {
                        "type": "boolean",
                        "description": (
                            "If true, returns namespaces as a hierarchical tree. "
                            "If false, returns flat list. Default: false"
                        ),
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name=TOOL_SEARCH,
            description=(
                "Perform semantic search across the RAGBrain knowledge base. "
                "Returns relevant text chunks that match the query. "
                "Use this to find information on any topic stored in RAGBrain."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query - can be a question or topic",
                        "minLength": 1,
                        "maxLength": 1000,
                    },
                    "namespace": {
                        "type": "string",
                        "description": (
                            "Optional: limit search to a specific namespace "
                            "(e.g., 'mba/finance'). Supports wildcards like 'mba/*'"
                        ),
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5, max: 20)",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name=TOOL_BROWSE_NAMESPACE,
            description=(
                "List all documents stored in a specific namespace. "
                "Returns document names, IDs, chunk counts, and creation dates. "
                "Use this to see what's in a particular knowledge area."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "The namespace to browse (e.g., 'personal', 'work/projects')",
                        "minLength": 1,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of documents to return (default: 50)",
                        "minimum": 1,
                        "maximum": 200,
                        "default": 50,
                    },
                },
                "required": ["namespace"],
            },
        ),
        Tool(
            name=TOOL_GET_DOCUMENT,
            description=(
                "Retrieve the full content of a specific document by its ID. "
                "Returns the complete reconstructed text from all chunks. "
                "Use this when you need to read an entire document."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "The document ID (UUID) to retrieve",
                        "minLength": 1,
                    }
                },
                "required": ["doc_id"],
            },
        ),
        Tool(
            name=TOOL_DISCOVER_DOCUMENTS,
            description=(
                "Discover documents by semantic search over their summaries. "
                "Use this to find documents about a topic BEFORE searching for specific content. "
                "Returns document titles, headings, and relevance scores. "
                "Example queries: 'documents about leadership', 'notes on valuation', "
                "'files covering conflict resolution'. "
                "After discovering relevant documents, use ragbrain_search to find specific content."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Semantic query to find documents by topic or content. "
                            "Can be a question, topic, or description of what you're looking for."
                        ),
                        "minLength": 1,
                        "maxLength": 500,
                    },
                    "namespace": {
                        "type": "string",
                        "description": (
                            "Optional: limit discovery to a specific namespace "
                            "(e.g., 'mba/finance'). Supports wildcards like 'mba/*'"
                        ),
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of documents to return (default: 10, max: 50)",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
    ]


class ToolHandler:
    """Handles execution of MCP tool calls.

    This class encapsulates the logic for processing tool calls,
    including input validation and error handling.
    """

    def __init__(self, client: RAGBrainClient, settings: Settings) -> None:
        """Initialize the tool handler.

        Args:
            client: RAGBrain API client.
            settings: Server settings.
        """
        self.client = client
        self.settings = settings

    async def handle(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle a tool call.

        Args:
            name: Name of the tool to execute.
            arguments: Tool arguments from MCP client.

        Returns:
            List of TextContent with the tool result.
        """
        logger.info(f"Tool called: {name} with args: {arguments}")

        try:
            if name == TOOL_LIST_NAMESPACES:
                return await self._handle_list_namespaces(arguments)
            elif name == TOOL_SEARCH:
                return await self._handle_search(arguments)
            elif name == TOOL_BROWSE_NAMESPACE:
                return await self._handle_browse_namespace(arguments)
            elif name == TOOL_GET_DOCUMENT:
                return await self._handle_get_document(arguments)
            elif name == TOOL_DISCOVER_DOCUMENTS:
                return await self._handle_discover_documents(arguments)
            else:
                return ToolError(f"Unknown tool: {name}").to_content()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {name}: {e}")
            if e.response.status_code == 404:
                return ToolError(f"Not found: {e.response.text}").to_content()
            return ToolError(
                f"API error ({e.response.status_code}): {e.response.text}"
            ).to_content()

        except httpx.ConnectError:
            logger.error(f"Connection error to {self.settings.url}")
            return ToolError(
                f"Cannot connect to RAGBrain at {self.settings.url}. Is it running?"
            ).to_content()

        except httpx.TimeoutException:
            logger.error(f"Timeout connecting to {self.settings.url}")
            return ToolError(
                "Request timed out. RAGBrain may be slow or unresponsive."
            ).to_content()

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return ToolError(
                "Invalid response from RAGBrain API"
            ).to_content()

        except Exception as e:
            logger.exception(f"Unexpected error calling tool {name}")
            # Don't expose internal error details to client
            return ToolError("An unexpected error occurred").to_content()

    async def _handle_list_namespaces(
        self, arguments: dict[str, Any]
    ) -> list[TextContent]:
        """Handle list_namespaces tool call."""
        tree_view = arguments.get("tree_view", False)

        if tree_view:
            result = self.client.get_namespace_tree(include_stats=True)
            output = format_namespace_tree(result.get("tree", []))
        else:
            result = self.client.list_namespaces(include_stats=True)
            output = format_namespace_list(result.get("namespaces", []))

        return [TextContent(type="text", text=output)]

    async def _handle_search(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle search tool call."""
        query = arguments.get("query", "").strip()
        if not query:
            return ToolError("'query' parameter is required").to_content()

        namespace = arguments.get("namespace")
        # Validate namespace to prevent path traversal
        if namespace and (".." in namespace or namespace.startswith("/")):
            return ToolError("Invalid namespace format").to_content()

        top_k = min(arguments.get("top_k", 5), self.settings.max_results)

        result = self.client.search(query, namespace, top_k)
        output = format_search_results(result)

        return [TextContent(type="text", text=output)]

    async def _handle_browse_namespace(
        self, arguments: dict[str, Any]
    ) -> list[TextContent]:
        """Handle browse_namespace tool call."""
        namespace = arguments.get("namespace", "").strip()
        if not namespace:
            return ToolError("'namespace' parameter is required").to_content()

        # Validate namespace to prevent path traversal
        if ".." in namespace or namespace.startswith("/"):
            return ToolError("Invalid namespace format").to_content()

        limit = min(arguments.get("limit", 50), 200)
        result = self.client.browse_namespace(namespace, limit)
        output = format_document_list(result)

        return [TextContent(type="text", text=output)]

    async def _handle_get_document(
        self, arguments: dict[str, Any]
    ) -> list[TextContent]:
        """Handle get_document tool call."""
        doc_id = arguments.get("doc_id", "").strip()
        if not doc_id:
            return ToolError("'doc_id' parameter is required").to_content()

        result = self.client.get_document(doc_id)
        output = format_document(result, self.settings.max_document_length)

        return [TextContent(type="text", text=output)]

    async def _handle_discover_documents(
        self, arguments: dict[str, Any]
    ) -> list[TextContent]:
        """Handle discover_documents tool call."""
        query = arguments.get("query", "").strip()
        if not query:
            return ToolError("'query' parameter is required").to_content()

        namespace = arguments.get("namespace")
        # Validate namespace to prevent path traversal
        if namespace and (".." in namespace or namespace.startswith("/")):
            return ToolError("Invalid namespace format").to_content()

        top_k = min(arguments.get("top_k", 10), 50)

        result = self.client.discover_documents(query, namespace, top_k)
        output = format_discover_results(result)

        return [TextContent(type="text", text=output)]
