import type { StatusKey } from "@/lib/types";
import { CheckCircle, HelpCircle, MinusCircle, XCircle } from "./Icon";
import styles from "./ui.module.css";

const MAP: Record<StatusKey, { label: string; cls: string; Icon: typeof CheckCircle }> = {
  corroboree: { label: "Corroborée", cls: styles.ok, Icon: CheckCircle },
  non_corroboree: { label: "Non corroborée", cls: styles.warn, Icon: MinusCircle },
  contredite: { label: "Contredite", cls: styles.bad, Icon: XCircle },
  indeterminee: { label: "Indéterminée", cls: styles.unk, Icon: HelpCircle },
};

export default function StatusBadge({ status }: { status: StatusKey }) {
  const { label, cls, Icon } = MAP[status] ?? MAP.indeterminee;
  return (
    <span className={`${styles.badge} ${cls}`}>
      <Icon size={16} />
      {label}
    </span>
  );
}
