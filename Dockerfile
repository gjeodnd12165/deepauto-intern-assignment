# --- Builder Stage ---
# Use Ubuntu 24.04 (Noble Numbat) as the base image
FROM ubuntu:24.04 AS builder

# Install necessary dependencies: Python 3.12, venv support, and pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install the specific version of uv using pip
COPY --from=ghcr.io/astral-sh/uv:0.8.2 /uv /uvx /bin/

# Set python3.12 as the default python
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy only dependency definition files
COPY pyproject.toml uv.lock* ./

# Create venv using the system's python
RUN python3 -m venv .venv

# Activate the venv for subsequent RUN commands
ENV PATH="/app/.venv/bin:$PATH"

# Install ONLY third-party dependencies from the lockfile into the venv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Copy the rest of the source code
COPY . .

# Install the local project itself into the venv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --no-deps .


# --- Final Stage ---
FROM mcr.microsoft.com/playwright/python:v1.54.0-noble

WORKDIR /app

# Copy the virtual environment
COPY --from=builder /app/.venv ./.venv

# Copy the application source code
COPY --from=builder /app/src ./src

# Copy the document files
COPY --from=builder /app/html ./html
COPY --from=builder /app/pdf ./pdf

# Set the PATH to find executables in the final image
ENV PATH="/app/.venv/bin:$PATH"

# Set the entrypoint
ENTRYPOINT ["mcp-server"]