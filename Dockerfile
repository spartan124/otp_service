# Dockerfile

# STAGE 1: Builder (Installs tools and dependencies)
FROM python:3.12.1-slim-bookworm AS builder

# Install uv (The modern way)
COPY --from=ghcr.io/astral-sh/uv:0.10.0 /uv /bin/uv
# Set working directory
WORKDIR /app

# Copy dependency files first (for better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
# --frozen: ensures we stick exactly to uv.lock versions
# --no-dev: excludes pytest/dev tools for production
RUN uv sync --frozen --no-dev

# STAGE 2: Runner (The actual app image)
FROM python:3.12-slim

# Create a non-root user for security (Render likes this)
RUN useradd -m appuser
USER appuser
WORKDIR /app

# Copy the environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Copy the application code
COPY --chown=appuser:appuser app ./app

# Add the virtual environment to the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Default command (Running the API)
# We use '0.0.0.0' so the container listens outside itself
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]