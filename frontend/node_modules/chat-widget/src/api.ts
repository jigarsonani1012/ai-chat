import type { BotPublicConfig, ChatResponse, ChatMessage } from "./types";

export async function fetchBotConfig(apiBase: string, botKey: string): Promise<BotPublicConfig> {
  const response = await fetch(`${apiBase}/bots/public/${botKey}`);
  if (!response.ok) {
    throw new Error("Unable to load bot configuration");
  }
  return response.json();
}

export async function askQuestion(
  apiBase: string,
  botKey: string,
  message: string,
  sessionId: string | null,
  history: ChatMessage[],
): Promise<ChatResponse> {
  const response = await fetch(`${apiBase}/chat/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      public_bot_key: botKey,
      message,
      session_id: sessionId,
      history: history.map((item) => ({ role: item.role, content: item.content })),
    }),
  });

  if (!response.ok) {
    throw new Error("Unable to send message");
  }

  return response.json();
}
