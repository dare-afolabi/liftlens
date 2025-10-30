# === STAGE 1: Builder ===
FROM python:3.11-slim AS builder

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Poetry
ENV POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Copy source
WORKDIR /app
COPY pyproject.toml poetry.lock ./
COPY liftlens ./liftlens
COPY scripts ./scripts
COPY examples ./examples
COPY data ./data

# Install dependencies
RUN poetry install --only main --no-root --extras "parallel"

# === STAGE 2: Runtime ===
FROM python:3.11-slim AS runtime

# System runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

# Copy venv from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy app
WORKDIR /app
COPY --from=builder /app /app

# Create output/logs
RUN mkdir -p output logs && chown appuser:appuser output logs

USER appuser

# Expose ports
EXPOSE 8000 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Default command (overridden by docker-compose)
CMD ["sh", "-c", "uvicorn liftlens.api.server:app --host 0.0.0.0 --port 8000 & streamlit run liftlens.api.dashboard.py --server.port=8501 --server.headless=true"]
