export type BotPublicConfig = {
  id: string;
  name: string;
  public_key: string;
  welcome_message: string;
  primary_color: string;
};

export type SourceItem = {
  document_id: string;
  source_name: string;
  source_url?: string | null;
  excerpt: string;
  score: number;
};

export type ChatResponse = {
  session_id: string;
  answer: string;
  sources: SourceItem[];
  confidence: string;
  escalation_triggered: boolean;
  escalation_intent?: string | null;
};

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  sources?: SourceItem[];
  confidence?: string;
  escalationTriggered?: boolean;
};
