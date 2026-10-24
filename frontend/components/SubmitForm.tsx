"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { AnalysisDetail } from "@/lib/types";
import { FileText, ImageIcon, Link, Send } from "./Icon";
import styles from "./ui.module.css";

type Tab = "text" | "link" | "image";

export default function SubmitForm() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("text");
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [image, setImage] = useState("");
  const [error, setError] = useState("");
  const [sending, setSending] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const MAX_TEXT = 5000;
  const MAX_IMG_BYTES = 5 * 1024 * 1024;

  async function submit() {
    setError("");
    const body: Record<string, string> = { input_type: tab };
    if (tab === "text") {
      if (!text.trim()) return setError("Veuillez saisir un texte à analyser.");
      body.input_text = text;
    } else if (tab === "link") {
      if (!url.trim()) return setError("Veuillez coller un lien.");
      body.input_url = url;
    } else {
      if (!image) return setError("Veuillez choisir une image.");
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
      return setError("Format non pris en charge : JPEG, PNG ou WebP uniquement.");
    }
    if (file.size > MAX_IMG_BYTES) {
      return setError("Image trop lourde : 5 Mo maximum.");
    }
    const img = new Image();
    const objectUrl = URL.createObjectURL(file);
    img.onload = () => {
      URL.revokeObjectURL(objectUrl);
      if (img.width > 4096 || img.height > 4096) {
        return setError("Image trop grande : 4 096 pixels maximum.");
      }
      const reader = new FileReader();
      reader.onload = () => setImage(String(reader.result));
      reader.readAsDataURL(file);
    };
    img.src = objectUrl;
  }

  return (
    <div>
      <div className={styles.tabs} role="tablist" aria-label="Type de contenu">
        <button role="tab" aria-selected={tab === "text"} className={styles.tab} onClick={() => setTab("text")}>
          <FileText size={16} /> Texte
        </button>
        <button role="tab" aria-selected={tab === "link"} className={styles.tab} onClick={() => setTab("link")}>
          <Link size={16} /> Lien
        </button>
        <button role="tab" aria-selected={tab === "image"} className={styles.tab} onClick={() => setTab("image")}>
          <ImageIcon size={16} /> Image
        </button>
      </div>

      {tab === "text" && (
        <div>
          <label htmlFor="input-text" className="sr-only">Texte à analyser</label>
          <textarea
            id="input-text"
            rows={5}
            maxLength={MAX_TEXT}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Collez ici l'information à vérifier…"
            aria-describedby="text-count"
          />
          <div className={styles.counter} id="text-count">
            {text.length} / {MAX_TEXT}
          </div>
        </div>
      )}

      {tab === "link" && (
        <div>
          <label htmlFor="input-url" className="sr-only">Lien à analyser</label>
          <input
            id="input-url"
            type="url"
            inputMode="url"
            className="mono"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://…"
          />
        </div>
      )}

      {tab === "image" && (
        <div>
          <input ref={fileRef} type="file" accept="image/jpeg,image/png,image/webp" className="sr-only" onChange={(e) => onFile(e.target.files?.[0])} />
          <button type="button" className={styles.dropzone} onClick={() => fileRef.current?.click()}>
            {image ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={image} alt="Aperçu de l'image soumise" style={{ maxWidth: "100%", maxHeight: 220, borderRadius: "var(--radius-md)" }} />
            ) : (
              <>
                <ImageIcon size={28} style={{ display: "block", margin: "0 auto" }} />
                Glissez une image ici ou appuyez pour choisir un fichier.
                <br />
                <span style={{ fontSize: "var(--fs-xs)" }}>JPEG, PNG ou WebP · 5 Mo maximum · 4 096 px maximum</span>
              </>
            )}
          </button>
        </div>
      )}

      <p style={{ fontSize: "var(--fs-xs)", color: "var(--ink-muted)", marginTop: "var(--s-3)" }}>
        Ne soumettez pas d&apos;informations personnelles ou confidentielles. Le contenu peut être transmis à des services externes.{" "}
        <a href="/confidentialite">En savoir plus sur la confidentialité.</a>
      </p>
      <p style={{ fontSize: "var(--fs-xs)", color: "var(--ink-muted)" }}>
        Les vidéos, audios et groupes fermés ne sont pas encore pris en charge : collez le texte ou l&apos;image à la main.
      </p>

      {error && <p className="error-text" role="alert">{error}</p>}

      <button className="btn btn-primary" onClick={submit} disabled={sending} style={{ width: "100%", marginTop: "var(--s-3)" }}>
        <Send size={16} /> {sending ? "Lancement…" : "Analyser"}
      </button>
    </div>
  );
}
