import { LoaderCircle, MessageSquareText, RefreshCcw, SendHorizontal } from "lucide-react";
import { useEffect, useMemo, useRef, useState, type CSSProperties } from "react";
import { askQuestion, fetchBotConfig } from "./api";
import type { BotPublicConfig, ChatMessage } from "./types";

type Props = {
  apiBase: string;
  botKey: string;
};

export function ChatWidget({ apiBase, botKey }: Props) {
  const [open, setOpen] = useState(false);
  const [loadingConfig, setLoadingConfig] = useState(true);
  const [bot, setBot] = useState<BotPublicConfig | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const transcriptRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let active = true;
    fetchBotConfig(apiBase, botKey)
      .then((config) => {
        if (!active) {
          return;
        }
        setBot(config);
        setMessages([{ role: "assistant", content: config.welcome_message }]);
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof Error ? err.message : "Failed to load widget");
        }
      })
      .finally(() => {
        if (active) {
          setLoadingConfig(false);
        }
      });

    return () => {
      active = false;
    };
  }, [apiBase, botKey]);

  useEffect(() => {
    transcriptRef.current?.scrollTo({ top: transcriptRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, sending]);

  const themeStyle = useMemo(
    () =>
      ({
        "--widget-accent": bot?.primary_color ?? "#14532d",
      }) as CSSProperties,
    [bot?.primary_color],
  );

  async function handleSend() {
    if (!input.trim() || sending) {
      return;
    }
    const userMessage = input.trim();
    setInput("");
    setSending(true);
    setError("");
    const history = [...messages, { role: "user" as const, content: userMessage }];
    setMessages(history);

    try {
      const response = await askQuestion(apiBase, botKey, userMessage, sessionId, messages);
      setSessionId(response.session_id);
      setMessages([
        ...history,
        {
          role: "assistant",
          content: response.answer,
          sources: response.sources,
          confidence: response.confidence,
          escalationTriggered: response.escalation_triggered,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Message failed");
    } finally {
      setSending(false);
    }
  }

  function resetConversation() {
    setSessionId(null);
    setMessages(bot ? [{ role: "assistant", content: bot.welcome_message }] : []);
  }

  return (
    <div className="widget-root" style={themeStyle}>
      {open ? (
        <div className="widget-panel">
          <header className="widget-header">
            <div>
              <strong>{bot?.name ?? "Assistant"}</strong>
              <span>Documentation assistant</span>
            </div>
            <div className="widget-header-actions">
              <button className="icon-button" onClick={resetConversation} title="Reset conversation">
                <RefreshCcw size={14} />
              </button>
              <button className="icon-button" onClick={() => setOpen(false)} title="Close">
                <MessageSquareText size={14} />
              </button>
            </div>
          </header>

          <div className="widget-transcript" ref={transcriptRef}>
            {loadingConfig ? (
              <div className="widget-state">
                <LoaderCircle className="spin" size={18} />
                <span>Loading assistant...</span>
              </div>
            ) : null}

            {messages.map((message, index) => (
              <article key={`${message.role}-${index}`} className={`widget-message ${message.role}`}>
                <p>{message.content}</p>
                {message.sources?.length ? (
                  <div className="source-stack">
                    {message.sources.map((source) => (
                      <a
                        key={`${source.document_id}-${source.source_name}`}
                        className="source-chip"
                        href={source.source_url || "#"}
                        target={source.source_url ? "_blank" : undefined}
                        rel="noreferrer"
                      >
                        <strong>{source.source_name}</strong>
                        <span>{source.excerpt}</span>
                      </a>
                    ))}
                  </div>
                ) : null}
                {message.confidence ? <small className="confidence-chip">{message.confidence} confidence</small> : null}
                {message.escalationTriggered ? <small className="escalation-chip">Human follow-up triggered</small> : null}
              </article>
            ))}

            {sending ? (
              <div className="widget-state">
                <LoaderCircle className="spin" size={18} />
                <span>Thinking...</span>
              </div>
            ) : null}
          </div>

          <footer className="widget-footer">
            {error ? <p className="widget-error">{error}</p> : null}
            <div className="composer">
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    void handleSend();
                  }
                }}
                placeholder="Ask about pricing, support, billing..."
              />
              <button className="send-button" onClick={() => void handleSend()} disabled={sending || !input.trim()}>
                <SendHorizontal size={16} />
              </button>
            </div>
          </footer>
        </div>
      ) : null}

      <button className="launcher-button" onClick={() => setOpen((value) => !value)}>
        <MessageSquareText size={18} />
        <span>{open ? "Hide assistant" : "Ask us anything"}</span>
      </button>
    </div>
  );
}
