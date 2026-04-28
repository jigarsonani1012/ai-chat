import React from "react";
import ReactDOM from "react-dom/client";
import { ChatWidget } from "./ChatWidget";
import "./widget.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ChatWidget
      apiBase={import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1"}
      botKey={import.meta.env.VITE_BOT_PUBLIC_KEY ?? "pk_demo_placeholder"}
    />
  </React.StrictMode>,
);
