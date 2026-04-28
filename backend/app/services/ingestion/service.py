from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.bot import Bot
from app.db.models.document import Document, DocumentChunk
from app.schemas.document import DocumentTextCreate, DocumentUrlCreate
from app.services.ingestion.chunker import chunk_text
from app.services.ingestion.parsers import extract_pdf_text, extract_url_text
from app.services.rag.embeddings import embed_texts
from app.services.rag.vector_store import FaissVectorStore
from app.services.tasks import TaskDispatcher


class IngestionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.task_dispatcher = TaskDispatcher()

    async def ingest_upload(self, bot: Bot, upload: UploadFile) -> Document:
        suffix = Path(upload.filename or "upload.pdf").suffix or ".pdf"
        file_name = f"{uuid4()}{suffix}"
        destination = settings.upload_dir / file_name
        content = await upload.read()
        destination.write_bytes(content)

        text = extract_pdf_text(destination)
        return self._persist_document(
            bot=bot,
            source_type="pdf",
            source_name=upload.filename or file_name,
            source_url=None,
            file_path=str(destination),
            text=text,
        )

    def ingest_url(self, bot: Bot, payload: DocumentUrlCreate) -> Document:
        document = Document(
            organization_id=bot.organization_id,
            bot_id=bot.id,
            source_type="url",
            source_name=str(payload.url),
            source_url=str(payload.url),
            file_path=None,
            status="queued",
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        self.task_dispatcher.dispatch_ingest_url(document.id)
        return document

    def process_url_document(self, document: Document) -> Document:
        bot = document.bot
        if not bot:
            raise ValueError("Document bot not found")
        text = extract_url_text(document.source_url or "")
        return self._persist_existing_document(bot=bot, document=document, text=text)

    def ingest_text(self, bot: Bot, payload: DocumentTextCreate) -> Document:
        return self._persist_document(
            bot=bot,
            source_type="text",
            source_name=payload.title,
            source_url=None,
            file_path=None,
            text=payload.content,
        )

    def _persist_document(
        self,
        bot: Bot,
        source_type: str,
        source_name: str,
        source_url: str | None,
        file_path: str | None,
        text: str,
    ) -> Document:
        document = Document(
            organization_id=bot.organization_id,
            bot_id=bot.id,
            source_type=source_type,
            source_name=source_name,
            source_url=source_url,
            file_path=file_path,
            status="processing",
        )
        self.db.add(document)
        self.db.flush()
        return self._persist_existing_document(bot=bot, document=document, text=text)

    def _persist_existing_document(self, bot: Bot, document: Document, text: str) -> Document:
        document.status = "processing"
        chunks = chunk_text(text)
        vectors = embed_texts(chunks) if chunks else []
        vector_metadata: list[dict] = []

        for idx, chunk in enumerate(chunks):
            record = DocumentChunk(
                organization_id=bot.organization_id,
                bot_id=bot.id,
                document_id=document.id,
                chunk_index=idx,
                content=chunk,
                source_name=document.source_name,
                source_url=document.source_url,
            )
            self.db.add(record)
            self.db.flush()
            vector_metadata.append(
                {
                    "chunk_id": record.id,
                    "document_id": document.id,
                    "source_name": document.source_name,
                    "source_url": document.source_url,
                    "content": chunk,
                }
            )

        if vector_metadata:
            FaissVectorStore(bot.id).upsert(vectors=vectors, metadata=vector_metadata)

        document.status = "ready"
        self.db.commit()
        self.db.refresh(document)
        return document
