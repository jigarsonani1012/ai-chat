import { useState } from "react";
import { apiRequest } from "../api/client";
import type { Bot } from "../types";

type Props = {
  token: string;
  bot: Bot | null;
  onCreated: (bot: Bot) => void;
};

export function SettingsPanel({ token, bot, onCreated }: Props) {
  const [name, setName] = useState(bot?.name ?? "Support Copilot");
  const [welcomeMessage, setWelcomeMessage] = useState(
    bot?.welcome_message ?? "Hi, how can I help you today using the available documentation?",
  );
  const [primaryColor, setPrimaryColor] = useState(bot?.primary_color ?? "#14532d");
  const [status, setStatus] = useState("");

  async function saveBot() {
    setStatus("Saving bot...");
    const path = bot ? `/bots/${bot.id}` : "/bots/";
    const method = bot ? "PATCH" : "POST";
    const saved = await apiRequest<Bot>(path, {
      method,
      token,
      body: JSON.stringify({
        name,
        welcome_message: welcomeMessage,
        primary_color: primaryColor,
      }),
    });
    onCreated(saved);
    setStatus(bot ? "Bot updated." : "Bot created.");
  }

  return (
    <section className="panel-grid">
      <div className="content-card content-card-wide">
        <h3>Bot settings</h3>
        <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Bot name" />
        <textarea value={welcomeMessage} onChange={(event) => setWelcomeMessage(event.target.value)} rows={4} />
        <div className="color-row">
          <input type="color" value={primaryColor} onChange={(event) => setPrimaryColor(event.target.value)} />
          <input value={primaryColor} onChange={(event) => setPrimaryColor(event.target.value)} />
        </div>
        <button className="primary-button" onClick={saveBot}>
          {bot ? "Save changes" : "Create bot"}
        </button>
        {status ? <p className="status-text">{status}</p> : null}
      </div>
    </section>
  );
}
