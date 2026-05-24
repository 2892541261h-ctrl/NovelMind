import { useEffect, useState } from "react";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export function DailyWriterPage() {
  const [selectedId] = useState<number>(() => Number(localStorage.getItem("selectedProjectId")) || 0);
  const [hasProfile, setHasProfile] = useState<boolean | null>(null);

  useEffect(() => {
    if (!selectedId) return;
    fetch(`${BASE}/api/reference-novels?project_id=${selectedId}`)
      .then((r) => r.json())
      .then((novels: Array<{ id: number }>) => {
        if (novels.length === 0) { setHasProfile(false); return; }
        return fetch(`${BASE}/api/reference-novels/${novels[0].id}/profile`);
      })
      .then((r) => r?.json())
      .then((profile) => setHasProfile(!!profile && !profile.detail))
      .catch(() => setHasProfile(false));
  }, [selectedId]);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Daily Writer</h2>
      {selectedId > 0 && (
        <div className={`rounded border px-4 py-3 text-sm ${hasProfile === true ? "border-emerald-500/30 bg-emerald-500/10" : "border-slate-800 bg-slate-900"}`}>
          {hasProfile === null ? (
            <span className="text-slate-500">checking reference profile...</span>
          ) : hasProfile ? (
            <span className="text-emerald-400">reference profile connected for creative guidance</span>
          ) : (
            <span className="text-slate-500">no reference profile yet. visit Ref Novels page to analyze one.</span>
          )}
        </div>
      )}
      <div className="rounded-lg border border-dashed border-slate-700 p-10 text-center">
        <p className="text-slate-400 mb-2">Daily Writer - generate novel chapters.</p>
        <p className="text-sm text-slate-600">coming soon:</p>
        <ul className="mt-3 text-sm text-slate-500 space-y-1">
          <li>- config daily generation schedule</li>
          <li>- preview next chapter info</li>
          <li>- view generation history</li>
          <li>- manual chapter generation</li>
        </ul>
        <p className="mt-4 text-xs text-slate-600">safety: never overwrite existing chapters.</p>
      </div>
    </div>
  );
}
