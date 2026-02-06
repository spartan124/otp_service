# STAGE 1: Builder (Installs tools and dependencies)
FROM python:3.12.1-slim-bookworm AS builder

# Install uv (Pinned version)
COPY --from=ghcr.io/astral-sh/uv:0.10.0 /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# STAGE 2: Runner (The actual app image)
FROM python:3.12-slim

# Create a non-root user
RUN useradd -m appuser
USER appuser
WORKDIR /app

# Copy the environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Copy the application code (ONCE)
COPY --chown=appuser:appuser app ./app

# Copy the startup script (NEW)
COPY --chown=appuser:appuser start.sh ./start.sh

# Make it executable (You own it, so you can chmod it)
RUN chmod +x ./start.sh

# Add the virtual environment to the PATH (ONCE)
ENV PATH="/app/.venv/bin:$PATH"

# Default command: Runs the startup script to launch API + Worker
CMD ["./start.sh"]