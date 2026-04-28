import type { AuthState, Bot } from "../types";

type Props = {
  auth: AuthState;
  bot: Bot | null;
  onLogout: () => void;
};

export function BotHeader({ auth, bot, onLogout }: Props) {
  return (
    <header className="topbar">
      <div>
        <span className="eyebrow">Workspace</span>
        <h1>{bot ? bot.name : "Create your first bot"}</h1>
      </div>
      <div className="topbar-actions">
        <div className="user-chip">
          <strong>{auth.user.full_name}</strong>
          <span>{auth.user.email}</span>
        </div>
        <button className="ghost-button" onClick={onLogout}>
          Log out
        </button>
      </div>
    </header>
  );
}
