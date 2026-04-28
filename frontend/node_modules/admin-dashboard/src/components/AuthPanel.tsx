import { useState, type FormEvent } from "react";

type Props = {
  onLogin: (email: string, password: string) => Promise<void>;
  onSignup: (organizationName: string, fullName: string, email: string, password: string) => Promise<void>;
};

export function AuthPanel({ onLogin, onSignup }: Props) {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [organizationName, setOrganizationName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      if (mode === "login") {
        await onLogin(email, password);
      } else {
        await onSignup(organizationName, fullName, email, password);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div className="auth-copy">
          <span className="eyebrow">AI Chatbot SaaS</span>
          <h1>Run support and sales AI from one control room.</h1>
          <p>Upload docs, monitor conversations, and route sensitive issues before they become expensive.</p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="segmented">
            <button type="button" className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>
              Login
            </button>
            <button type="button" className={mode === "signup" ? "active" : ""} onClick={() => setMode("signup")}>
              Sign up
            </button>
          </div>

          {mode === "signup" ? (
            <>
              <input placeholder="Organization name" value={organizationName} onChange={(e) => setOrganizationName(e.target.value)} required />
              <input placeholder="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
            </>
          ) : null}

          <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          {error ? <p className="error-text">{error}</p> : null}
          <button className="primary-button" disabled={loading} type="submit">
            {loading ? "Working..." : mode === "login" ? "Access dashboard" : "Create workspace"}
          </button>
        </form>
      </div>
    </div>
  );
}
