import json
import re
from typing import Any

from openai import APIConnectionError, APIError, AuthenticationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.bot import Bot
from app.db.models.chat import ChatMessage, ChatSession
from app.db.models.document import DocumentChunk
from app.schemas.chat import ChatRequest, ChatResponse, SourceItem
from app.services.analytics import AnalyticsService
from app.services.escalation.service import EscalationService
from app.services.rag.embeddings import embed_query
from app.services.rag.openai_client import client
from app.services.rag.vector_store import FaissVectorStore


class ChatService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.analytics = AnalyticsService(db)

    def answer_question(self, payload: ChatRequest) -> ChatResponse:
        bot = self.db.query(Bot).filter(Bot.public_key == payload.public_bot_key).first()
        if not bot:
            raise ValueError("Invalid bot key")

        session = self._get_or_create_session(bot=bot, payload=payload)
        smalltalk_answer = self._smalltalk_answer(bot, payload.message)
        if smalltalk_answer:
            self._store_message(session.id, "user", payload.message)
            self._store_message(session.id, "assistant", smalltalk_answer, sources=[])
            self.db.commit()
            return ChatResponse(
                session_id=session.id,
                answer=smalltalk_answer,
                sources=[],
                confidence="high",
                escalation_triggered=False,
                escalation_intent=None,
            )

        retrieved = self._retrieve_context(bot.id, payload.message)
        confidence = self._classify_confidence(retrieved)
        intent = self._detect_intent(payload.message)

        sources = [
            SourceItem(
                document_id=item["document_id"],
                source_name=item["source_name"],
                source_url=item.get("source_url"),
                excerpt=item["content"][:220],
                score=item["score"],
            )
            for item in retrieved
        ]

        if confidence == "low":
            answer = self._fallback_answer(bot, payload.message, payload.history)
            self.analytics.track_event(
                organization_id=bot.organization_id,
                bot_id=bot.id,
                session_id=session.id,
                event_type="unanswered_question",
                message_text=payload.message,
                confidence=confidence,
                metadata={"intent": intent},
            )
            escalation_triggered = EscalationService(self.db).maybe_escalate(
                bot=bot,
                session_id=session.id,
                intent=intent,
                reason="low_confidence",
                transcript=self._build_transcript(payload.history, payload.message, answer),
                sources=[item.model_dump() for item in sources],
            )
        else:
            answer = self._generate_answer(payload.message, retrieved)
            escalation_triggered = EscalationService(self.db).maybe_escalate(
                bot=bot,
                session_id=session.id,
                intent=intent,
                reason="intent_match",
                transcript=self._build_transcript(payload.history, payload.message, answer),
                sources=[item.model_dump() for item in sources],
            )

        self.analytics.track_event(
            organization_id=bot.organization_id,
            bot_id=bot.id,
            session_id=session.id,
            event_type="question_asked",
            message_text=payload.message,
            confidence=confidence,
            metadata={"intent": intent, "source_count": len(sources)},
        )
        if escalation_triggered:
            self.analytics.track_event(
                organization_id=bot.organization_id,
                bot_id=bot.id,
                session_id=session.id,
                event_type="escalation_triggered",
                message_text=payload.message,
                confidence=confidence,
                metadata={"intent": intent},
            )

        self._store_message(session.id, "user", payload.message)
        self._store_message(session.id, "assistant", answer, sources=[item.model_dump() for item in sources])
        self.db.commit()

        return ChatResponse(
            session_id=session.id,
            answer=answer,
            sources=sources,
            confidence=confidence,
            escalation_triggered=escalation_triggered,
            escalation_intent=intent if escalation_triggered else None,
        )

    def _get_or_create_session(self, bot: Bot, payload: ChatRequest) -> ChatSession:
        if payload.session_id:
            existing = self.db.query(ChatSession).filter(ChatSession.id == payload.session_id).first()
            if existing:
                return existing

        session = ChatSession(
            organization_id=bot.organization_id,
            bot_id=bot.id,
            user_identifier=payload.user_identifier,
        )
        self.db.add(session)
        self.db.flush()
        return session

    def _generate_answer(self, question: str, retrieved: list[dict[str, Any]]) -> str:
        if not settings.openai_api_key:
            return self._extractive_answer(question, retrieved) or self._fallback_no_ai_answer()
        context = "\n\n".join(
            [f"Source: {item['source_name']}\nContent: {item['content']}" for item in retrieved]
        )
        system_prompt = (
            "You are a support AI assistant. Use the provided documentation context as your primary source. "
            "Answer clearly and accurately. If the user is making simple conversation, you can respond naturally. "
            "If they ask for details that are not supported by the context, say that the documentation does not "
            "confirm it instead of inventing facts."
        )
        try:
            response = client.responses.create(
                model=settings.openai_chat_model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Question: {question}\n\nContext:\n{context}",
                    },
                ],
            )
            return response.output_text.strip()
        except (APIConnectionError, APIError, AuthenticationError):
            return self._extractive_answer(question, retrieved) or self._fallback_no_ai_answer()

    def _generate_general_answer(self, bot: Bot, question: str, history: list[Any]) -> str | None:
        if not settings.openai_api_key:
            return None

        history_lines = [
            f"{item.role.capitalize()}: {item.content.strip()}"
            for item in history[-6:]
            if getattr(item, "content", "").strip()
        ]
        history_block = "\n".join(history_lines)

        system_prompt = (
            f"You are {bot.name}, a friendly AI assistant embedded on a website. "
            "You can answer greetings, basic conversational questions, and simple general-help requests. "
            "Keep replies short, warm, and practical. Do not claim product or company facts unless the user "
            "provided them or they came from documentation context."
        )
        user_prompt = f"Conversation so far:\n{history_block or 'No prior conversation.'}\n\nUser: {question}"

        try:
            response = client.responses.create(
                model=settings.openai_chat_model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            answer = response.output_text.strip()
            return answer or None
        except (APIConnectionError, APIError, AuthenticationError):
            return None

    def _detect_intent(self, message: str) -> str:
        lowered = message.lower()
        if any(word in lowered for word in ["refund", "money back", "chargeback"]):
            return "refund"
        if any(word in lowered for word in ["complaint", "angry", "upset", "bad service"]):
            return "complaint"
        if any(word in lowered for word in ["urgent", "asap", "immediately", "critical"]):
            return "urgent"
        if any(word in lowered for word in ["pricing", "demo", "buy", "enterprise", "sales"]):
            return "sales"
        if any(word in lowered for word in ["invoice", "billing", "payment"]):
            return "billing"
        return "general"

    def _classify_confidence(self, retrieved: list[dict]) -> str:
        if not retrieved:
            return "low"
        top_score = retrieved[0]["score"]
        if top_score >= 0.78:
            return "high"
        if top_score >= 0.62:
            return "medium"
        return "low"

    def _build_transcript(self, history: list, user_message: str, answer: str) -> list[dict]:
        transcript = [{"role": item.role, "content": item.content} for item in history]
        transcript.append({"role": "user", "content": user_message})
        transcript.append({"role": "assistant", "content": answer})
        return transcript

    def _store_message(self, session_id: str, role: str, content: str, sources: list[dict] | None = None) -> None:
        self.db.add(
            ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
                source_json=json.dumps(sources or []),
            )
        )

    def _retrieve_context(self, bot_id: str, message: str) -> list[dict]:
        query_vector = embed_query(message)
        if query_vector:
            retrieved = FaissVectorStore(bot_id).search(query_vector, limit=5)
            if retrieved:
                return retrieved
        return self._keyword_search_context(bot_id, message)

    def _fallback_answer(self, bot: Bot, message: str, history: list[Any]) -> str:
        general_answer = self._generate_general_answer(bot, message, history)
        if general_answer:
            return general_answer

        lowered = message.lower()
        if any(phrase in lowered for phrase in ["what is this", "who are you", "what do you do", "what is this project"]):
            return (
                f"This is {bot.name}, a documentation assistant for your website. "
                "It can answer questions from uploaded docs, cite sources, and escalate sensitive requests."
            )
        return self._fallback_no_ai_answer(bot)

    def _fallback_no_ai_answer(self, bot: Bot | None = None) -> str:
        assistant_name = bot.name if bot else "this assistant"
        return (
            f"I can help with greetings and simple conversation, but {assistant_name} needs an OpenAI API key "
            "for richer answers. Upload documents as well if you want documentation-based support with citations."
        )

    def _keyword_search_context(self, bot_id: str, message: str) -> list[dict[str, Any]]:
        terms = self._keyword_terms(message)
        if not terms:
            return []

        chunks = (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.bot_id == bot_id)
            .order_by(DocumentChunk.created_at.desc())
            .all()
        )

        scored: list[dict[str, Any]] = []
        for chunk in chunks:
            content = chunk.content or ""
            lowered = content.lower()
            overlap = sum(1 for term in terms if term in lowered)
            if overlap == 0:
                continue

            score = min(0.95, overlap / max(len(terms), 1))
            if " ".join(terms) in lowered:
                score = min(0.99, score + 0.15)

            scored.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "source_name": chunk.source_name,
                    "source_url": chunk.source_url,
                    "content": content,
                    "score": score,
                }
            )

        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:5]

    def _keyword_terms(self, message: str) -> list[str]:
        stopwords = {
            "the",
            "and",
            "for",
            "with",
            "that",
            "this",
            "from",
            "have",
            "your",
            "about",
            "what",
            "when",
            "where",
            "which",
            "how",
            "can",
            "are",
            "you",
            "into",
            "does",
            "show",
            "tell",
        }
        terms = re.findall(r"[a-z0-9]{3,}", message.lower())
        unique_terms: list[str] = []
        for term in terms:
            if term in stopwords or term in unique_terms:
                continue
            unique_terms.append(term)
        return unique_terms[:10]

    def _extractive_answer(self, question: str, retrieved: list[dict[str, Any]]) -> str | None:
        if not retrieved:
            return None

        terms = self._keyword_terms(question)
        snippets: list[str] = []
        seen_sources: set[str] = set()

        for item in retrieved:
            content = self._clean_document_text(item["content"])
            source_name = item["source_name"]
            if source_name not in seen_sources:
                seen_sources.add(source_name)

            matched_sentences = [
                sentence.strip()
                for sentence in re.split(r"(?<=[.!?])\s+", content)
                if not terms or any(term in sentence.lower() for term in terms)
            ]
            snippet = matched_sentences[0] if matched_sentences else content[:260].strip()
            if snippet and snippet not in snippets:
                snippets.append(snippet)
            if len(snippets) == 2:
                break

        if not snippets:
            return None

        source_list = ", ".join(list(seen_sources)[:2])
        if len(snippets) == 1:
            return f"Based on the documentation, {snippets[0]} Source: {source_list}."

        return f"Based on the documentation, {snippets[0]} {snippets[1]} Sources: {source_list}."

    def _clean_document_text(self, content: str) -> str:
        text = re.sub(r"#+\s*", "", content)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _smalltalk_answer(self, bot: Bot, message: str) -> str | None:
        normalized = re.sub(r"[^a-z0-9\s']", " ", message.lower()).strip()
        compact = " ".join(normalized.split())
        if not compact:
            return "I am here whenever you are. Ask me something about the docs or just say hello."

        if compact in {"hi", "hello", "hey", "hii", "helo", "yo"} or compact.startswith(("hi ", "hello ", "hey ")):
            return (
                f"Hello! I am {bot.name}. I can help with uploaded documentation, and I can also handle simple questions."
            )
        if any(phrase in compact for phrase in ["how are you", "how r you", "how do you do"]):
            return "I am doing well and ready to help. You can ask me about the docs or any simple question."
        if any(phrase in compact for phrase in ["thank you", "thanks", "thx"]):
            return "You are welcome. Keep the questions coming."
        if compact in {"bye", "goodbye", "see you", "cya"}:
            return "Bye for now. I will be here when you need me again."
        if compact in {"who are you", "what are you", "what can you do", "help"}:
            return (
                f"I am {bot.name}. I answer questions from uploaded documentation, and I can also reply to simple chat "
                "like greetings, help requests, and basic conversation."
            )
        return None
