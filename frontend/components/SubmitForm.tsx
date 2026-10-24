"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { AnalysisDetail } from "@/lib/types";
import { Camera, Clipboard, FileText, ImageIcon, Link as LinkIcon, Lock, Send, X } from "./Icon";
import Spinner from "./Spinner";
import styles from "./ui.module.css";

type Tab = "text" | "link" | "image";

const MAX_TEXT = 5000;
const MAX_IMG_BYTES = 5 * 1024 * 1024;

export default function SubmitForm() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("text");
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [image, setImage] = useState("");
  const [error, setError] = useState("");
  const [sending, setSending] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  async function paste() {
    try {
      const clip = await navigator.clipboard.readText();
      if (clip) setText(clip.slice(0, MAX_TEXT));
    } catch {
      document.getElementById("input-text")?.focus();
    }
  }

  async function submit() {
    setError("");
    const body: Record<string, string> = { input_type: tab };
    if (tab === "text") {
      if (!text.trim()) return setError("Collez ou saisissez le texte à vérifier.");
      body.input_text = text;
    } else if (tab === "link") {
      if (!url.trim()) return setError("Collez le lien de la publication à vérifier.");
      body.input_url = url;
    } else {
      if (!image) return setError("Choisissez une capture d'écran à analyser.");
      body.image = image;
    }
    setSending(true);
    try {
      // `auth` par défaut : un visiteur reste anonyme (aucun jeton), un inscrit
      // retrouve son analyse dans son historique et reçoit ses notifications.
      const res = await api<AnalysisDetail>("/analyses/", { method: "POST", body });
      router.push(`/analyses/${res.public_id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "L'analyse n'a pas pu être lancée.");
      setSending(false);
    }
  }

  async function onFile(file: File | undefined) {
    setError("");
    if (!file) return;
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      return setError("Formats acceptés : JPEG, PNG ou WebP.");
    }
    if (file.size > MAX_IMG_BYTES) {
      return setError("Cette image dépasse 5 Mo. Réduisez-la avant de l'envoyer.");
    }
    const img = new Image();
    const objectUrl = URL.createObjectURL(file);
    img.onload = () => {
      URL.revokeObjectURL(objectUrl);
      if (img.width > 4096 || img.height > 4096) {
        return setError("Cette image dépasse 4 096 pixels de côté.");
      }
      const reader = new FileReader();
      reader.onload = () => setImage(String(reader.result));
      reader.readAsDataURL(file);
    };
    img.src = objectUrl;
  }

  return (
    <div>
      <div className={styles.tabs} role="tablist" aria-label="Type de contenu à vérifier">
        <button
          role="tab"
          type="button"
          aria-selected={tab === "text"}
          aria-controls="panneau-texte"
          className={styles.tab}
          onClick={() => setTab("text")}
        >
          <FileText size={16} /> Texte
        </button>
        <button
          role="tab"
          type="button"
          aria-selected={tab === "link"}
          aria-controls="panneau-lien"
          className={styles.tab}
          onClick={() => setTab("link")}
        >
          <LinkIcon size={16} /> Lien
        </button>
        <button
          role="tab"
          type="button"
          aria-selected={tab === "image"}
          aria-controls="panneau-image"
          className={styles.tab}
          onClick={() => setTab("image")}
        >
          <ImageIcon size={16} /> Image
        </button>
      </div>

      <div id="panneau-texte" role="tabpanel" hidden={tab !== "text"}>
        <label htmlFor="input-text" className="sr-only">
          Texte à analyser
        </label>
        <div className={styles.editor}>
          <textarea
            id="input-text"
            rows={5}
            maxLength={MAX_TEXT}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Collez le message reçu par WhatsApp, SMS, ou copié sur Facebook…"
          />
          <div className={styles.editorBar}>
            <button type="button" className={styles.pasteBtn} onClick={paste}>
              <Clipboard size={15} /> Coller le message
            </button>
            <span className={styles.counter} data-over={text.length > MAX_TEXT - 500} aria-live="polite">
              {text.length.toLocaleString("fr-FR")} / {MAX_TEXT.toLocaleString("fr-FR")}
            </span>
          </div>
        </div>
      </div>

      <div id="panneau-lien" role="tabpanel" hidden={tab !== "link"}>
        <label htmlFor="input-url" className="hint" style={{ display: "block", marginBottom: 6, fontWeight: 600 }}>
          Adresse de la publication ou de la page web
        </label>
        <div className={styles.editor}>
          <input
            id="input-url"
            type="url"
            inputMode="url"
            autoComplete="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://…"
          />
        </div>
      </div>

      <div id="panneau-image" role="tabpanel" hidden={tab !== "image"}>
        <input
          ref={fileRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          className="sr-only"
          onChange={(e) => onFile(e.target.files?.[0])}
        />
        {image ? (
          <div className="stack-sm">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={image} alt="Aperçu de la capture à analyser" className={styles.previewImg} />
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => {
                setImage("");
                if (fileRef.current) fileRef.current.value = "";
              }}
            >
              <X size={16} /> Changer d&apos;image
            </button>
          </div>
        ) : (
          <button type="button" className={styles.dropzone} onClick={() => fileRef.current?.click()}>
            <Camera size={30} style={{ color: "var(--brand-700)" }} />
            <strong>Choisir une capture d&apos;écran</strong>
            <span>Affiche, tract, photo ou publication partagée — JPEG, PNG ou WebP, 5 Mo maximum.</span>
          </button>
        )}
      </div>

      <div className={styles.audioNote}>
        <span aria-hidden style={{ color: "var(--warn-bd)", fontWeight: 700 }}>♪</span>
        <p>
          <strong>Message audio reçu sur WhatsApp ?</strong>
          La plateforme ne lit pas encore les fichiers vocaux : transcrivez les propos essentiels
          ou joignez la capture des commentaires.
        </p>
      </div>

      {error && <p className="error-text" role="alert">{error}</p>}

      <button type="button" className={`btn btn-primary ${styles.submitBtn}`} onClick={submit} disabled={sending}>
        {sending ? (
          <>
            <Spinner size={17} label="Analyse en cours" /> Analyse en cours…
          </>
        ) : (
          <>
            <Send size={18} /> Analyser l&apos;information
          </>
        )}
      </button>

      <p className={styles.privacyNote}>
        <Lock size={13} style={{ marginTop: 1, flex: "none" }} />
        <span>
          Traitement anonymisé. Ne soumettez ni information personnelle ni contenu confidentiel.
          Les images ne sont pas conservées après l&apos;analyse.{" "}
          <a href="/confidentialite">Confidentialité</a>
        </span>
      </p>
    </div>
  );
}
