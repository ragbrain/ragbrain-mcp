"""Pytest configuration and fixtures for RAGBrain MCP tests."""

import pytest

from ragbrain_mcp.client import RAGBrainClient
from ragbrain_mcp.config import Settings
from ragbrain_mcp.tools import ToolHandler


@pytest.fixture
def settings() -> Settings:
    """Create test settings."""
    return Settings(
        url="http://localhost:8000",
        timeout=10.0,
        log_level="DEBUG",
        max_results=20,
        max_document_length=10000,
    )


@pytest.fixture
def client(settings: Settings) -> RAGBrainClient:
    """Create a test RAGBrain client."""
    return RAGBrainClient(settings)


@pytest.fixture
def tool_handler(client: RAGBrainClient, settings: Settings) -> ToolHandler:
    """Create a test tool handler."""
    return ToolHandler(client, settings)


# Sample API responses for mocking
@pytest.fixture
def sample_namespaces() -> dict:
    """Sample namespace list response."""
    return {
        "namespaces": [
            {
                "id": "personal",
                "name": "Personal",
                "description": "Personal notes and documents",
                "doc_count": 15,
                "chunk_count": 150,
            },
            {
                "id": "work",
                "name": "Work",
                "description": "Work-related documents",
                "doc_count": 25,
                "chunk_count": 300,
            },
        ]
    }


@pytest.fixture
def sample_namespace_tree() -> dict:
    """Sample namespace tree response."""
    return {
        "tree": [
            {
                "id": "personal",
                "name": "Personal",
                "doc_count": 15,
                "children": [
                    {"id": "personal/notes", "name": "Notes", "doc_count": 10, "children": []},
                ],
            },
            {
                "id": "work",
                "name": "Work",
                "doc_count": 25,
                "children": [],
            },
        ]
    }


@pytest.fixture
def sample_search_results() -> dict:
    """Sample search results response."""
    return {
        "question": "machine learning",
        "sources": [
            {
                "content": "This is a sample search result about machine learning.",
                "score": 0.95,
                "metadata": {
                    "filename": "ml-notes.md",
                    "namespace": "personal",
                    "doc_id": "abc-123",
                },
            },
            {
                "content": "Another result about deep learning techniques.",
                "score": 0.87,
                "metadata": {
                    "filename": "dl-guide.pdf",
                    "namespace": "work",
                    "doc_id": "def-456",
                },
            },
        ],
        "namespace": "default",
        "reranked": False,
    }


@pytest.fixture
def sample_search_results_with_answer() -> dict:
    """Sample search results with synthesized answer."""
    return {
        "question": "what is machine learning",
        "sources": [
            {
                "content": "Machine learning is a subset of AI.",
                "score": 0.92,
                "metadata": {
                    "filename": "ai-intro.md",
                    "namespace": "personal",
                    "doc_id": "ghi-789",
                },
            },
        ],
        "answer": "Machine learning is a field of artificial intelligence that enables systems to learn from data.",
        "namespace": "default",
        "reranked": False,
    }


@pytest.fixture
def sample_documents() -> dict:
    """Sample document list response."""
    return {
        "namespace": "personal",
        "total": 2,
        "documents": [
            {
                "doc_id": "abc-123",
                "filename": "notes.md",
                "total_chunks": 5,
                "created_at": "2024-01-15T10:30:00Z",
            },
            {
                "doc_id": "def-456",
                "filename": "guide.pdf",
                "total_chunks": 12,
                "created_at": "2024-01-20T14:00:00Z",
            },
        ],
    }


@pytest.fixture
def sample_document() -> dict:
    """Sample full document response."""
    return {
        "doc_id": "abc-123",
        "filename": "notes.md",
        "namespace": "personal",
        "total_chunks": 5,
        "reconstructed_text": "# My Notes\n\nThis is the content of my notes document.\n\n## Section 1\n\nSome important information here.",
    }
