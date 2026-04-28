import type { ConversationDetail, ConversationSummary } from "../types";

type Props = {
  conversations: ConversationSummary[];
  selected: ConversationDetail | null;
  onSelect: (sessionId: string) => void;
};

export function ConversationsPanel({ conversations, selected, onSelect }: Props) {
  return (
    <section className="split-layout">
      <div className="content-card">
        <h3>Sessions</h3>
        <div className="conversation-list">
          {conversations.map((conversation) => (
            <button key={conversation.session_id} className="conversation-row" onClick={() => onSelect(conversation.session_id)}>
              <strong>{conversation.user_identifier || "Anonymous visitor"}</strong>
              <span>{conversation.last_message || "No messages yet"}</span>
              <small>{conversation.message_count} messages</small>
            </button>
          ))}
        </div>
      </div>

      <div className="content-card">
        <h3>Transcript</h3>
        <div className="transcript">
          {(selected?.messages ?? []).map((message) => (
            <article key={message.id} className={`message-bubble ${message.role}`}>
              <span>{message.role}</span>
              <p>{message.content}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
