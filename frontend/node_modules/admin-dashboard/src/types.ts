export type AuthUser = {
  id: string;
  organization_id: string;
  full_name: string;
  email: string;
};

export type AuthState = {
  access_token: string;
  token_type: string;
  user: AuthUser;
};

export type Bot = {
  id: string;
  organization_id: string;
  name: string;
  public_key: string;
  welcome_message: string;
  primary_color: string;
  escalation_emails: Record<string, string>;
};

export type ConversationSummary = {
  session_id: string;
  bot_id: string;
  created_at: string;
  user_identifier?: string | null;
  message_count: number;
  last_message?: string | null;
};

export type MessageRead = {
  id: string;
  role: string;
  content: string;
  created_at: string;
  source_json?: string | null;
};

export type ConversationDetail = {
  session_id: string;
  messages: MessageRead[];
};

export type AnalyticsOverview = {
  total_sessions: number;
  total_messages: number;
  escalations: number;
  unanswered_questions: number;
  top_questions: string[];
};

export type DocumentRecord = {
  id: string;
  organization_id: string;
  bot_id: string;
  source_type: string;
  source_name: string;
  source_url?: string | null;
  status: string;
  created_at: string;
};
