# Chatbotify Backend

This is the backend service for the Chatbotify application, providing API endpoints for document scraping and querying.

## Docker Setup

### Prerequisites

- Docker and Docker Compose installed on your system
- Environment variables configured (see below)

### Environment Variables

The following environment variables need to be set:

- `POSTGRES_CONNECTION`: PostgreSQL connection string
- `GEMINI_API_KEY`: Google Gemini API Key
- `LOGGING_LEVEL`: (Optional) Logging level (default: INFO)

You can set these variables in a `.env` file in the project root directory. See `.env.example` for a template.

### Building and Running with Docker

1. Build and start the container:

```bash
docker-compose up -d
```

2. To stop the container:

```bash
docker-compose down
```

### Running without Docker Compose

1. Build the Docker image:

```bash
docker build -t chatbotify-backend .
```

2. Run the container:

```bash
docker run -p 8000:8000 \
  -e POSTGRES_CONNECTION="your-postgres-connection-string" \
  -e GEMINI_API_KEY="your-gemini-api-key" \
  -e LOGGING_LEVEL="INFO" \
  chatbotify-backend
```

## API Documentation

Once the service is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc