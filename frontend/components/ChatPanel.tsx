"use client";

import { useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { MessageCircle, Send, X } from "./Icon";
import styles from "./ui.module.css";

interface ChatResponse {
  answer: string;
  sources?: { title: string; url: string }[];
}

export default function ChatPanel() {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<{ role: "user" | "bot"; text: string; links?: { title: string; url: string }[] }[]>([]);
  const [busy, setBusy] = useState(false);

  async function ask(e: React.FormEvent) {
    e.preventDefault();
    const q = question.trim();
    if (!q || busy) return;
    setMessages((m) => [...m, { role: "user", text: q }]);
    setQuestion("");
    setBusy(true);
    try {
      const res = await api<ChatResponse>("/chat/", { method: "POST", body: { question: q }, auth: false });
      setMessages((m) => [...m, { role: "bot", text: res.answer || "", links: res.sources }]);
    } catch {
      setMessages((m) => [...m, { role: "bot", text: "Le service est momentanément indisponible. Vous pouvez lancer une analyse directement." }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <button className={styles.chatFab} onClick={() => setOpen((v) => !v)} aria-expanded={open}>
        <MessageCircle size={18} /> Poser une question
      </button>
      {open && (
        <div className={styles.chatPanel} role="dialog" aria-label="Chatbot de redirection">
          <div className={styles.chatHead}>
            <span>Besoin d&apos;un éclairage ?</span>
            <button onClick={() => setOpen(false)} aria-label="Fermer le chatbot" style={{ background: "transparent", border: "none", color: "#fff" }}>
              <X size={18} />
            </button>
          </div>
          <div className={styles.chatBody} aria-live="polite">
            {messages.length === 0 && (
              <div className={`${styles.chatMsg} ${styles.chatBot}`}>
                Je vous aide à trouver où vérifier une information. Je ne dis jamais si elle est « vraie » ou « fausse ».
              </div>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`${styles.chatMsg} ${m.role === "user" ? styles.chatUser : styles.chatBot}`}>
                <div>{m.text}</div>
                {m.links && m.links.length > 0 && (
                  <div style={{ display: "flex", flexDirection: "column", gap: "var(--s-1)", marginTop: "var(--s-2)" }}>
                    {m.links.map((l, j) => (
                      <a key={j} href={l.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: "var(--fs-xs)" }}>
                        {l.title || l.url}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {busy && <div className={`${styles.chatMsg} ${styles.chatBot}`}>…</div>}
          </div>
          <form className={styles.chatForm} onSubmit={ask}>
            <input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Votre question…" aria-label="Votre question" />
            <button className="btn btn-primary" type="submit" aria-label="Envoyer" disabled={busy}>
              <Send size={16} />
            </button>
          </form>
          <div style={{ padding: "var(--s-1) var(--s-3) var(--s-3)", textAlign: "center" }}>
            <Link href="/" className="btn btn-ghost" onClick={() => setOpen(false)}>
              Lancer une analyse
            </Link>
          </div>
        </div>
      )}
    </>
  );
}
