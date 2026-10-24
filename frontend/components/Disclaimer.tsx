import { ShieldCheck } from "./Icon";

export default function Disclaimer() {
  return (
    <p className="banner" role="note">
      <ShieldCheck size={17} style={{ flex: "none", marginTop: 2, color: "var(--brand-700)" }} />
      <span>
        <strong>Ce site aide à vérifier :</strong> il ne prouve pas qu&apos;une information est
        vraie.
      </span>
    </p>
  );
}
