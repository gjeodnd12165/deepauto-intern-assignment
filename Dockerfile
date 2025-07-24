# --- Builder Stage ---
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
# REMOVED ENV PLAYWRIGHT_BROWSERS_PATH=0

# Copy only dependency definition files
COPY pyproject.toml uv.lock ./

# 2. <<< FIX: Perform all installations and then forcefully remove GPU packages in ONE layer.
RUN set -e && \
    echo "STEP 1: Creating venv..." && \
    uv venv && \
    \
    echo "STEP 2: Installing all dependencies from lockfile (including GPU versions for now)..." && \
    uv sync --no-cache-dir --frozen --no-install-project && \
    \
    echo "STEP 3: Uninstalling torch and triton to remove GPU dependencies..." && \
    uv pip uninstall torch torchvision torchaudio triton && \
    \
    echo "STEP 4: Installing the clean, CPU-only version of torch..." && \
    uv pip install torch --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu && \
    \
    echo "STEP 5: Cleaning up all caches..." && \
    uv cache clean && \
    echo "Installation and cleanup complete."

# # Create venv before install torch
# RUN uv venv

# # Manually pre-install the SMALLER, CPU-only version of torch.
# # This will prevent uv sync from installing the massive default torch package.
# # Clean the uv cache to reduce the size of this layer.
# RUN set -e && \
#     uv venv && \
#     uv pip install torch --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu && \
#     uv sync --no-cache-dir --frozen --no-install-project && \
#     uv cache clean

# # Install ONLY third-party dependencies from the lockfile
# RUN --mount=type=cache,target=/root/.cache/uv \
#     uv sync --frozen --no-install-project

# Manually install only Chromium.
RUN /app/.venv/bin/playwright install --with-deps chromium

# Copy the rest of the source code
COPY . .

# Install the local project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --no-deps .


# --- Final Stage ---
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy the virtual environment
COPY --from=builder /app/.venv ./.venv

# Copy the Playwright browser cache.
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright

# Copy the application source code
COPY --from=builder /app/src ./src

# Set the PATH to find executables in the final image
ENV PATH="/app/.venv/bin:$PATH"

# Set the entrypoint
ENTRYPOINT ["mcp-server"]