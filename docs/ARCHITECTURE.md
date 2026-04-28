# Architecture and Overview

## 1. Product Summary

This project is a multi-tenant AI chatbot SaaS that lets companies upload documentation, embed a website chat widget, answer customer questions with retrieval-augmented generation (RAG), cite sources, and escalate sensitive or low-confidence conversations to human teams by email.

Primary personas:

- SaaS admins who configure the bot, upload content, and review analytics
- Website visitors who interact with the chat widget
- Internal support, sales, or operations teams who receive escalations

## 2. High-Level Architecture

### Core subsystems

1. React chat widget
   - Embeddable by script tag
   - Talks to public chat APIs
   - Streams answers and shows citations

2. Admin dashboard
   - Login/signup
   - Workspace and bot configuration
   - Document upload and content management
   - Chat logs, escalations, analytics

3. FastAPI backend
   - Auth and workspace management
   - Ingestion pipeline
   - Query/RAG pipeline
   - Escalation engine
   - Analytics and admin APIs

4. PostgreSQL
   - Users, organizations, bots, documents, chunks metadata
   - Chats, messages, escalations, analytics events

5. Vector store abstraction
   - FAISS default for local/self-hosted deployments
   - Pinecone adapter for managed cloud search

6. Background workers
   - Document parsing
   - Embedding generation
   - URL crawling
   - Email delivery
   - Analytics aggregation jobs

7. Storage
   - Local or S3-compatible object store for PDFs and exported assets

8. Email service
   - SMTP or provider abstraction
   - Department-specific routing for escalation

## 3. Recommended Production Stack

### Frontend

- `widget/`: React + Vite + TypeScript
- `admin/`: React + Vite + TypeScript
- Styling: Tailwind CSS or CSS modules
- State: React Query + lightweight local state

### Backend

- FastAPI
- SQLAlchemy + Alembic
- Pydantic settings
- Celery or Dramatiq for async jobs
- Redis for queue/cache/rate limit state

### AI and Retrieval

- OpenAI `text-embedding-3-large` or `text-embedding-3-small`
- OpenAI chat model for answer generation and intent classification
- Hybrid retrieval design:
  - Dense vector retrieval via FAISS/Pinecone
  - Optional keyword fallback using PostgreSQL `tsvector`

### Data

- PostgreSQL for relational data
- FAISS index per tenant or logical namespace
- S3/local file storage for uploaded docs

## 4. Multi-Tenant SaaS Model

Each customer is an `organization`.

Each organization can have:

- multiple users
- one or more bots
- uploaded documents
- widget settings
- escalation routing rules
- chat sessions and analytics

Isolation rules:

- every API request is scoped by `organization_id`
- vector entries include `organization_id`, `bot_id`, `document_id`, and `chunk_id`
- auth tokens carry user identity and workspace access
- public widget access uses a publishable bot key, never an admin JWT

## 5. Core User Flows

### A. Admin onboarding

1. User signs up
2. Creates organization
3. Creates first bot
4. Configures brand, greeting, allowed domains, and escalation emails
5. Uploads docs or submits URLs
6. Embeds widget script on website

### B. Ingestion flow

1. Admin uploads PDF or submits URL/plain text
2. Backend stores source record in PostgreSQL
3. Worker extracts text
4. Text is cleaned and chunked
5. Embeddings are generated
6. Vectors and metadata are stored
7. Document status becomes `ready`

### C. Chat flow

1. Visitor opens widget
2. Widget creates or resumes session
3. User asks question
4. Backend embeds the query
5. Retriever fetches top relevant chunks
6. Confidence policy evaluates retrieval quality
7. LLM answers only from approved context
8. API returns answer, citations, confidence, and escalation status

### D. Escalation flow

1. Policy engine detects low confidence or sensitive intent
2. Intent classifier maps the issue to support/refund/complaint/sales/urgent
3. Chat transcript and metadata are compiled
4. Email job is queued
5. Admin dashboard records escalation status

## 6. Backend Service Design

### API domains

- `auth`
  - signup, login, refresh, profile
- `organizations`
  - workspace settings, member access
- `bots`
  - bot config, widget config, publishable key
- `documents`
  - upload, list, reprocess, delete
- `ingestion`
  - URL import, text import, crawl status
- `chat`
  - session create, ask, history
- `analytics`
  - top questions, failures, usage trends
- `escalations`
  - routing rules, event logs

### Internal modules

- `core/config.py`
- `core/security.py`
- `db/models/*`
- `services/ingestion/*`
- `services/rag/*`
- `services/escalation/*`
- `services/email/*`
- `workers/tasks/*`

## 7. RAG Pipeline Design

### Ingestion

Source types:

- PDF upload
- website URL crawl
- pasted plain text

Pipeline stages:

1. Extract text
2. Normalize content
3. Split into chunks with overlap
4. Enrich metadata
5. Generate embeddings
6. Upsert vectors

Recommended chunking defaults:

- chunk size: 700 to 1000 characters
- overlap: 100 to 150 characters
- preserve section titles when possible

Chunk metadata example:

- `organization_id`
- `bot_id`
- `document_id`
- `chunk_id`
- `source_type`
- `source_name`
- `source_url`
- `page_number`
- `section_title`

### Query-time retrieval

