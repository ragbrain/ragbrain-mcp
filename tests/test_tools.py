"""Tests for MCP tool definitions and handlers."""

import pytest
import respx
from httpx import Response

from ragbrain_mcp.tools import (
    TOOL_BROWSE_NAMESPACE,
    TOOL_DISCOVER_DOCUMENTS,
    TOOL_GET_DOCUMENT,
    TOOL_LIST_NAMESPACES,
    TOOL_SEARCH,
    ToolHandler,
    get_tool_definitions,
)
from ragbrain_mcp.client import RAGBrainClient
from ragbrain_mcp.config import Settings


class TestToolDefinitions:
    """Tests for tool definitions."""

    def test_get_tool_definitions_count(self) -> None:
        """Test that all tools are defined."""
        tools = get_tool_definitions()
        assert len(tools) == 5

    def test_tool_names(self) -> None:
        """Test tool names are correct."""
        tools = get_tool_definitions()
        names = {t.name for t in tools}
        assert names == {
            TOOL_LIST_NAMESPACES,
            TOOL_SEARCH,
            TOOL_BROWSE_NAMESPACE,
            TOOL_GET_DOCUMENT,
            TOOL_DISCOVER_DOCUMENTS,
        }

    def test_all_tools_have_descriptions(self) -> None:
        """Test all tools have descriptions."""
        tools = get_tool_definitions()
        for tool in tools:
            assert tool.description
            assert len(tool.description) > 20

    def test_all_tools_have_schemas(self) -> None:
        """Test all tools have input schemas."""
        tools = get_tool_definitions()
        for tool in tools:
            assert tool.inputSchema
            assert tool.inputSchema["type"] == "object"
            assert "properties" in tool.inputSchema

    def test_search_tool_schema(self) -> None:
        """Test search tool has correct schema."""
        tools = get_tool_definitions()
        search_tool = next(t for t in tools if t.name == TOOL_SEARCH)
        schema = search_tool.inputSchema
        assert "query" in schema["properties"]
        assert schema["required"] == ["query"]
        assert schema["properties"]["query"]["minLength"] == 1
        assert schema["properties"]["top_k"]["maximum"] == 20


@pytest.fixture
def mock_settings() -> Settings:
    """Create settings for mocked testing."""
    return Settings(url="http://test-api:8000", timeout=5.0)


@pytest.fixture
def mock_handler(mock_settings: Settings) -> ToolHandler:
    """Create a tool handler with mocked client."""
    client = RAGBrainClient(mock_settings)
    return ToolHandler(client, mock_settings)


