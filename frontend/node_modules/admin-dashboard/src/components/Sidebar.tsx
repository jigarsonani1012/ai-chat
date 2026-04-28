import { BarChart3, Bot, FileText, MessagesSquare, Settings } from "lucide-react";

type View = "overview" | "documents" | "conversations" | "settings";

type Props = {
  active: View;
  onChange: (view: View) => void;
};

const items: Array<{ id: View; label: string; icon: typeof Bot }> = [
  { id: "overview", label: "Overview", icon: BarChart3 },
  { id: "documents", label: "Documents", icon: FileText },
  { id: "conversations", label: "Conversations", icon: MessagesSquare },
  { id: "settings", label: "Settings", icon: Settings },
];

export function Sidebar({ active, onChange }: Props) {
  return (
    <aside className="sidebar">
      <div className="brand-block">
        <div className="brand-badge">AI</div>
        <div>
          <h2>Operator Console</h2>
          <p>Chatbot control plane</p>
        </div>
      </div>
      <nav className="nav-list">
        {items.map((item) => {
          const Icon = item.icon;
          return (
            <button key={item.id} className={`nav-item ${active === item.id ? "selected" : ""}`} onClick={() => onChange(item.id)}>
              <Icon size={16} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
