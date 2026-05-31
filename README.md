# Intellex Chatbot

Intellex Chatbot is a full-stack chatbot project with a React + Vite client and a Node/Express backend that now covers authentication, chat persistence, PDF upload ingestion, and Chroma-backed RAG retrieval.

## Repository Structure

```text
Intellex-chatbot/
├── client/
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── app/
│       │   ├── providers/
│       │   │   ├── AuthProvider.jsx
│       │   │   └── ThemeProvider.jsx
│       │   ├── routes/
│       │   │   └── AppRoutes.jsx
│       │   └── store/
│       │       └── chatStore.js
│       ├── components/
│       │   ├── layout/
│       │   │   ├── MainLayout.jsx
│       │   │   ├── Navbar.jsx
│       │   │   └── Sidebar.jsx
│       │   └── ui/
│       │       ├── Button.jsx
│       │       ├── Input.jsx
│       │       ├── Loader.jsx
│       │       └── Modal.jsx
│       ├── context/
│       │   ├── AuthContext.jsx
│       │   └── ThemeContext.jsx
│       ├── features/
│       │   ├── auth/
│       │   │   ├── components/
│       │   │   ├── hooks/
│       │   │   ├── pages/
│       │   │   └── services/
│       │   ├── chat/
│       │   │   ├── components/
│       │   │   │   ├── ChatBox.jsx
│       │   │   │   ├── MessageBox.jsx
│       │   │   │   └── UploadBox.jsx
│       │   │   ├── hooks/
│       │   │   │   └── useChat.js
│       │   │   ├── pages/
│       │   │   │   └── ChatPage.jsx
│       │   │   └── services/
│       │   │       └── chatApi.js
│       │   └── upload/
│       │       ├── components/
│       │       ├── hooks/
│       │       └── services/
│       ├── hooks/
│       │   ├── useDebounce.js
│       │   └── useTheme.js
│       ├── pages/
│       │   ├── Home.jsx
│       │   ├── Login.jsx
│       │   └── Signup.jsx
│       ├── services/
│       │   ├── apiEndpoints.js
│       │   └── axios.js
│       ├── styles/
│       │   ├── globals.css
│       │   ├── themes.css
│       │   └── variables.css
│       └── utils/
│           ├── constants.js
│           └── formatDate.js
└── server/
    ├── package.json
    └── src/
        ├── app.js
        ├── server.js
        ├── config/
        │   ├── db.js
        │   └── env.js
        ├── controllers/
        │   ├── authController.js
        │   ├── chatController.js
        │   └── uploadController.js
        ├── middleware/
        │   ├── authMiddleware.js
        │   ├── errorMiddleware.js
        │   └── uploadMiddleware.js
        ├── models/
        │   ├── Chat.js
        │   ├── Message.js
        │   └── User.js
        ├── routes/
        │   ├── authRoutes.js
        │   ├── chatRoutes.js
        │   └── uploadRoutes.js
        ├── services/
        │   ├── ai/
        │   │   ├── embeddingService.js
        │   │   ├── llmService.js
        │   │   └── ragService.js
        │   ├── auth/
        │   │   └── authService.js
        │   └── db/
        │       └── vectorStoreService.js
        ├── uploads/
        └── utils/
            ├── generateToken.js
            └── logger.js
```

## What Has Been Implemented

### Client

- Tailwind CSS v4 is wired into Vite through `@tailwindcss/vite`.
- Dark and light mode support is implemented with a theme provider.
- Theme selection is stored in `localStorage` under `intellex-theme`.
- Theme preference is restored on page load and applied before React mounts to avoid a flash of the wrong theme.
- `useTheme()` is exposed through the context layer for consuming components.
- The starter app has been replaced with a small Tailwind-based theme demo screen.
- Global theme variables and base styles are defined in the `styles/` folder.

### Server

- Authentication is implemented with JWT cookies, protected routes, and user profile handling.
- Chat persistence is implemented with MongoDB chat and message models, controller endpoints, and message history helpers.
- PDF uploads are parsed on the server and the extracted text is chunked, embedded, and stored in a local Chroma persistent database.
- The RAG retrieval path is implemented so chat responses can optionally use Chroma document context through the existing `useRAG` flow.
- The server structure still includes room for additional auth, chat, upload, and retrieval enhancements, but the main backend flows are now live.

## Key Client Files

- [client/vite.config.js](client/vite.config.js)
- [client/src/index.css](client/src/index.css)
- [client/src/main.jsx](client/src/main.jsx)
- [client/src/context/ThemeContext.jsx](client/src/context/ThemeContext.jsx)
- [client/src/app/providers/ThemeProvider.jsx](client/src/app/providers/ThemeProvider.jsx)
- [client/src/App.jsx](client/src/App.jsx)
- [client/index.html](client/index.html)

## Notes

- The current client build passes successfully.
- Chroma now uses a local persistent path configured with `CHROMA_PATH` (default: `server-python/chroma-data`). No separate Chroma server is required for local development.
- The backend expects `CHROMA_PATH` and `CHROMA_COLLECTION_NAME` when needed.

## Recent Progress (Chat feature)

Below is a concise changelog of the chat-related work completed in this workspace during the current session:

- **Chat components added:** `ChatBox`, `MessageBox`, and `UploadBox` created under `client/src/features/chat/components/`. These provide the chat UI, message rendering (including code blocks and loading state), and a file upload UI.
- **Client hook implemented:** `useChat` added at `client/src/features/chat/hooks/useChat.js` to manage chat state, loading, error handling, and interactions with the API.
- **Chat service implemented:** `client/src/features/chat/services/chatApi.js` added with `sendChatMessage`, `uploadChatFiles`, `getChatHistory`, and `clearChatHistory` helper functions that use the existing axios instance.
- **API endpoints centralized:** `client/src/services/apiEndpoints.js` added and populated with `CHAT` endpoints (send, upload, get, delete, list) and other base endpoints.
- **Chat page scaffolded:** `client/src/features/chat/pages/ChatPage.jsx` added and wired to render the `ChatBox` inside the main layout.
- **Authentication backend completed:** user registration, login, logout, protected profile access, and auth middleware are implemented and wired into the server.
- **Chat persistence backend completed:** chat and message storage, retrieval, title updates, message clearing, and protected chat routes are implemented.
- **PDF upload ingestion added:** uploaded PDFs are parsed server-side, chunked, embedded, and stored in a local Chroma persistent database for later retrieval.
- **RAG retrieval added:** the chat response flow can now retrieve relevant Chroma chunks and feed them into the LLM when `useRAG` is enabled.

These changes are intended as a full-stack integration layer; the main frontend and backend flows are now connected, with Chroma as the document store for RAG-enabled uploads and retrieval.

If you'd like, I can:

- Wire `ChatPage` into the app routes (`client/src/app/routes/AppRoutes.jsx`).
- Add tests or storybook stories for the new components.
- Add a README section for local setup, environment variables, and how to run the server with Chroma.
