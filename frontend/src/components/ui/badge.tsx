import { cn } from "@/lib/utils";

const styles: Record<string, string> = {
  uploaded: "bg-slate-100 text-slate-700",
  processing: "bg-blue-100 text-blue-800",
  completed: "bg-emerald-100 text-emerald-800",
  failed: "bg-red-100 text-red-800",
  pending: "bg-amber-100 text-amber-900",
  in_review: "bg-indigo-100 text-indigo-800",
  approved: "bg-emerald-100 text-emerald-800",
  rejected: "bg-red-100 text-red-800",
};

export function Badge({ label, tone }: { label: string; tone: string }) {
  return (
    <span className={cn("inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium capitalize", styles[tone] ?? styles.uploaded)}>
      {label.replaceAll("_", " ")}
    </span>
  );
}
