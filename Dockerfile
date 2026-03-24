# Stage 1 — Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Stage 2 — Production stage
FROM python:3.12-slim

WORKDIR /app

# Security — create non-root user
RUN addgroup --system app && adduser --system --group app

# Copy dependencies from build stage
COPY --from=builder /usr/local/lib/python3.12/site-packages \
     /usr/local/lib/python3.12/site-packages

# Copy gunicorn binary — needed to run it
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy app code
COPY app/ .

# Health check — Kubernetes uses this
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5003/health')" \
  || exit 1

# Run as non-root user
USER app

EXPOSE 5001

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "app:app"]