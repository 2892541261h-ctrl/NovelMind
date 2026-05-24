import { useEffect, useState, useCallback } from "react";
import * as api from "../api/client";
import type { Project } from "../types/api";
import { LoadingState, ErrorState, EmptyState } from "../components/LoadingState";

interface RefNovel { id: number; project_id: number; title: string; author: string; content: string; source_type: string; status: string; created_at: string; updated_at: string; }
interface RefProfile { id: number; novel_id: number; project_id: number; genre: string; worldbuilding_pattern: string; character_archetypes: string; conflict_patterns: string; writing_style_profile: string; plot_progression_model: string; target_novel_direction: string; confidence: string; status: string; }

export function ReferenceNovelPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedId, setSelectedId] = useState<number>(() => Number(localStorage.getItem("selectedProjectId")) || 0);
  const [novels, setNovels] = useState<RefNovel[]>([]);
  const [selectedNovel, setSelectedNovel] = useState<RefNovel | null>(null);
  const [profile, setProfile] = useState<RefProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  const loadProjects = useCallback(async () => {
    try { setProjects(await api.getProjects()); } catch { /* ignore */ }
  }, []);

  const loadNovels = useCallback(async (pid: number) => {
    if (!pid) return;
    setLoading(true); setError(null);
    try {
      const url = `${BASE}/api/reference-novels?project_id=${pid}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(await res.text());
      setNovels(await res.json());
    } catch (e) { setError(e instanceof Error ? e.message : "load failed"); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { loadProjects(); }, [loadProjects]);
  useEffect(() => { loadNovels(selectedId); }, [selectedId, loadNovels]);

  function selectProject(id: number) { setSelectedId(id); localStorage.setItem("selectedProjectId", String(id)); setSelectedNovel(null); setProfile(null); }

  const BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

  async function handleCreate(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    try {
      const res = await fetch(`${BASE}/api/reference-novels`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: selectedId, title: fd.get("title"), author: fd.get("author"), content: fd.get("content"), source_type: "paste" }),
      });
      if (!res.ok) throw new Error(await res.text());
      setShowForm(false);
      loadNovels(selectedId);
    } catch (err) { alert(err instanceof Error ? err.message : "create failed"); }
  }

  async function handleDelete(novelId: number) {
    if (!confirm("confirm delete?")) return;
    await fetch(`${BASE}/api/reference-novels/${novelId}`, { method: "DELETE" });
    loadNovels(selectedId);
    setSelectedNovel(null); setProfile(null);
  }

  async function handleAnalyze(novelId: number) {
    setAnalyzing(true);
    try {
      const res = await fetch(`${BASE}/api/reference-novels/${novelId}/analyze`, { method: "POST" });
      if (!res.ok) throw new Error(await res.text());
      setProfile(await res.json());
    } catch (err) { alert(err instanceof Error ? err.message : "analyze failed"); }
    finally { setAnalyzing(false); }
  }

  async function selectNovel(novel: RefNovel) {
    setSelectedNovel(novel);
    setProfile(null);
    try {
      const res = await fetch(`${BASE}/api/reference-novels/${novel.id}/profile`);
      if (res.ok) setProfile(await res.json());
    } catch { /* no profile yet */ }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold">Reference Novel Analysis</h2>
        <select value={selectedId || ""} onChange={(e) => selectProject(Number(e.target.value))}
          className="rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white">
          <option value="">-- select project --</option>
          {projects.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
        </select>
        {selectedId > 0 && (
          <button onClick={() => setShowForm(!showForm)}
            className="rounded bg-cyan-600 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-700">
            {showForm ? "cancel" : "+ add reference novel"}
          </button>
        )}
      </div>

      <p className="text-xs text-slate-500">
        Reference novels are used to extract creative patterns (genre, worldbuilding, character archetypes, conflict types, writing style, plot progression).
        They are NOT used to copy, rewrite, or continue the original work. The extracted profile guides YOUR original novel creation.
      </p>

      {!selectedId ? <EmptyState text="select a project first" /> : (
        <>
          {showForm && (
            <form onSubmit={handleCreate} className="rounded-lg border border-slate-800 bg-slate-900 p-4 space-y-3">
              <input name="title" placeholder="reference novel title *" required className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" />
              <input name="author" placeholder="author (optional)" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" />
              <textarea name="content" placeholder="paste reference novel text here (for analysis only, will not be published)" rows={6} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" />
              <button type="submit" className="rounded bg-cyan-600 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-700">save</button>
            </form>
          )}

          {loading ? <LoadingState /> :
           error ? <ErrorState message={error} onRetry={() => loadNovels(selectedId)} /> :
           novels.length === 0 ? <EmptyState text="no reference novels yet" /> : (
            <div className="grid gap-3 lg:grid-cols-3">
              <div className="space-y-2 lg:col-span-1">
                {novels.map((n) => (
                  <div key={n.id}
                    onClick={() => selectNovel(n)}
                    className={`cursor-pointer rounded border p-3 text-sm transition ${selectedNovel?.id === n.id ? "border-cyan-500 bg-cyan-500/10" : "border-slate-800 bg-slate-900 hover:border-slate-700"}`}>
                    <div className="font-medium truncate">{n.title || "untitled"}</div>
                    <div className="text-xs text-slate-500 mt-1">{n.author || "unknown"} · {n.content.length} chars</div>
                    <button onClick={(e) => { e.stopPropagation(); handleDelete(n.id); }} className="mt-2 text-xs text-red-400 hover:underline">delete</button>
                  </div>
                ))}
              </div>

              <div className="space-y-3 lg:col-span-2">
                {selectedNovel && (
                  <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold">{selectedNovel.title || "untitled"}</h3>
                      <button onClick={() => handleAnalyze(selectedNovel.id)} disabled={analyzing}
                        className="rounded bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-emerald-700 disabled:opacity-50">
                        {analyzing ? "analyzing..." : "analyze (mock AI)"}
                      </button>
                    </div>

                    <div className="max-h-40 overflow-y-auto rounded bg-slate-950 p-3 mb-4">
                      <pre className="text-xs text-slate-400 whitespace-pre-wrap">{selectedNovel.content.slice(0, 1000)}{selectedNovel.content.length > 1000 ? "..." : ""}</pre>
                    </div>

                    {profile ? (
                      <div className="space-y-3">
                        <h4 className="text-sm font-semibold text-cyan-400">Reference Creation Profile (mock)</h4>
                        <Field label="genre" value={profile.genre} />
                        <Field label="worldbuilding" value={profile.worldbuilding_pattern} />
                        <Field label="character archetypes" value={profile.character_archetypes} />
                        <Field label="conflict patterns" value={profile.conflict_patterns} />
                        <Field label="writing style" value={profile.writing_style_profile} />
                        <Field label="plot progression" value={profile.plot_progression_model} />
                        <Field label="creative direction" value={profile.target_novel_direction} />
                        <div className="text-xs text-slate-600">confidence: {profile.confidence} · status: {profile.status}</div>
                      </div>
                    ) : (
                      <p className="text-xs text-slate-600">click "analyze" to generate a mock Reference Creation Profile. real AI analysis will come later via backend/ai/gateway.py.</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  if (!value) return null;
  return (
    <div>
      <div className="text-xs text-slate-500 mb-0.5">{label}</div>
      <div className="text-sm text-slate-300">{value.slice(0, 300)}{value.length > 300 ? "..." : ""}</div>
    </div>
  );
}