1. Embed user question
2. Retrieve top-k chunks
3. Filter by minimum similarity
4. Optional rerank
5. Build prompt with context and source metadata
6. Generate answer

Answer policy:

- only answer from retrieved context
- cite the supporting sources
- when context is weak, say `I don't know based on the available documentation`

## 8. Confidence and Hallucination Control

This is a product-critical subsystem.

Signals used for confidence:

- top similarity score
- average similarity of top-k chunks
- keyword overlap
- retrieval diversity
- answer groundedness self-check
- explicit LLM confidence classification

Decision policy:

- high confidence:
  - answer normally with sources
- medium confidence:
  - answer cautiously and mention uncertainty
- low confidence:
  - do not speculate
  - return fallback answer
  - trigger escalation if intent/rules match

Low-confidence fallback:

`I don't know based on the documentation currently available. I've flagged this for follow-up if you'd like a human team member to help.`

## 9. Intent Detection and Escalation

Intent classes:

- refund
- complaint
- urgent
- sales
- technical_support
- billing
- general

Escalation triggers:

- low retrieval confidence
- explicit user frustration
- sensitive request such as refund or complaint
- urgent wording
- high-value sales intent

Routing examples:

- refund -> `billing@company.com`
- complaint -> `support@company.com`
- urgent -> `priority@company.com`
- sales -> `sales@company.com`

Email payload:

- organization
- bot
- session id
- detected intent
- confidence status
- user message
- full chat transcript
- top retrieved sources
- timestamp

## 10. Admin Dashboard Features

### Documents

- upload PDFs
- add website URLs
- paste text manually
- processing status
- delete or reindex

### Conversations

- list sessions
- inspect transcript
- filter escalated chats
- export logs

### Analytics

- top questions
- unanswered questions
- escalation counts
- document coverage gaps
- daily message volume

### Settings

- brand colors and widget text
- allowed domains
- escalation routing emails
- model and confidence thresholds

## 11. Frontend Widget Design

The widget should be:

- script-embeddable
- isolated from host CSS via scoped styles or shadow DOM strategy
- mobile responsive
- fast to load
- brandable per bot

UI features:

- launcher button
- welcome state
- message list
- typing indicator
- citations under answers
- escalation acknowledgment state
- restart conversation action

Recommended embed model:

1. Host site adds:

```html
<script src="https://cdn.example.com/widget.js" data-bot-key="pk_live_xxx"></script>
```

2. Script mounts widget into an isolated container
3. Widget fetches public bot config from backend

## 12. Security Best Practices

- store admin auth with short-lived JWT + refresh token rotation
- separate public widget token from admin auth
- hash passwords with `bcrypt` or `argon2`
- validate upload MIME types and file sizes
- sanitize crawled HTML
- rate-limit public chat endpoint
- apply CORS restrictions
- encrypt secrets in deployment platform
- audit log admin actions
- avoid logging raw secrets or full private data
- add bot/domain allowlists for widget usage

## 13. Performance Strategy

- async APIs for chat and upload processing
- background workers for ingestion and emails
- cache bot config and popular retrieval metadata
- batch embeddings during ingestion
- paginate chats and analytics
- stream model responses to widget
- use vector namespaces per tenant

## 14. Suggested Folder Structure

```text
ai-chatbot-saas/
  backend/
    app/
      api/
        v1/
          routes/
      core/
      db/
        models/
        repositories/
      schemas/
      services/
        auth/
        ingestion/
        rag/
        escalation/
        email/
        analytics/
      workers/
      utils/
      main.py
    alembic/
    tests/
    requirements/
    .env.example
    Dockerfile
  frontend/
    admin-dashboard/
      src/
        components/
        pages/
        hooks/
        api/
        styles/
    chat-widget/
      src/
        components/
        hooks/
        api/
        styles/
    package.json
  infra/
    docker/
    nginx/
    terraform/
  docs/
    ARCHITECTURE.md
    API.md
    DEPLOYMENT.md
```

## 15. Deployment Topology

### Local/dev

- FastAPI app
- PostgreSQL
- Redis
- FAISS storage on disk
- local file storage

### Production

- frontend on Vercel/Netlify or CDN
- backend on AWS ECS, Render, Railway, or Kubernetes
- PostgreSQL on managed service
- Redis on managed service
- S3 for uploads
- Pinecone optional for vector search
- SMTP provider or transactional email platform

## 16. Build Sequence

### Step 1

Architecture and overview

### Step 2

Generate backend step by step:

1. backend skeleton
2. config/auth/database
3. document ingestion
4. vector store and embeddings
5. chat and RAG pipeline
6. confidence and escalation
7. analytics and admin APIs

### Step 3

Generate frontend widget and admin dashboard:

1. widget shell
2. chat experience
3. citations and escalation UI
4. admin auth and layout
5. document management and analytics

### Step 4

Integrate everything:

1. environment wiring
2. end-to-end flows
3. local docker setup
4. deployment docs

## 17. Recommended MVP Scope

For the first production-ready version, I recommend:

- FastAPI backend
- PostgreSQL
- Redis
- FAISS default
- local file storage in dev, S3 in prod
- React widget
- React admin dashboard
- OpenAI embeddings + chat generation
- SMTP email adapter

This keeps the system deployable quickly while preserving clean upgrade paths to Pinecone, managed queues, and richer analytics later.
