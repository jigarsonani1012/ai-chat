# Deployment Guide

## 1. Local development

### Backend

1. Copy `backend/.env.example` to `backend/.env`
2. Start infrastructure:

```bash
cd backend
docker compose up -d postgres redis mailhog
```

3. Install Python dependencies and run migrations:

```bash
pip install -r requirements/base.txt
alembic upgrade head
```

4. Start the API:

```bash
uvicorn app.main:app --reload
```

5. Start the worker:

```bash
dramatiq app.workers.actors
```

### Frontend

1. Copy:
   - `frontend/admin-dashboard/.env.example` to `frontend/admin-dashboard/.env`
   - `frontend/chat-widget/.env.example` to `frontend/chat-widget/.env`
2. Install packages:

```bash
cd frontend
npm install
```

3. Start both apps:

```bash
npm run dev:admin
npm run dev:widget
```

Admin dashboard:

`http://localhost:5174`

Widget preview:

`http://localhost:5173`

## 2. Script embed

Build the widget bundle and publish `frontend/chat-widget/dist/widget.js` to your CDN.

Then embed it like this:

```html
<script
  src="https://cdn.example.com/widget.js"
  data-api-base="https://api.example.com/api/v1"
  data-bot-key="pk_live_xxx"
></script>
```

## 3. Production services

- Backend API: Render, Railway, ECS, or Kubernetes
- Worker: separate long-running process using the same image and env
- Database: managed PostgreSQL
- Cache/queue: managed Redis
- Files: local in dev, S3-compatible storage in prod
- Email: SMTP or provider credentials in env

## 4. Security checklist

- replace `SECRET_KEY`
- lock down CORS origins
- use managed Postgres and Redis credentials
- set a real SMTP provider
- keep `OPENAI_API_KEY` in platform secrets
- publish the widget from HTTPS only
- restrict allowed host domains at the reverse proxy or app layer
