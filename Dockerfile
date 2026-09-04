# DevBrain Unified MCP Server Container
# Multi-stage minimal footprint build (<60MB)
FROM python:3.12-slim AS runtime

# Install Git (required by devbrain_daemon for commit tracking) and curl for healthchecks
RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl && \
    rm -rf /var/lib/apt/lists/*

# Create unprivileged user
RUN useradd -m -u 1000 devbrain

WORKDIR /app

# Copy application source code and configuration
COPY src/ /app/src/
COPY config/ /app/config/

# Ensure proper permissions
RUN chown -R devbrain:devbrain /app

# Environment defaults for MCP and UTF-8 standard I/O
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PYTHONUTF8=1 \
    VAULT_DIR=/vault \
    PROJECTS_DIR=/projects \
    PROJECTS_CONFIG=/app/config/projects.json

USER devbrain

# Mount points:
# /vault: Obsidian Vault directory (Read/Write)
# /projects: Monitored code repositories (Read-Only recommended)
VOLUME ["/vault", "/projects"]

# Default command launches MCP server over stdio
ENTRYPOINT ["python", "-u", "/app/src/devbrain_mcp.py"]
