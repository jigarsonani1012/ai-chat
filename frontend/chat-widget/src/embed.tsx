import React from "react";
import ReactDOM from "react-dom/client";
import { ChatWidget } from "./ChatWidget";
import widgetCss from "./widget.css?inline";

declare global {
  interface Window {
    AiChatbotWidget?: {
      mount: (options: { apiBase: string; botKey: string; target?: HTMLElement }) => void;
    };
  }
}

function mount(options: { apiBase: string; botKey: string; target?: HTMLElement }) {
  const target = options.target ?? document.body.appendChild(document.createElement("div"));
  const host = document.createElement("div");
  const root = target.attachShadow ? target.attachShadow({ mode: "open" }) : target;
  const style = document.createElement("style");
  style.textContent = widgetCss;
  root.appendChild(style);
  root.appendChild(host);
  ReactDOM.createRoot(host).render(
    <React.StrictMode>
      <ChatWidget apiBase={options.apiBase} botKey={options.botKey} />
    </React.StrictMode>,
  );
}

window.AiChatbotWidget = { mount };

const currentScript = document.currentScript as HTMLScriptElement | null;
if (currentScript?.dataset.botKey) {
  mount({
    apiBase: currentScript.dataset.apiBase ?? "http://localhost:8000/api/v1",
    botKey: currentScript.dataset.botKey,
  });
}
