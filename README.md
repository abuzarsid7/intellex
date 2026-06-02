# Intellex Chatbot

Intellex Chatbot is a full-stack chatbot app with a React + Vite frontend and a FastAPI backend. It supports JWT authentication, chat persistence, PDF upload ingestion, and Chroma-backed retrieval-augmented generation.

## Deployment

- Frontend: https://intellex-sand.vercel.app/
- Backend: https://squid-app-hgnfm.ondigitalocean.app/

## Tech Stack

### Frontend

- React 19 - component-based UI for the chat app and auth flows.
- Vite - fast local development and production bundling.
- React Router - page routing for login, signup, home, and protected views.
- Axios - API client with JWT bearer header injection.
- Tailwind CSS - utility-first styling for fast layout and theme work.

### Backend

- FastAPI - async API framework with strong request validation and OpenAPI support.
- Pydantic - schema validation and response shaping.
- Uvicorn - ASGI server used to run the API.
- Motor / MongoDB - async database access for users, chats, messages, and uploads.
- python-jose - JWT creation and verification.
- bcrypt - password hashing.
- pypdf - PDF text extraction before ingestion.
- ChromaDB - vector store for retrieval on uploaded documents.

### Tooling

- ESLint - frontend linting.
- python-dotenv - environment variable loading.
- Vercel - frontend hosting.
- DigitalOcean App Platform - backend hosting.

## How to Run Locally

The frontend can be run with Node.js only. The backend is Python-based, so a full local backend run also requires Python 3.11+ and pip.

### Frontend

```bash
cd client
npm install
npm run dev
```

The app will be available at http://localhost:5173.

### Backend

```bash
cd server-python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

If your shell does not have `python3`, install Python 3.11+ first. The API will be available at http://localhost:8000.

## API Documentation

All protected endpoints expect `Authorization: Bearer <token>`.

### Auth

#### `POST /api/auth/signup`

Request body:

```json
{
	"name": "Ada Lovelace",
	"email": "ada@example.com",
	"password": "secret123"
}
```

Response shape:

```json
{
	"success": true,
	"message": "User registered successfully",
	"access_token": "jwt-token",
	"token_type": "bearer",
	"user": {
		"_id": "user-id",
		"name": "Ada Lovelace",
		"email": "ada@example.com",
		"created_at": "2026-06-02T00:00:00Z",
		"updated_at": "2026-06-02T00:00:00Z"
	}
}
```

#### `POST /api/auth/login`

Request body:

```json
{
	"email": "ada@example.com",
	"password": "secret123"
}
```

Response shape:

```json
{
	"success": true,
	"message": "Logged in successfully",
	"access_token": "jwt-token",
	"token_type": "bearer",
	"user": {
		"_id": "user-id",
		"name": "Ada Lovelace",
		"email": "ada@example.com",
		"created_at": "2026-06-02T00:00:00Z",
		"updated_at": "2026-06-02T00:00:00Z"
	}
}
```

#### `POST /api/auth/logout`

Request body: none

Response shape:

```json
{
	"success": true,
	"message": "Logged out successfully"
}
```

#### `GET /api/auth/profile`

Request body: none

Response shape:

```json
{
	"success": true,
	"user": {
		"_id": "user-id",
		"name": "Ada Lovelace",
		"email": "ada@example.com",
		"created_at": "2026-06-02T00:00:00Z",
		"updated_at": "2026-06-02T00:00:00Z"
	}
}
```

### Chat

#### `POST /api/chat`

Request body:

```json
{
	"title": "New Chat",
	"description": "Optional description"
}
```

Response shape:

```json
{
	"success": true,
	"message": "Chat created successfully",
	"chat": {
		"_id": "chat-id",
		"title": "New Chat",
		"description": "Optional description",
		"userId": "user-id",
		"createdAt": "2026-06-02T00:00:00Z",
		"updatedAt": "2026-06-02T00:00:00Z"
	}
}
```

#### `GET /api/chat?page=1&limit=50`

Request body: none

Response shape:

```json
{
	"success": true,
	"chats": [],
	"page": 1,
	"limit": 50
}
```

#### `POST /api/chat/message`

Request body:

```json
{
	"chatId": "chat-id",
	"message": "What is in this document?",
	"useRAG": true
}
```

Response shape:

```json
{
	"success": true,
	"message": "Message sent successfully",
	"userMessage": {},
	"assistantMessage": {}
}
```

#### `GET /api/chat/:chat_id`

Request body: none

Response shape:

```json
{
	"success": true,
	"chat": {}
}
```

#### `GET /api/chat/:chat_id/messages?page=1&limit=100`

Request body: none

Response shape:

```json
{
	"success": true,
	"messages": [],
	"page": 1,
	"limit": 100
}
```

#### `GET /api/chat/:chat_id/files`

Request body: none

Response shape:

```json
{
	"success": true,
	"files": []
}
```

#### `PUT /api/chat/:chat_id/title`

Request body:

```json
{
	"title": "Renamed chat"
}
```

Response shape:

```json
{
	"success": true,
	"message": "Chat title updated",
	"chat": {}
}
```

#### `DELETE /api/chat/:chat_id`

Request body: none

Response shape:

```json
{
	"success": true,
	"message": "..."
}
```

#### `DELETE /api/chat/:chat_id/messages`

Request body: none

Response shape:

```json
{
	"success": true,
	"message": "..."
}
```

### Upload

#### `POST /api/upload`

Request body: `multipart/form-data`

- `file`: PDF file
- `chat_id` or `chatId`: optional chat id

Response shape:

```json
{
	"success": true,
	"file": {},
	"parsed": {
		"pages": [],
		"text": ""
	},
	"ingestion": {
		"success": true,
		"chunk_count": 0,
		"metadata": {}
	},
	"storedFile": {}
}
```

## Project Structure

```text
.
├── client/                  Frontend application
│   └── src/
│       ├── app/             Providers and route guards
│       ├── components/      Shared UI and layout components
│       ├── context/         React contexts
│       ├── features/        Feature-specific pages, hooks, and services
│       ├── pages/           Top-level pages like Home, Login, Signup
│       ├── services/        Axios client and API endpoint helpers
│       ├── styles/          Global styles, themes, and variables
│       └── utils/           Small shared helpers
├── server-python/           FastAPI backend
│   └── app/
│       ├── api/             Route definitions and dependencies
│       ├── controllers/     Request handlers
│       ├── core/            Config, database, security, logging
│       ├── middleware/      Auth, upload, and error middleware
│       ├── models/          Database models
│       ├── schemas/         Pydantic request/response schemas
│       ├── services/        Auth, chat, file, PDF, and RAG logic
│       └── utils/           Shared helpers
├── README.md                Project overview and setup notes
└── chroma-data/             Local Chroma persistence used for retrieval
```

## Next Steps

What I did not do yet:

- I did not add Docker or a one-command full-stack launcher.
- I did not add automated API smoke tests or frontend end-to-end tests.
- I did not add a production-ready token refresh flow.

What I would build next:

- A refresh-token flow so the JWT does not need to live in localStorage long term.
- Docker Compose for MongoDB, backend, and frontend to make local setup repeatable.
- A small API test suite for auth, chat creation, message sending, and uploads.
- Better upload feedback and chat streaming in the UI.
