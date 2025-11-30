# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Security Considerations

### Network Communication

RAGBrain MCP communicates with a RAGBrain backend server over HTTP. Important considerations:

1. **Use HTTPS in Production**: When connecting to a remote RAGBrain instance, always use HTTPS to encrypt traffic:
   ```bash
   export RAGBRAIN_URL=https://your-ragbrain-server.com
   ```

2. **Local Development**: HTTP is acceptable when both MCP server and RAGBrain run on localhost.

3. **Network Exposure**: The MCP server itself does not expose any network ports. It communicates with Claude Desktop via stdio (standard input/output).

### Authentication

Currently, RAGBrain MCP does not implement authentication between the MCP server and RAGBrain backend. This is acceptable for:
- Local development (both on same machine)
- Trusted network environments

For production deployments with remote RAGBrain instances, consider:
- Using a VPN or private network
- Implementing API key authentication in RAGBrain
- Using a reverse proxy with authentication

### Data Privacy

- **Query Logging**: Search queries and tool calls are logged at INFO level. In production, consider setting `RAGBRAIN_LOG_LEVEL=WARNING` to reduce logged data.
- **Document Content**: Full document content may be returned to Claude Desktop. Ensure sensitive documents are appropriately managed in RAGBrain.

### Input Validation

RAGBrain MCP validates input parameters:
- Query length limits (1-1000 characters)
- Result count limits (1-20)
- Document length limits (configurable)
- URL format validation

### Dependencies

We pin dependency version ranges and regularly update:
- `mcp`: MCP protocol library
- `httpx`: HTTP client
- `pydantic`: Configuration validation

## Reporting a Vulnerability

If you discover a security vulnerability, please:

1. **Do NOT** open a public issue
2. Open a private security advisory on GitHub
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to:
1. Confirm the vulnerability
2. Develop a fix
3. Release a patched version
4. Credit you in the release notes (unless you prefer anonymity)

## Security Best Practices for Users

1. **Keep Updated**: Always use the latest version
2. **Limit Access**: Only grant MCP access to trusted Claude Desktop installations
3. **Monitor Logs**: Review logs for unusual activity
4. **Secure RAGBrain**: Follow RAGBrain's security guidelines for the backend
5. **Environment Variables**: Don't commit `.env` files with sensitive URLs
