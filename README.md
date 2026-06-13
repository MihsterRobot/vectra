# Vectra

A RAG (Retrieval-Augmented Generation) API that lets users upload documents and query them using natural language. Built with FastAPI, PostgreSQL, Pinecone, and the Anthropic API.

## Features

- User registration and JWT-based authentication
- Document upload (PDF and plain text)
- Automatic text chunking and vector embedding via Pinecone
- Natural language querying powered by Claude
- Per-user document isolation via Pinecone namespaces

## Tech Stack

- **FastAPI** — API framework
- **PostgreSQL** — user and document metadata storage
- **Pinecone** — vector storage and semantic search
- **Anthropic API** — response generation
- **Docker** — containerised local development
- **Railway** — cloud deployment

## Getting Started

### Prerequisites

- Docker Desktop
- A Pinecone account and index
- An Anthropic API key

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/MihsterRobot/vectra.git
   cd vectra
   ```

2. Copy the environment template and fill in your values:
   ```bash
   cp .env.example .env
   ```

3. Start the containers:
   ```bash
   docker compose up --build
   ```

4. The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/token` | Obtain a JWT token | No |
| POST | `/documents/upload` | Upload a PDF or text file | Yes |
| GET | `/documents/` | List uploaded documents | Yes |
| DELETE | `/documents/{id}` | Delete a document | Yes |
| POST | `/query/` | Query documents | Yes |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `PINECONE_API_KEY` | Pinecone API key |
| `PINECONE_INDEX_NAME` | Pinecone index name |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `SECRET_KEY` | JWT signing secret |
