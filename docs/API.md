# API Overview

Base URL in development:

`http://localhost:8000/api/v1`

## Auth

- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`

## Bots

- `POST /bots/`
- `GET /bots/`
- `PATCH /bots/{bot_id}`
- `GET /bots/public/{public_key}`

## Documents

- `GET /documents/?bot_id={bot_id}`
- `POST /documents/upload`
- `POST /documents/url`
- `POST /documents/text`

## Chat

- `POST /chat/ask`

## Admin insights

- `GET /conversations/`
- `GET /conversations/{session_id}`
- `GET /analytics/overview`
