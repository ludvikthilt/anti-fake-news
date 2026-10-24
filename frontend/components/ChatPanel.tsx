"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { ArrowRight, CheckCircle, MessageCircle, Search, Send, Sparkles, X } from "./Icon";
import Spinner from "./Spinner";
import styles from "./ui.module.css";

interface ChatResponse {
  answer: string;
  sources?: { title: string; url: string }[];
}

const SUGGESTIONS = [
  "Vérifier une rumeur",
  "Retrouver une source",
  "Évaluer une image",
];

export default function ChatPanel() {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<{ role: "user" | "bot"; text: string; links?: { title: string; url: string }[] }[]>([]);
  const [busy, setBusy] = useState(false);
  const questionInput = useRef<HTMLInputElement>(null);

  // Le bouton d'en-tête (desktop) ouvre le même panneau.
  useEffect(() => {
    const openPanel = () => setOpen(true);
    window.addEventListener("antifake:chat", openPanel);
    return () => window.removeEventListener("antifake:chat", openPanel);
  }, []);

  useEffect(() => {
    if (!open) return;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [open]);

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
      setMessages((m) => [
        ...m,
        { role: "bot", text: "Je ne peux pas répondre pour l'instant. Vous pouvez lancer une analyse directement." },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <button
        type="button"
        className={styles.chatFab}
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls="panneau-assistance"
        aria-label="Poser une question à l'assistant"
      >
        <MessageCircle size={21} />
        <span className={styles.chatFabLabel}>Poser une question</span>
      </button>

      {open && (
        <div className={styles.chatPanel} id="panneau-assistance" role="dialog" aria-label="Assistant de vérification">
          <div className={styles.chatHead}>
            <span className={styles.chatAvatar} aria-hidden="true">
              <Sparkles size={21} />
            </span>
            <div className={styles.chatIdentity}>
              <span className={styles.chatEyebrow}>Assistant EMI</span>
              <strong>Assistant de vérification</strong>
              <span>Des repères, jamais un verdict</span>
            </div>
            <button type="button" className={styles.chatClose} onClick={() => setOpen(false)} aria-label="Fermer l'assistant">
              <X size={18} />
            </button>
          </div>

          <div className={styles.chatContext}>
            <span className={styles.chatContextBadge}><CheckCircle size={15} /> Mode pédagogique</span>
            <span className={styles.chatContextBadge}>Sans verdict automatique</span>
            <p><Sparkles size={15} /> Démarche critique · Sources · Réseau Mfoundi</p>
          </div>

          <div className={styles.chatBody} aria-live="polite">
            {messages.length === 0 && (
              <div className={styles.chatWelcome}>
                <span className={styles.chatWelcomeIcon} aria-hidden="true"><MessageCircle size={21} /></span>
                <div>
                  <strong>Par où commencer ?</strong>
                  <p>Décrivez l&apos;information qui vous questionne : nous chercherons ensemble des pistes et des sources à consulter.</p>
                </div>
                <div className={styles.chatSuggestions} aria-label="Suggestions de questions">
                  {SUGGESTIONS.map((suggestion) => (
                    <button
                      type="button"
                      className={styles.chatSuggestion}
                      key={suggestion}
                      onClick={() => {
                        setQuestion(suggestion);
                        questionInput.current?.focus();
                      }}
                    >
                      {suggestion}<ArrowRight size={14} />
                    </button>
                  ))}
                </div>
              </div>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`${styles.chatMsg} ${m.role === "user" ? styles.chatUser : styles.chatBot}`}>
                <div>{m.text}</div>
                {m.links && m.links.length > 0 && (
                  <div className="stack-sm" style={{ marginTop: "var(--s-2)" }}>
                    {m.links.map((l, j) => (
                      <a key={j} href={l.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: "var(--fs-xs)" }}>
                        {l.title || l.url}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {busy && (
              <div className={`${styles.chatMsg} ${styles.chatBot}`}>
                <span className="cluster" style={{ gap: 8 }}>
                  <Spinner size={15} label="Recherche en cours" /> Recherche en cours…
                </span>
              </div>
            )}
          </div>

          <form className={styles.chatForm} onSubmit={ask}>
            <input
              ref={questionInput}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Posez une question de méthode…"
              aria-label="Votre question"
            />
            <button className={`btn btn-primary ${styles.chatSend}`} type="submit" aria-label="Envoyer" disabled={busy || !question.trim()}>
              <Send size={16} />
            </button>
          </form>
          <div className={styles.chatFoot}>
            <p>L&apos;assistant propose des pistes, sans valider de fait.</p>
            <Link href="/" className={`btn btn-secondary ${styles.chatAnalyze}`} onClick={() => setOpen(false)}>
              <Search size={17} /> Lancer une analyse
            </Link>
          </div>
        </div>
      )}
    </>
  );
}
