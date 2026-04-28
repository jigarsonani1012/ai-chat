import type { AnalyticsOverview, Bot } from "../types";

type Props = {
  bot: Bot | null;
  analytics?: AnalyticsOverview;
};

export function OverviewPanel({ bot, analytics }: Props) {
  return (
    <section className="panel-grid">
      <div className="hero-panel">
        <div>
          <span className="eyebrow">Live widget key</span>
          <h2>{bot ? bot.public_key : "No bot yet"}</h2>
        </div>
        <p>Embed the widget script with this public key and route customer questions into your knowledge base.</p>
      </div>

      <div className="stats-grid">
        <article className="stat-card">
          <span>Total sessions</span>
          <strong>{analytics?.total_sessions ?? 0}</strong>
        </article>
        <article className="stat-card">
          <span>Total messages</span>
          <strong>{analytics?.total_messages ?? 0}</strong>
        </article>
        <article className="stat-card">
          <span>Escalations</span>
          <strong>{analytics?.escalations ?? 0}</strong>
        </article>
        <article className="stat-card">
          <span>Unanswered</span>
          <strong>{analytics?.unanswered_questions ?? 0}</strong>
        </article>
      </div>

      <div className="content-card">
        <h3>Top questions</h3>
        <ul className="simple-list">
          {(analytics?.top_questions ?? []).map((question) => (
            <li key={question}>{question}</li>
          ))}
        </ul>
      </div>

      <div className="content-card code-card">
        <h3>Embed snippet</h3>
        <pre>{`<script
  src="https://cdn.example.com/widget.js"
  data-api-base="https://api.example.com/api/v1"
  data-bot-key="${bot?.public_key ?? "pk_live_xxx"}"
></script>`}</pre>
      </div>
    </section>
  );
}
