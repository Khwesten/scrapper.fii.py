# Use Python Alpine image (minimal and lightweight)
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Set work directory
WORKDIR /app

# Install system dependencies required for some Python packages
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libxml2-dev \
    libxslt-dev \
    curl \
    && rm -rf /var/cache/apk/*

# Install Poetry
RUN pip install poetry==1.8.3

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Configure poetry: disable virtual env creation since we're in a container
# Install dependencies including dev dependencies for development builds
RUN poetry config virtualenvs.create false \
    && poetry install --no-root \
    && rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY . .

# Make entrypoint script executable
RUN chmod +x scripts/entrypoint.sh

# Create non-root user for security
RUN addgroup -g 1001 -S appuser && \
    adduser -S appuser -u 1001 -G appuser

# Change ownership of the app directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application using Poetry
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