class TestToolHandler:
    """Tests for ToolHandler class."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_list_namespaces(
        self, mock_handler: ToolHandler, sample_namespaces: dict
    ) -> None:
        """Test list_namespaces tool."""
        respx.get("http://test-api:8000/api/namespaces").mock(
            return_value=Response(200, json=sample_namespaces)
        )

        result = await mock_handler.handle(TOOL_LIST_NAMESPACES, {})
        assert len(result) == 1
        assert "Personal" in result[0].text
        assert "Work" in result[0].text

    @respx.mock
    @pytest.mark.asyncio
    async def test_list_namespaces_tree_view(
        self, mock_handler: ToolHandler, sample_namespace_tree: dict
    ) -> None:
        """Test list_namespaces with tree view."""
        respx.get("http://test-api:8000/api/namespaces/tree").mock(
            return_value=Response(200, json=sample_namespace_tree)
        )

        result = await mock_handler.handle(TOOL_LIST_NAMESPACES, {"tree_view": True})
        assert "Namespace Tree" in result[0].text

    @respx.mock
    @pytest.mark.asyncio
    async def test_search(
        self, mock_handler: ToolHandler, sample_search_results: dict
    ) -> None:
        """Test search tool."""
        respx.post("http://test-api:8000/api/query").mock(
            return_value=Response(200, json=sample_search_results)
        )

        result = await mock_handler.handle(TOOL_SEARCH, {"query": "machine learning"})
        assert len(result) == 1
        assert "Search Results" in result[0].text
        assert "ml-notes.md" in result[0].text

    @pytest.mark.asyncio
    async def test_search_missing_query(self, mock_handler: ToolHandler) -> None:
        """Test search tool with missing query."""
        result = await mock_handler.handle(TOOL_SEARCH, {})
        assert "Error" in result[0].text
        assert "query" in result[0].text

    @pytest.mark.asyncio
    async def test_search_empty_query(self, mock_handler: ToolHandler) -> None:
        """Test search tool with empty query."""
        result = await mock_handler.handle(TOOL_SEARCH, {"query": "  "})
        assert "Error" in result[0].text

    @respx.mock
    @pytest.mark.asyncio
    async def test_browse_namespace(
        self, mock_handler: ToolHandler, sample_documents: dict
    ) -> None:
        """Test browse_namespace tool."""
        respx.get("http://test-api:8000/api/documents").mock(
            return_value=Response(200, json=sample_documents)
        )

        result = await mock_handler.handle(
            TOOL_BROWSE_NAMESPACE, {"namespace": "personal"}
        )
        assert "Documents in" in result[0].text
        assert "notes.md" in result[0].text

    @pytest.mark.asyncio
    async def test_browse_namespace_missing(self, mock_handler: ToolHandler) -> None:
        """Test browse_namespace with missing namespace."""
        result = await mock_handler.handle(TOOL_BROWSE_NAMESPACE, {})
        assert "Error" in result[0].text
        assert "namespace" in result[0].text

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_document(
        self, mock_handler: ToolHandler, sample_document: dict
    ) -> None:
        """Test get_document tool."""
        respx.get("http://test-api:8000/api/documents/id/abc-123").mock(
            return_value=Response(200, json=sample_document)
        )

        result = await mock_handler.handle(TOOL_GET_DOCUMENT, {"doc_id": "abc-123"})
        assert "notes.md" in result[0].text
        assert "My Notes" in result[0].text

    @pytest.mark.asyncio
    async def test_get_document_missing_id(self, mock_handler: ToolHandler) -> None:
        """Test get_document with missing doc_id."""
        result = await mock_handler.handle(TOOL_GET_DOCUMENT, {})
        assert "Error" in result[0].text
        assert "doc_id" in result[0].text

    @pytest.mark.asyncio
    async def test_unknown_tool(self, mock_handler: ToolHandler) -> None:
        """Test handling of unknown tool."""
        result = await mock_handler.handle("unknown_tool", {})
        assert "Error" in result[0].text
        assert "Unknown tool" in result[0].text

    @respx.mock
    @pytest.mark.asyncio
    async def test_connection_error(self, mock_handler: ToolHandler) -> None:
        """Test connection error handling."""
        import httpx
        respx.get("http://test-api:8000/api/namespaces").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        result = await mock_handler.handle(TOOL_LIST_NAMESPACES, {})
        assert "Error" in result[0].text
        assert "Cannot connect" in result[0].text

    @respx.mock
    @pytest.mark.asyncio
    async def test_404_error(self, mock_handler: ToolHandler) -> None:
        """Test 404 error handling."""
        respx.get("http://test-api:8000/api/documents/id/missing").mock(
            return_value=Response(404, text="Document not found")
        )

        result = await mock_handler.handle(TOOL_GET_DOCUMENT, {"doc_id": "missing"})
        assert "Error" in result[0].text
        assert "Not found" in result[0].text

    @respx.mock
    @pytest.mark.asyncio
    async def test_timeout_error(self, mock_handler: ToolHandler) -> None:
        """Test timeout error handling."""
        import httpx
        respx.get("http://test-api:8000/api/namespaces").mock(
            side_effect=httpx.TimeoutException("Request timed out")
        )

        result = await mock_handler.handle(TOOL_LIST_NAMESPACES, {})
        assert "Error" in result[0].text
        assert "timed out" in result[0].text

    @pytest.mark.asyncio
    async def test_search_namespace_path_traversal(self, mock_handler: ToolHandler) -> None:
        """Test that path traversal in namespace is rejected."""
        result = await mock_handler.handle(TOOL_SEARCH, {"query": "test", "namespace": "../etc"})
        assert "Error" in result[0].text
        assert "Invalid namespace" in result[0].text

    @pytest.mark.asyncio
    async def test_search_namespace_absolute_path(self, mock_handler: ToolHandler) -> None:
        """Test that absolute path in namespace is rejected."""
        result = await mock_handler.handle(TOOL_SEARCH, {"query": "test", "namespace": "/etc/passwd"})
        assert "Error" in result[0].text
        assert "Invalid namespace" in result[0].text

    @pytest.mark.asyncio
    async def test_browse_namespace_path_traversal(self, mock_handler: ToolHandler) -> None:
        """Test that path traversal in browse namespace is rejected."""
        result = await mock_handler.handle(TOOL_BROWSE_NAMESPACE, {"namespace": "../secrets"})
        assert "Error" in result[0].text
        assert "Invalid namespace" in result[0].text

    @pytest.mark.asyncio
    async def test_browse_namespace_absolute_path(self, mock_handler: ToolHandler) -> None:
        """Test that absolute path in browse namespace is rejected."""
        result = await mock_handler.handle(TOOL_BROWSE_NAMESPACE, {"namespace": "/root"})
        assert "Error" in result[0].text
        assert "Invalid namespace" in result[0].text
