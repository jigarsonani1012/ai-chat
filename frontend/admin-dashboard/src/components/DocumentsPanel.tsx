import { useState } from "react";
import { apiRequest } from "../api/client";
import type { Bot, DocumentRecord } from "../types";

type Props = {
  token: string;
  bot: Bot | null;
  documents: DocumentRecord[];
};

export function DocumentsPanel({ token, bot, documents }: Props) {
  const [url, setUrl] = useState("");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState("");

  async function uploadPdf() {
    if (!bot || !file) {
      return;
    }
    const formData = new FormData();
    formData.append("bot_id", bot.id);
    formData.append("file", file);
    setStatus("Uploading PDF...");
    await apiRequest("/documents/upload", { method: "POST", token, body: formData });
    setStatus("PDF queued successfully.");
  }

  async function addUrl() {
    if (!bot || !url) {
      return;
    }
    setStatus("Queueing URL ingestion...");
    await apiRequest("/documents/url", {
      method: "POST",
      token,
      body: JSON.stringify({ bot_id: bot.id, url }),
    });
    setStatus("URL source added.");
  }

  async function addText() {
    if (!bot || !title || !content) {
      return;
    }
    setStatus("Saving text knowledge...");
    await apiRequest("/documents/text", {
      method: "POST",
      token,
      body: JSON.stringify({ bot_id: bot.id, title, content }),
    });
    setStatus("Text knowledge added.");
  }

  return (
    <section className="panel-grid">
      <div className="content-card">
        <h3>PDF upload</h3>
        <input type="file" accept=".pdf" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
        <button className="primary-button" onClick={uploadPdf} disabled={!bot || !file}>
          Upload PDF
        </button>
      </div>

      <div className="content-card">
        <h3>Website URL</h3>
        <input placeholder="https://docs.example.com" value={url} onChange={(event) => setUrl(event.target.value)} />
        <button className="primary-button" onClick={addUrl} disabled={!bot || !url}>
          Import URL
        </button>
      </div>

      <div className="content-card content-card-wide">
        <h3>Manual knowledge</h3>
        <input placeholder="Title" value={title} onChange={(event) => setTitle(event.target.value)} />
        <textarea placeholder="Paste trusted knowledge here" value={content} onChange={(event) => setContent(event.target.value)} rows={8} />
        <button className="primary-button" onClick={addText} disabled={!bot || !title || !content}>
          Save text source
        </button>
      </div>

      <div className="content-card content-card-wide">
        <h3>Indexed sources</h3>
        <div className="document-list">
          {documents.map((document) => (
            <article key={document.id} className="document-row">
              <div>
                <strong>{document.source_name}</strong>
                <span>{document.source_type.toUpperCase()}</span>
              </div>
              <div>
                <small>{new Date(document.created_at).toLocaleString()}</small>
                <span className={`status-badge ${document.status}`}>{document.status}</span>
              </div>
            </article>
          ))}
          {!documents.length ? <p className="status-text">No documents indexed yet.</p> : null}
        </div>
      </div>

      {status ? <p className="status-text">{status}</p> : null}
    </section>
  );
}
