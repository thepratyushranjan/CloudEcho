# syntax=docker/dockerfile:1.5
FROM python:3.12-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System dependencies and Node.js (for MCP helpers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY fastapi_backend/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Install Node dependencies for the helper scripts
COPY fastapi_backend/package.json fastapi_backend/package.json
RUN npm install --prefix fastapi_backend --omit=dev

# Copy project code
COPY fastapi_backend ./fastapi_backend

EXPOSE 8000

CMD ["uvicorn", "fastapi_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
