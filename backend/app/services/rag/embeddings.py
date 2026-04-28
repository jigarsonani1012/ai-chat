from openai import APIConnectionError, APIError, AuthenticationError

from app.core.config import settings
from app.services.rag.openai_client import client


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    if not settings.openai_api_key:
        return []
    try:
        response = client.embeddings.create(model=settings.openai_embedding_model, input=texts)
        return [item.embedding for item in response.data]
    except (APIConnectionError, APIError, AuthenticationError):
        return []


def embed_query(text: str) -> list[float]:
    vectors = embed_texts([text])
    return vectors[0] if vectors else []
