import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "./api/client";
import { AuthPanel } from "./components/AuthPanel";
import { BotHeader } from "./components/BotHeader";
import { ConversationsPanel } from "./components/ConversationsPanel";
import { DocumentsPanel } from "./components/DocumentsPanel";
import { OverviewPanel } from "./components/OverviewPanel";
import { SettingsPanel } from "./components/SettingsPanel";
import { Sidebar } from "./components/Sidebar";
import { useAuth } from "./hooks/useAuth";
import type { AnalyticsOverview, Bot, ConversationDetail, ConversationSummary, DocumentRecord } from "./types";

type View = "overview" | "documents" | "conversations" | "settings";

export function App() {
  const { auth, login, signup, logout } = useAuth();
  const [activeView, setActiveView] = useState<View>("overview");
  const [bot, setBot] = useState<Bot | null>(null);
  const [selectedConversation, setSelectedConversation] = useState<ConversationDetail | null>(null);

  const botsQuery = useQuery({
    queryKey: ["bots", auth?.access_token],
    queryFn: () => apiRequest<Bot[]>("/bots/", { token: auth?.access_token }),
    enabled: Boolean(auth?.access_token),
  });

  useEffect(() => {
    if (botsQuery.data?.length) {
      setBot(botsQuery.data[0]);
    }
  }, [botsQuery.data]);

  const analyticsQuery = useQuery({
    queryKey: ["analytics", auth?.access_token],
    queryFn: () => apiRequest<AnalyticsOverview>("/analytics/overview", { token: auth?.access_token }),
    enabled: Boolean(auth?.access_token),
  });

  const conversationsQuery = useQuery({
    queryKey: ["conversations", auth?.access_token],
    queryFn: () => apiRequest<ConversationSummary[]>("/conversations/", { token: auth?.access_token }),
    enabled: Boolean(auth?.access_token),
  });

  const documentsQuery = useQuery({
    queryKey: ["documents", auth?.access_token, bot?.id],
    queryFn: () =>
      apiRequest<DocumentRecord[]>(`/documents/${bot ? `?bot_id=${encodeURIComponent(bot.id)}` : ""}`, {
        token: auth?.access_token,
      }),
    enabled: Boolean(auth?.access_token && bot?.id),
  });

  async function loadConversation(sessionId: string) {
    if (!auth?.access_token) {
      return;
    }
    const detail = await apiRequest<ConversationDetail>(`/conversations/${sessionId}`, {
      token: auth.access_token,
    });
    setSelectedConversation(detail);
  }

  if (!auth) {
    return <AuthPanel onLogin={login} onSignup={signup} />;
  }

  return (
    <div className="dashboard-shell">
      <Sidebar active={activeView} onChange={setActiveView} />
      <main className="dashboard-main">
        <BotHeader auth={auth} bot={bot} onLogout={logout} />

        {activeView === "overview" ? <OverviewPanel bot={bot} analytics={analyticsQuery.data} /> : null}
        {activeView === "documents" ? (
          <DocumentsPanel token={auth.access_token} bot={bot} documents={documentsQuery.data ?? []} />
        ) : null}
        {activeView === "conversations" ? (
          <ConversationsPanel
            conversations={conversationsQuery.data ?? []}
            selected={selectedConversation}
            onSelect={loadConversation}
          />
        ) : null}
        {activeView === "settings" ? (
          <SettingsPanel
            token={auth.access_token}
            bot={bot}
            onCreated={(created) => {
              setBot(created);
              setActiveView("overview");
            }}
          />
        ) : null}
      </main>
    </div>
  );
}
