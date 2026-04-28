# AI Chatbot SaaS

Production-ready AI chatbot SaaS for support, sales, and documentation search.

## Build Plan

1. Architecture and overview
2. Backend generation
3. Frontend widget generation
4. Full integration

The implementation will use:

- Frontend: React
- Backend: FastAPI
- AI: OpenAI API
- Vector store: FAISS by default, Pinecone-ready adapter
- Database: PostgreSQL
- Auth: JWT
- Email: SMTP or provider adapter

See [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) for the full system design.
See [docs/API.md](./docs/API.md) for the route surface and [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) for local and production setup.
