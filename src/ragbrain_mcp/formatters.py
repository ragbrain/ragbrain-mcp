"""Output formatters for RAGBrain MCP responses.

These formatters convert RAGBrain API responses into human-readable
Markdown format suitable for display in Claude.
"""

from typing import Any

# Maximum length for truncated content
MAX_CHUNK_LENGTH = 1000


def format_namespace_list(namespaces: list[dict[str, Any]]) -> str:
    """Format namespace list as Markdown.

    Args:
        namespaces: List of namespace dictionaries from API.

    Returns:
        Formatted Markdown string.
    """
    if not namespaces:
        return "No namespaces found. Create one in the RAGBrain UI."

    lines = ["# RAGBrain Namespaces\n"]

    for ns in namespaces:
        doc_count = ns.get("doc_count", 0)
        chunk_count = ns.get("chunk_count", 0)
        desc = ns.get("description", "")
        name = ns.get("name", "Unknown")
        ns_id = ns.get("id", "")

        lines.append(f"## {name}")
        lines.append(f"**ID:** `{ns_id}`")
        if desc:
            lines.append(f"*{desc}*")
        lines.append(f"Documents: {doc_count} | Chunks: {chunk_count}")
        lines.append("")

    return "\n".join(lines)


def format_namespace_tree(tree: list[dict[str, Any]], indent: int = 0) -> str:
    """Format namespace tree as Markdown with indentation.

    Args:
        tree: List of namespace tree nodes from API.
        indent: Current indentation level.

    Returns:
        Formatted Markdown string.
    """
    if not tree and indent == 0:
        return "No namespaces found. Create one in the RAGBrain UI."

    lines = []

    if indent == 0:
        lines.append("# RAGBrain Namespace Tree\n")

    for node in tree:
        prefix = "  " * indent
        doc_count = node.get("doc_count", 0)
        name = node.get("name", "Unknown")
        ns_id = node.get("id", "")

        lines.append(f"{prefix}- **{name}** (`{ns_id}`) — {doc_count} docs")

        children = node.get("children", [])
        if children:
            lines.append(format_namespace_tree(children, indent + 1))

    return "\n".join(lines)


def format_search_results(result: dict[str, Any]) -> str:
    """Format search results as Markdown.

    Args:
        result: Search result dictionary from API.

    Returns:
        Formatted Markdown string.
    """
    lines = ["# Search Results\n"]

    # Show individual chunks (API returns "sources" with "content")
    chunks = result.get("sources", [])
    if not chunks:
        lines.append("No results found for this query.")
        return "\n".join(lines)

    for i, chunk in enumerate(chunks, 1):
        score = chunk.get("score", 0)
        text = chunk.get("content", "")
        metadata = chunk.get("metadata", {})
        filename = metadata.get("filename", "Unknown source")
        namespace = metadata.get("namespace", "default")

        # Truncate long text
        if len(text) > MAX_CHUNK_LENGTH:
            text = text[:MAX_CHUNK_LENGTH] + "..."

        lines.append(f"### Result {i} (score: {score:.3f})")
        lines.append(f"**Source:** {filename} | **Namespace:** {namespace}")
        lines.append(f"\n{text}\n")

    return "\n".join(lines)


def format_document_list(result: dict[str, Any]) -> str:
    """Format document list as Markdown.

    Args:
        result: Document list response from API.

    Returns:
        Formatted Markdown string.
    """
    namespace = result.get("namespace", "unknown")
    documents = result.get("documents", [])
    total = result.get("total", len(documents))

    lines = [f"# Documents in `{namespace}`\n"]
    lines.append(f"**Total:** {total} documents\n")

    if not documents:
        lines.append("No documents found in this namespace.")
        return "\n".join(lines)

    for doc in documents:
        filename = doc.get("filename", "Untitled")
        doc_id = doc.get("doc_id", "")
        # Handle both field names (total_chunks from old API, chunk_count from new)
        chunks = doc.get("total_chunks") or doc.get("chunk_count", "?")
        created = doc.get("created_at", "")[:10] if doc.get("created_at") else "N/A"

        lines.append(f"- **{filename}**")
        lines.append(f"  - ID: `{doc_id}`")
        lines.append(f"  - Chunks: {chunks} | Created: {created}")

    return "\n".join(lines)


def format_document(result: dict[str, Any], max_length: int = 100000) -> str:
    """Format full document as Markdown.

    Args:
        result: Document response from API.
        max_length: Maximum content length to return.

    Returns:
        Formatted Markdown string.
    """
    filename = result.get("filename", "Untitled")
    doc_id = result.get("doc_id", "")
    namespace = result.get("namespace", "default")
    total_chunks = result.get("total_chunks", 0)
    text = result.get("reconstructed_text", "")

    # Truncate if too long
    truncated = False
    if len(text) > max_length:
        text = text[:max_length]
        truncated = True

    lines = [
        f"# {filename}",
        "",
        f"**ID:** `{doc_id}`",
        f"**Namespace:** {namespace}",
        f"**Chunks:** {total_chunks}",
        "",
        "---",
        "",
        text,
    ]

    if truncated:
        lines.append("\n\n*[Document truncated due to length]*")

    return "\n".join(lines)


def format_discover_results(result: dict[str, Any]) -> str:
    """Format document discovery results as Markdown.

    Args:
        result: Discovery response from API.

    Returns:
        Formatted Markdown string.
    """
    query = result.get("query", "")
    documents = result.get("documents", [])
    count = result.get("count", len(documents))

    lines = [f"# Document Discovery Results\n"]
    lines.append(f"**Query:** {query}")
    lines.append(f"**Found:** {count} documents\n")

    if not documents:
        lines.append("No documents found matching this query.")
        return "\n".join(lines)

    for i, doc in enumerate(documents, 1):
        filename = doc.get("filename", "Untitled")
        doc_id = doc.get("doc_id", "")
        namespace = doc.get("namespace", "default")
        score = doc.get("score", 0)
        chunk_count = doc.get("chunk_count", "?")
        headings = doc.get("headings", [])
        preview = doc.get("summary_preview", "")

        lines.append(f"### {i}. {filename} (score: {score:.3f})")
        lines.append(f"**ID:** `{doc_id}` | **Namespace:** {namespace} | **Chunks:** {chunk_count}")

        if headings:
            # Show first 5 headings
            heading_str = ", ".join(headings[:5])
            if len(headings) > 5:
                heading_str += f" (+{len(headings) - 5} more)"
            lines.append(f"**Headings:** {heading_str}")

        if preview:
            # Truncate preview if too long
            if len(preview) > 200:
                preview = preview[:200] + "..."
            lines.append(f"\n*{preview}*")

        lines.append("")

    return "\n".join(lines)
