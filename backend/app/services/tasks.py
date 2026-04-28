from app.core.config import settings


class TaskDispatcher:
    def dispatch_ingest_url(self, document_id: str) -> None:
        from app.workers.actors import ingest_url_actor

        if settings.enable_sync_task_fallback:
            ingest_url_actor.fn(document_id)
            return
        ingest_url_actor.send(document_id)

    def dispatch_escalation_email(self, escalation_event_id: str) -> None:
        from app.workers.actors import deliver_escalation_email_actor

        if settings.enable_sync_task_fallback:
            deliver_escalation_email_actor.fn(escalation_event_id)
            return
        deliver_escalation_email_actor.send(escalation_event_id)
