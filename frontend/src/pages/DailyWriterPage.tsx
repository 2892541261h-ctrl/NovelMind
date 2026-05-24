import { useEffect, useState, useCallback } from "react";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

interface DraftItem { id: number; project_id: number; chapter_number: number; title: string; status: string; source: string; created_at: string; updated_at: string; }
interface DraftRead extends DraftItem { content: string; writing_goal: string; prompt_snapshot: string; context_snapshot: string; }

export function DailyWriterPage() {
  const [selectedId, setSelectedId] = useState<number>(() => Number(localStorage.getItem("selectedProjectId")) || 0);
  const [hasProfile, setHasProfile] = useState<boolean | null>(null);
  const [drafts, setDrafts] = useState<DraftItem[]>([]);
  const [selected, setSelected] = useState<DraftRead | null>(null);

  const [chapterNumber, setChapterNumber] = useState(1);
  const [title, setTitle] = useState("");
  const [goal, setGoal] = useState("");
  const [extra, setExtra] = useState("");
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDrafts = useCallback(async () => {
    if (!selectedId) return;
    try {
      const r = await fetch(`${BASE}/api/daily-writer/chapters?project_id=${selectedId}`);
      if (r.ok) setDrafts(await r.json());
    } catch { /* */ }
  }, [selectedId]);

  useEffect(() => {
    if (!selectedId) return;
    loadDrafts();
    fetch(`${BASE}/api/reference-novels?project_id=${selectedId}`)
      .then((r) => r.json())
      .then((novels: Array<{ id: number }>) => novels.length > 0
        ? fetch(`${BASE}/api/reference-novels/${novels[0].id}/profile`).then(r => r.json())
        : Promise.reject())
      .then((p) => setHasProfile(!!p && !p.detail))
      .catch(() => setHasProfile(false));
  }, [selectedId, loadDrafts]);

  async function handleGenerate() {
    if (!selectedId) return;
    setGenerating(true); setError(null);
    try {
      const r = await fetch(`${BASE}/api/daily-writer/generate`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: selectedId, chapter_number: chapterNumber, title, writing_goal: goal, extra_instruction: extra }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || r.statusText);
      setSelected(data.draft);
      loadDrafts();
    } catch (e) { setError(e instanceof Error ? e.message : "generate failed"); }
    finally { setGenerating(false); }
  }

  async function viewDraft(id: number) {
    const r = await fetch(`${BASE}/api/daily-writer/chapters/${id}`);
    if (r.ok) setSelected(await r.json());
  }

  async function deleteDraft(id: number) {
    if (!confirm("delete this draft?")) return;
    await fetch(`${BASE}/api/daily-writer/chapters/${id}`, { method: "DELETE" });
    setSelected(null);
    loadDrafts();
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold">Daily Writer</h2>
        <span className="text-xs text-slate-500">project {selectedId || "(none)"}</span>
      </div>

      {!selectedId ? (
        <div className="rounded border border-dashed border-slate-700 p-6 text-center text-sm text-slate-500">
          select a project first (use Characters or Chapters page, then come back)
        </div>
      ) : (
        <>
          <div className={`rounded border px-4 py-3 text-sm ${hasProfile === true ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400" : "border-slate-800 bg-slate-900 text-slate-500"}`}>
            {hasProfile === null ? "checking reference profile..." :
             hasProfile ? "reference profile connected - creative guidance active" :
             "no reference profile. visit Ref Novels to analyze one."}
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900 p-4 space-y-3">
            <h3 className="text-sm font-semibold">Generate Chapter Draft</h3>
            <div className="flex gap-3">
              <input type="number" value={chapterNumber} onChange={(e) => setChapterNumber(Number(e.target.value) || 1)}
                className="w-28 rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" placeholder="#" />
              <input value={title} onChange={(e) => setTitle(e.target.value)}
                className="flex-1 rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" placeholder="chapter title (optional)" />
            </div>
            <textarea value={goal} onChange={(e) => setGoal(e.target.value)} rows={2}
              className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" placeholder="writing goal (optional)" />
            <textarea value={extra} onChange={(e) => setExtra(e.target.value)} rows={2}
              className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" placeholder="extra instructions (optional)" />
            <button onClick={handleGenerate} disabled={generating}
              className="rounded bg-cyan-600 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-700 disabled:opacity-50">
              {generating ? "generating..." : "Generate Chapter Draft"}
            </button>
            {error && <p className="text-sm text-red-400">{error}</p>}
          </div>

          <div className="grid gap-4 lg:grid-cols-5">
            <div className="space-y-2 lg:col-span-2">
              <h3 className="text-sm font-semibold mb-2">Drafts ({drafts.length})</h3>
              {drafts.length === 0 ? (
                <p className="text-xs text-slate-600">no drafts yet</p>
              ) : drafts.map((d) => (
                <div key={d.id}
                  onClick={() => viewDraft(d.id)}
                  className={`cursor-pointer rounded border p-3 text-sm transition ${selected?.id === d.id ? "border-cyan-500 bg-cyan-500/10" : "border-slate-800 bg-slate-900 hover:border-slate-700"}`}>
                  <div className="font-medium">#{d.chapter_number} {d.title || "untitled"}</div>
                  <div className="text-xs text-slate-500 mt-1">{d.status} · {new Date(d.created_at).toLocaleDateString()}</div>
                </div>
              ))}
            </div>

            <div className="lg:col-span-3">
              {selected ? (
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold">#{selected.chapter_number} {selected.title || "Chapter Draft"}</h3>
                    <button onClick={() => deleteDraft(selected.id)} className="text-xs text-red-400 hover:underline">delete</button>
                  </div>
                  {selected.writing_goal && <p className="text-xs text-slate-500 mb-3">goal: {selected.writing_goal}</p>}
                  <div className="max-h-96 overflow-y-auto rounded bg-slate-950 p-4">
                    <pre className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">{selected.content}</pre>
                  </div>
                  <p className="text-xs text-slate-600 mt-3">source: {selected.source} · status: {selected.status}</p>
                </div>
              ) : (
                <div className="rounded border border-dashed border-slate-700 p-10 text-center text-sm text-slate-600">
                  select a draft from the list or generate a new one
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
