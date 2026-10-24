"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api, setStoredUser, setTokens } from "@/lib/api";
import { googleCallbackUri } from "@/lib/google";
import type { UserInfo } from "@/lib/types";

interface GoogleAuthResponse {
  access: string;
  refresh: string;
  user: UserInfo;
}

function CallbackInner() {
  const params = useSearchParams();
  const router = useRouter();
  const [error, setError] = useState("");

  useEffect(() => {
    const code = params.get("code");
    if (!code) {
      setError("La connexion Google a été annulée ou aucun code n'a été reçu.");
      return;
    }
    const nonce = sessionStorage.getItem("google.nonce") || "";
    api<GoogleAuthResponse>("/auth/google/", {
      method: "POST",
      auth: false,
      body: { code, redirect_uri: googleCallbackUri(), nonce },
    })
      .then((res) => {
        setTokens(res.access, res.refresh);
        setStoredUser(res.user);
        sessionStorage.removeItem("google.nonce");
        router.replace("/compte");
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Connexion Google impossible."));
  }, [params, router]);

  if (error) {
    return (
      <div className="container" style={{ maxWidth: "30rem" }}>
        <h1>Connexion Google</h1>
        <p className="error-text" role="alert">{error}</p>
        <p>
          <a href="/compte">Revenir à la page de connexion</a>
        </p>
      </div>
    );
  }

  return (
    <div className="container" style={{ maxWidth: "30rem" }}>
      <h1>Connexion Google</h1>
      <p>
        <span className="pulse" aria-hidden /> Vérification de votre compte…
      </p>
    </div>
  );
}

export default function GoogleCallbackPage() {
  return (
    <Suspense fallback={<div className="container"><p>Chargement…</p></div>}>
      <CallbackInner />
    </Suspense>
  );
}
