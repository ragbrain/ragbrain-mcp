"""Tests for output formatters."""

import pytest

from ragbrain_mcp.formatters import (
    format_document,
    format_document_list,
    format_namespace_list,
    format_namespace_tree,
    format_search_results,
)


class TestFormatNamespaceList:
    """Tests for format_namespace_list function."""

    def test_empty_list(self) -> None:
        """Test formatting empty namespace list."""
        result = format_namespace_list([])
        assert "No namespaces found" in result

    def test_single_namespace(self) -> None:
        """Test formatting single namespace."""
        namespaces = [
            {
                "id": "personal",
                "name": "Personal",
                "description": "My personal notes",
                "doc_count": 10,
                "chunk_count": 100,
            }
        ]
        result = format_namespace_list(namespaces)
        assert "# RAGBrain Namespaces" in result
        assert "Personal" in result
        assert "`personal`" in result
        assert "My personal notes" in result
        assert "Documents: 10" in result
        assert "Chunks: 100" in result

    def test_multiple_namespaces(
        self, sample_namespaces: dict
    ) -> None:
        """Test formatting multiple namespaces."""
        result = format_namespace_list(sample_namespaces["namespaces"])
        assert "Personal" in result
        assert "Work" in result

    def test_namespace_without_description(self) -> None:
        """Test namespace without description."""
        namespaces = [{"id": "test", "name": "Test", "doc_count": 5, "chunk_count": 50}]
        result = format_namespace_list(namespaces)
        assert "Test" in result
        # Should not have empty description line


class TestFormatNamespaceTree:
    """Tests for format_namespace_tree function."""

    def test_empty_tree(self) -> None:
        """Test formatting empty tree."""
        result = format_namespace_tree([])
        assert "No namespaces found" in result

    def test_flat_tree(self) -> None:
        """Test formatting tree without children."""
        tree = [
            {"id": "a", "name": "A", "doc_count": 5, "children": []},
            {"id": "b", "name": "B", "doc_count": 10, "children": []},
        ]
        result = format_namespace_tree(tree)
        assert "# RAGBrain Namespace Tree" in result
        assert "**A**" in result
        assert "**B**" in result
        assert "5 docs" in result
        assert "10 docs" in result

    def test_nested_tree(self, sample_namespace_tree: dict) -> None:
        """Test formatting nested tree."""
        result = format_namespace_tree(sample_namespace_tree["tree"])
        assert "Personal" in result
        assert "Notes" in result
        assert "Work" in result


class TestFormatSearchResults:
    """Tests for format_search_results function."""

    def test_empty_results(self) -> None:
        """Test formatting empty search results."""
        result = format_search_results({"sources": []})
        assert "# Search Results" in result
        assert "No results found" in result

    def test_with_results(self, sample_search_results: dict) -> None:
        """Test formatting search results."""
        result = format_search_results(sample_search_results)
        assert "# Search Results" in result
        assert "Result 1" in result
        assert "Result 2" in result
        assert "0.950" in result  # score
        assert "ml-notes.md" in result
        assert "machine learning" in result

    def test_with_synthesized_answer(
        self, sample_search_results_with_answer: dict
    ) -> None:
        """Test formatting search results with answer."""
        result = format_search_results(sample_search_results_with_answer)
        # The formatter shows sources, answer is in the data but not specially formatted
        assert "Result 1" in result
        assert "ai-intro.md" in result

    def test_truncates_long_text(self) -> None:
        """Test that long text is truncated."""
        long_text = "x" * 2000
        results = {
            "question": "test",
            "sources": [
                {
                    "content": long_text,
                    "score": 0.9,
                    "metadata": {"filename": "test.txt", "namespace": "test"},
                }
            ],
            "namespace": "default",
            "reranked": False,
        }
        result = format_search_results(results)
        assert "..." in result
        assert len(result) < len(long_text) + 500  # Some overhead for formatting


class TestFormatDocumentList:
    """Tests for format_document_list function."""

    def test_empty_list(self) -> None:
        """Test formatting empty document list."""
        result = format_document_list({"namespace": "test", "documents": [], "total": 0})
        assert "Documents in `test`" in result
        assert "No documents found" in result

    def test_with_documents(self, sample_documents: dict) -> None:
        """Test formatting document list."""
        result = format_document_list(sample_documents)
        assert "Documents in `personal`" in result
        assert "Total:** 2" in result
        assert "notes.md" in result
        assert "guide.pdf" in result
        assert "abc-123" in result


class TestFormatDocument:
    """Tests for format_document function."""

    def test_basic_document(self, sample_document: dict) -> None:
        """Test formatting basic document."""
        result = format_document(sample_document)
        assert "# notes.md" in result
        assert "`abc-123`" in result
        assert "personal" in result
        assert "Chunks:** 5" in result
        assert "My Notes" in result

    def test_truncates_long_document(self) -> None:
        """Test that long documents are truncated."""
        doc = {
            "doc_id": "test-123",
            "filename": "long.txt",
            "namespace": "test",
            "total_chunks": 100,
            "reconstructed_text": "x" * 200000,
        }
        result = format_document(doc, max_length=1000)
        assert "[Document truncated" in result
        assert len(result) < 2000
