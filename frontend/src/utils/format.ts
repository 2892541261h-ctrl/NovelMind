export function formatDate(iso: string): string {
  if (!iso) return "-";
  return new Date(iso).toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function statusBadge(status: string): string {
  const map: Record<string, string> = {
    planning: "bg-blue-500/20 text-blue-300",
    drafting: "bg-amber-500/20 text-amber-300",
    active: "bg-emerald-500/20 text-emerald-300",
    completed: "bg-green-500/20 text-green-300",
    draft: "bg-slate-500/20 text-slate-300",
    planted: "bg-purple-500/20 text-purple-300",
    revealed: "bg-cyan-500/20 text-cyan-300",
  };
  return map[status] ?? "bg-slate-500/20 text-slate-300";
}
