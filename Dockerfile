# syntax=docker/dockerfile:1.5
FROM python:3.12-slim
# Set the working directory to /app
WORKDIR /app
# Set environment variables to optimize Python behavior in Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app
# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
# Download the NLTK data resource required for tokenization
RUN python -c "import nltk; nltk.download('punkt_tab')"
# Copy the current directory contents into the container at /app
COPY app/ /app/
# Expose port 8000 to the host
EXPOSE 8000
# Verify files were copied correctly (for debugging)
RUN ls -la /app

# Run the FastAPI application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
