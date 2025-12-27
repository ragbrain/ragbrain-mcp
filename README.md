# Deprecated
This project has moved to [stache-ai](https://github.com/stache-ai/stache-ai) - it is no longer maintained here.

# RAGBrain MCP

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MCP server that connects [Claude Desktop](https://claude.ai/download) to your [RAGBrain](https://github.com/ragbrain/ragbrain) knowledge base.

## Install

```bash
pip install ragbrain-mcp
```

## Configure Claude Desktop

Add to your config file:

| OS | Path |
|----|------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

```json
{
  "mcpServers": {
    "ragbrain": {
      "command": "ragbrain-mcp",
      "env": {
        "RAGBRAIN_URL": "http://localhost:8000"
      }
    }
  }
}
```

Restart Claude Desktop. Done.

## Tools

| Tool | Description |
|------|-------------|
| `ragbrain_list_namespaces` | List namespaces with doc counts |
| `ragbrain_search` | Semantic search |
| `ragbrain_browse_namespace` | List docs in a namespace |
| `ragbrain_get_document` | Get full document by ID |
| `ragbrain_discover_documents` | Find docs by topic via summary search |

## Example prompts

- "What namespaces do I have?"
- "Search for machine learning"
- "Show docs in work/projects"
- "Get document abc-123"

## Config

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `RAGBRAIN_URL` | `http://localhost:8000` | RAGBrain API URL |
| `RAGBRAIN_TIMEOUT` | `60` | Request timeout (seconds) |
| `RAGBRAIN_LOG_LEVEL` | `INFO` | DEBUG, INFO, WARNING, ERROR |
| `RAGBRAIN_MAX_RESULTS` | `20` | Max search results |
| `RAGBRAIN_MAX_DOCUMENT_LENGTH` | `100000` | Max doc length (chars) |

## Development

```bash
git clone https://github.com/ragbrain/ragbrain-mcp.git
cd ragbrain-mcp
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest
```

```
┌─────────────────┐     stdio      ┌─────────────────┐     HTTP      ┌─────────────────┐
│  Claude Desktop │ ◄────────────► │  RAGBrain MCP   │ ◄───────────► │  RAGBrain API   │
└─────────────────┘                └─────────────────┘               └─────────────────┘
```

## Troubleshooting

**Can't connect?** Check RAGBrain is running: `curl http://localhost:8000/health`

**Tools not showing?** Verify config path, test with `ragbrain-mcp`, restart Claude Desktop.

**Timeouts?** Set `RAGBRAIN_TIMEOUT` higher.

## License

MIT
