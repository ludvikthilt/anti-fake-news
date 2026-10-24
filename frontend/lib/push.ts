import { api } from "@/lib/api";

export interface PushStatus {
  available: boolean;
  public_key: string;
  count: number;
}

export function pushSupported(): boolean {
  return (
    typeof window !== "undefined" &&
    "serviceWorker" in navigator &&
    "PushManager" in window &&
    "Notification" in window
  );
}

function urlBase64ToUint8Array(base64: string): Uint8Array {
  const padding = "=".repeat((4 - (base64.length % 4)) % 4);
  const normalized = (base64 + padding).replace(/-/g, "+").replace(/_/g, "/");
  const raw = window.atob(normalized);
  return Uint8Array.from([...raw].map((char) => char.charCodeAt(0)));
}

export async function enablePush(publicKey: string): Promise<void> {
  if (!pushSupported()) throw new Error("Ce navigateur ne prend pas en charge les notifications push.");
  const permission = await Notification.requestPermission();
  if (permission !== "granted") throw new Error("Notifications refusées par le navigateur.");
  await navigator.serviceWorker.register("/sw.js");
  const registration = await navigator.serviceWorker.ready;
  const existing = await registration.pushManager.getSubscription();
  const subscription =
    existing ??
    (await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(publicKey),
    }));
  await api("/auth/me/push/", {
    method: "POST",
    body: { ...subscription.toJSON(), consent: true },
  });
}

export async function disablePush(): Promise<void> {
  const registration = await navigator.serviceWorker.getRegistration();
  const subscription = await registration?.pushManager.getSubscription();
  if (subscription) {
    await api("/auth/me/push/", { method: "DELETE", body: { endpoint: subscription.endpoint } });
    await subscription.unsubscribe();
    return;
  }
  await api("/auth/me/push/", { method: "DELETE", body: {} });
}
