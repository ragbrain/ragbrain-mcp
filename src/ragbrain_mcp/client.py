"""HTTP client for RAGBrain API."""

import logging
from typing import Any

import httpx

from .config import Settings

logger = logging.getLogger("ragbrain-mcp")


class RAGBrainClient:
    """HTTP client for communicating with RAGBrain API.

    This client handles all HTTP communication with the RAGBrain backend,
    including proper error handling and response parsing.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize the client with settings.

        Args:
            settings: Server settings containing URL and timeout configuration.
        """
        self.base_url = settings.url
        self.timeout = settings.timeout
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """Lazy-initialize and return the HTTP client."""
        if self._client is None:
            self._client = httpx.Client(timeout=self.timeout)
        return self._client

    def close(self) -> None:
        """Close the HTTP client connection."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make GET request to RAGBrain API.

        Args:
            path: API endpoint path.
            params: Optional query parameters.

        Returns:
            JSON response as dictionary.

        Raises:
            httpx.HTTPStatusError: If the request fails.
            httpx.ConnectError: If connection fails.
        """
        url = f"{self.base_url}{path}"
        logger.debug(f"GET {url} params={params}")
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make POST request to RAGBrain API.

        Args:
            path: API endpoint path.
            data: JSON body data.

        Returns:
            JSON response as dictionary.

        Raises:
            httpx.HTTPStatusError: If the request fails.
            httpx.ConnectError: If connection fails.
        """
        url = f"{self.base_url}{path}"
        logger.debug(f"POST {url} data={data}")
        response = self.client.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict[str, Any]:
        """Check if RAGBrain API is healthy.

        Returns:
            Health status response.
        """
        return self._get("/health")

    def list_namespaces(self, include_stats: bool = True) -> dict[str, Any]:
        """List all namespaces with optional statistics.

        Args:
            include_stats: Whether to include document/chunk counts.

        Returns:
            Response containing list of namespaces.
        """
        return self._get(
            "/api/namespaces",
            {"include_stats": include_stats, "include_children": True},
        )

    def get_namespace_tree(self, include_stats: bool = True) -> dict[str, Any]:
        """Get namespace hierarchy as a tree structure.

        Args:
            include_stats: Whether to include document/chunk counts.

        Returns:
            Response containing namespace tree.
        """
        return self._get("/api/namespaces/tree", {"include_stats": include_stats})

    def browse_namespace(self, namespace: str, limit: int = 50) -> dict[str, Any]:
        """List documents in a namespace.

        Args:
            namespace: Namespace identifier to browse.
            limit: Maximum number of documents to return.

        Returns:
            Response containing document list.
        """
        # Use /api/documents which queries Qdrant directly via document summaries
        # This doesn't require the namespace to exist in Redis
        result = self._get("/api/documents", {"namespace": namespace})

        # Apply limit and format response to match expected structure
        documents = result.get("documents", [])[:limit]
        return {
            "namespace": namespace,
            "documents": documents,
            "total": len(documents)
        }

    def search(
        self,
        query: str,
        namespace: str | None = None,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """Perform semantic search in knowledge base.

        Args:
            query: Search query string.
            namespace: Optional namespace to limit search scope.
            top_k: Number of results to return.

        Returns:
            Response containing search results.
        """
        data: dict[str, Any] = {
            "query": query,
            "top_k": top_k,
        }
        if namespace:
            data["namespace"] = namespace
        return self._post("/api/query", data)

    def get_document(self, doc_id: str) -> dict[str, Any]:
        """Get full document content by ID.

        Args:
            doc_id: Document UUID.

        Returns:
            Response containing full document content.
        """
        return self._get(f"/api/documents/id/{doc_id}")

    def discover_documents(
        self,
        query: str,
        namespace: str | None = None,
        top_k: int = 10,
    ) -> dict[str, Any]:
        """Discover documents semantically matching a query.

        Uses vector search over document summaries to find relevant documents
        by topic or content. This is more targeted than browsing a namespace.

        Args:
            query: Semantic search query (e.g., "documents about leadership").
            namespace: Optional namespace filter (supports wildcards like 'mba/*').
            top_k: Number of documents to return.

        Returns:
            Response containing matched documents with scores.
        """
        params: dict[str, Any] = {
            "query": query,
            "top_k": top_k,
        }
        if namespace:
            params["namespace"] = namespace
        return self._get("/api/documents/discover", params)
