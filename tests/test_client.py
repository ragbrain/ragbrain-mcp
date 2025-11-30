"""Tests for RAGBrain API client."""

import pytest
import respx
from httpx import Response

from ragbrain_mcp.client import RAGBrainClient
from ragbrain_mcp.config import Settings


@pytest.fixture
def mock_client() -> RAGBrainClient:
    """Create a client for testing with mocked HTTP."""
    settings = Settings(url="http://test-api:8000", timeout=5.0)
    return RAGBrainClient(settings)


class TestRAGBrainClient:
    """Tests for RAGBrainClient class."""

    def test_init(self, settings: Settings) -> None:
        """Test client initialization."""
        client = RAGBrainClient(settings)
        assert client.base_url == "http://localhost:8000"
        assert client.timeout == 10.0

    def test_lazy_client_initialization(self, settings: Settings) -> None:
        """Test that HTTP client is lazily initialized."""
        client = RAGBrainClient(settings)
        assert client._client is None
        _ = client.client  # Access the property
        assert client._client is not None

    def test_close(self, settings: Settings) -> None:
        """Test client close method."""
        client = RAGBrainClient(settings)
        _ = client.client  # Initialize the client
        client.close()
        assert client._client is None

    @respx.mock
    def test_health_check(self, mock_client: RAGBrainClient) -> None:
        """Test health check request."""
        respx.get("http://test-api:8000/health").mock(
            return_value=Response(200, json={"status": "healthy"})
        )

        result = mock_client.health_check()
        assert result["status"] == "healthy"

    @respx.mock
    def test_list_namespaces(
        self, mock_client: RAGBrainClient, sample_namespaces: dict
    ) -> None:
        """Test list namespaces request."""
        respx.get("http://test-api:8000/api/namespaces").mock(
            return_value=Response(200, json=sample_namespaces)
        )

        result = mock_client.list_namespaces()
        assert "namespaces" in result
        assert len(result["namespaces"]) == 2

    @respx.mock
    def test_get_namespace_tree(
        self, mock_client: RAGBrainClient, sample_namespace_tree: dict
    ) -> None:
        """Test get namespace tree request."""
        respx.get("http://test-api:8000/api/namespaces/tree").mock(
            return_value=Response(200, json=sample_namespace_tree)
        )

        result = mock_client.get_namespace_tree()
        assert "tree" in result

    @respx.mock
    def test_browse_namespace(
        self, mock_client: RAGBrainClient, sample_documents: dict
    ) -> None:
        """Test browse namespace request."""
        respx.get("http://test-api:8000/api/documents").mock(
            return_value=Response(200, json=sample_documents)
        )

        result = mock_client.browse_namespace("personal", limit=50)
        assert result["namespace"] == "personal"
        assert len(result["documents"]) == 2

    @respx.mock
    def test_search(
        self, mock_client: RAGBrainClient, sample_search_results: dict
    ) -> None:
        """Test search request."""
        respx.post("http://test-api:8000/api/query").mock(
            return_value=Response(200, json=sample_search_results)
        )

        result = mock_client.search("machine learning", top_k=5)
        assert "sources" in result
        assert len(result["sources"]) == 2

    @respx.mock
    def test_search_with_namespace(
        self, mock_client: RAGBrainClient, sample_search_results: dict
    ) -> None:
        """Test search request with namespace filter."""
        route = respx.post("http://test-api:8000/api/query").mock(
            return_value=Response(200, json=sample_search_results)
        )

        mock_client.search("test query", namespace="personal", top_k=3)

        # Verify request body
        request = route.calls.last.request
        import json
        body = json.loads(request.content)
        assert body["query"] == "test query"
        assert body["namespace"] == "personal"
        assert body["top_k"] == 3

    @respx.mock
    def test_get_document(
        self, mock_client: RAGBrainClient, sample_document: dict
    ) -> None:
        """Test get document request."""
        respx.get("http://test-api:8000/api/documents/id/abc-123").mock(
            return_value=Response(200, json=sample_document)
        )

        result = mock_client.get_document("abc-123")
        assert result["doc_id"] == "abc-123"
        assert result["filename"] == "notes.md"

    @respx.mock
    def test_http_error_handling(self, mock_client: RAGBrainClient) -> None:
        """Test HTTP error is raised properly."""
        respx.get("http://test-api:8000/health").mock(
            return_value=Response(500, json={"error": "Internal error"})
        )

        import httpx
        with pytest.raises(httpx.HTTPStatusError):
            mock_client.health_check()

    @respx.mock
    def test_404_error(self, mock_client: RAGBrainClient) -> None:
        """Test 404 error handling."""
        respx.get("http://test-api:8000/api/documents/id/not-found").mock(
            return_value=Response(404, json={"detail": "Document not found"})
        )

        import httpx
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            mock_client.get_document("not-found")
        assert exc_info.value.response.status_code == 404
