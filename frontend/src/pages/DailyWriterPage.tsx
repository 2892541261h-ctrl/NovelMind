import { useEffect, useState, useCallback } from "react";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

interface DraftItem { id: number; project_id: number; chapter_number: number; title: string; status: string; source: string; created_at: string; updated_at: string; }
interface DraftRead extends DraftItem { content: string; writing_goal: string; prompt_snapshot: string; context_snapshot: string; }
interface FormalItem { id: number; project_id: number; chapter_number: number; title: string; status: string; word_count: number; published_at: string | null; created_at: string; updated_at: string; }
interface FormalRead extends FormalItem { content: string; source_draft_id: number | null; }

export function DailyWriterPage() {
  const [pid, setPid] = useState<number>(() => Number(localStorage.getItem("selectedProjectId")) || 0);
  const [hasProfile, setHasProfile] = useState<boolean | null>(null);
  const [drafts, setDrafts] = useState<DraftItem[]>([]);
  const [selDraft, setSelDraft] = useState<DraftRead | null>(null);
  const [formalChs, setFormalChs] = useState<FormalItem[]>([]);
  const [selFormal, setSelFormal] = useState<FormalRead | null>(null);
  const [tab, setTab] = useState<"generate" | "drafts" | "published">("generate");

  const [cNum, setCNum] = useState(1);
  const [title, setTitle] = useState("");
  const [goal, setGoal] = useState("");
  const [extra, setExtra] = useState("");
  const [genLoading, setGenLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [editTitle, setEditTitle] = useState("");
  const [editContent, setEditContent] = useState("");
  const [editSaving, setEditSaving] = useState(false);
  const [pubLoading, setPubLoading] = useState(false);

  const loadDrafts = useCallback(async () => {
    if (!pid) { setDrafts([]); return; }
    try { const r = await fetch(`${BASE}/api/daily-writer/chapters?project_id=${pid}`); if (r.ok) setDrafts(await r.json()); } catch { /* */ }
  }, [pid]);

  const loadFormal = useCallback(async () => {
    if (!pid) { setFormalChs([]); return; }
    try { const r = await fetch(`${BASE}/api/chapters?project_id=${pid}`); if (r.ok) setFormalChs(await r.json()); } catch { /* */ }
  }, [pid]);

  useEffect(() => {
    if (!pid) { setDrafts([]); setSelDraft(null); setFormalChs([]); setSelFormal(null); setHasProfile(null); return; }
    loadDrafts(); loadFormal();
    fetch(`${BASE}/api/reference-novels?project_id=${pid}`)
      .then(r => r.json()).then((ns: Array<{id:number}>) => ns.length>0 ? fetch(`${BASE}/api/reference-novels/${ns[0].id}/profile`).then(r=>r.json()) : Promise.reject())
      .then(p => setHasProfile(!!p && !p.detail)).catch(() => setHasProfile(false));
  }, [pid, loadDrafts, loadFormal]);

  function setProject(n: number) { setPid(n); n>0 ? localStorage.setItem("selectedProjectId", String(n)) : localStorage.removeItem("selectedProjectId"); }

  async function handleGenerate() {
    if (!pid) return; setGenLoading(true); setError(null);
    try {
      const r = await fetch(`${BASE}/api/daily-writer/generate`, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({project_id:pid, chapter_number:cNum, title, writing_goal:goal, extra_instruction:extra}) });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || r.statusText);
      setTab("drafts"); setSelDraft(data.draft); setSelFormal(null); loadDrafts();
    } catch(e) { setError(e instanceof Error ? e.message : "generate failed"); }
    finally { setGenLoading(false); }
  }

  async function viewDraft(id: number) {
    setSelFormal(null);
    try { const r = await fetch(`${BASE}/api/daily-writer/chapters/${id}`); if (r.ok) { const d = await r.json(); setSelDraft(d); setEditTitle(d.title); setEditContent(d.content); } } catch { /* */ }
  }

  async function saveDraft() {
    if (!selDraft) return; setEditSaving(true); setError(null);
    try {
      const r = await fetch(`${BASE}/api/daily-writer/chapters/${selDraft.id}`, { method:"PATCH", headers:{"Content-Type":"application/json"}, body:JSON.stringify({title:editTitle, content:editContent}) });
      if (!r.ok) throw new Error((await r.json()).detail || r.statusText);
      setSelDraft(await r.json()); loadDrafts();
    } catch(e) { setError(e instanceof Error ? e.message : "save failed"); }
    finally { setEditSaving(false); }
  }

  async function deleteDraft(id: number) {
    if (!confirm("delete this draft?")) return;
    await fetch(`${BASE}/api/daily-writer/chapters/${id}`, { method:"DELETE" });
    setSelDraft(null); loadDrafts();
  }

  async function publishDraft() {
    if (!selDraft) return; setPubLoading(true); setError(null);
    try {
      const r = await fetch(`${BASE}/api/chapters/publish-draft/${selDraft.id}`, { method:"POST" });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || r.statusText);
      setTab("published"); setSelFormal(data.chapter); setSelDraft(null); loadFormal();
    } catch(e) { setError(e instanceof Error ? e.message : "publish failed"); }
    finally { setPubLoading(false); }
  }

  async function viewFormal(id: number) {
    setSelDraft(null);
    try { const r = await fetch(`${BASE}/api/chapters/${id}`); if (r.ok) setSelFormal(await r.json()); } catch { /* */ }
  }

  function exportMarkdown() { if (pid) window.open(`${BASE}/api/exports/project/${pid}/markdown`); }
  function exportTxt() { if (pid) window.open(`${BASE}/api/exports/project/${pid}/txt`); }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4 flex-wrap">
        <h2 className="text-lg font-semibold">Daily Writer</h2>
        <label className="flex items-center gap-2 text-xs text-slate-500">
          project <input type="number" min={1} value={pid||""} onChange={e=>setProject(Number(e.target.value)||0)} className="w-24 rounded border border-slate-700 bg-slate-800 px-2 py-1 text-sm text-white" />
        </label>
      </div>

      {!pid ? <Placeholder text="select a project first" /> : (
        <>
          <div className={`rounded border px-4 py-3 text-sm ${hasProfile===true?"border-emerald-500/30 bg-emerald-500/10 text-emerald-400":"border-slate-800 bg-slate-900 text-slate-500"}`}>
            {hasProfile===null?"checking...":hasProfile?"reference profile connected":"no reference profile"}
          </div>

          <div className="flex gap-2">
            {(["generate","drafts","published"] as const).map(t => (
              <button key={t} onClick={()=>setTab(t)} className={`rounded px-3 py-1.5 text-xs font-medium ${tab===t?"bg-cyan-600 text-white":"border border-slate-700 text-slate-400 hover:text-white"}`}>
                {t==="generate"?"Generate":t==="drafts"?`Drafts (${drafts.length})`:`Published (${formalChs.length})`}
              </button>
            ))}
          </div>

          {tab === "generate" && (
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-4 space-y-3">
              <h3 className="text-sm font-semibold">New Chapter Draft</h3>
              <div className="flex gap-3">
                <input type="number" value={cNum} onChange={e=>setCNum(Number(e.target.value)||1)} className="w-28 rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" placeholder="#" />
                <input value={title} onChange={e=>setTitle(e.target.value)} className="flex-1 rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" placeholder="title (optional)" />
              </div>
              <textarea value={goal} onChange={e=>setGoal(e.target.value)} rows={2} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" placeholder="writing goal (optional)" />
              <textarea value={extra} onChange={e=>setExtra(e.target.value)} rows={2} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" placeholder="extra instructions (optional)" />
              <button onClick={handleGenerate} disabled={genLoading} className="rounded bg-cyan-600 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-700 disabled:opacity-50">{genLoading?"generating...":"Generate"}</button>
              {error && <p className="text-sm text-red-400">{error}</p>}
            </div>
          )}

          <div className="grid gap-4 lg:grid-cols-5">
            <div className="space-y-2 lg:col-span-2">
              {tab === "drafts" && (
                <>
                  <h3 className="text-sm font-semibold">Drafts</h3>
                  {drafts.length===0 ? <p className="text-xs text-slate-600">no drafts</p> : drafts.map(d=>(
                    <div key={d.id} onClick={()=>viewDraft(d.id)} className={`cursor-pointer rounded border p-3 text-sm transition ${selDraft?.id===d.id?"border-cyan-500 bg-cyan-500/10":"border-slate-800 bg-slate-900 hover:border-slate-700"}`}>
                      <div className="font-medium">#{d.chapter_number} {d.title||"untitled"}</div>
                      <div className="text-xs text-slate-500 mt-1">{d.status} · {new Date(d.created_at).toLocaleDateString()}</div>
                    </div>
                  ))}
                </>
              )}
              {tab === "published" && (
                <>
                  <h3 className="text-sm font-semibold">Published Chapters</h3>
                  <div className="flex gap-2 mb-2">
                    <button onClick={exportMarkdown} className="text-xs text-cyan-400 hover:underline">Export MD</button>
                    <button onClick={exportTxt} className="text-xs text-cyan-400 hover:underline">Export TXT</button>
                  </div>
                  {formalChs.length===0 ? <p className="text-xs text-slate-600">no chapters</p> : formalChs.map(c=>(
                    <div key={c.id} onClick={()=>viewFormal(c.id)} className={`cursor-pointer rounded border p-3 text-sm transition ${selFormal?.id===c.id?"border-emerald-500 bg-emerald-500/10":"border-slate-800 bg-slate-900 hover:border-slate-700"}`}>
                      <div className="font-medium">#{c.chapter_number} {c.title||"untitled"}</div>
                      <div className="text-xs text-slate-500 mt-1">{c.word_count} chars · {c.published_at ? new Date(c.published_at).toLocaleDateString() : "-"}</div>
                    </div>
                  ))}
                </>
              )}
            </div>

            <div className="lg:col-span-3">
              {selDraft && (
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold">Draft #{selDraft.chapter_number} {selDraft.title}</h3>
                    <div className="flex gap-2">
                      <button onClick={saveDraft} disabled={editSaving} className="rounded bg-cyan-600 px-3 py-1 text-xs text-white hover:bg-cyan-700 disabled:opacity-50">{editSaving?"saving...":"Save"}</button>
                      <button onClick={publishDraft} disabled={pubLoading} className="rounded bg-emerald-600 px-3 py-1 text-xs text-white hover:bg-emerald-700 disabled:opacity-50">{pubLoading?"publishing...":"Publish"}</button>
                      <button onClick={()=>deleteDraft(selDraft.id)} className="text-xs text-red-400 hover:underline">Del</button>
                    </div>
                  </div>
                  <input value={editTitle} onChange={e=>setEditTitle(e.target.value)} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" />
                  <textarea value={editContent} onChange={e=>setEditContent(e.target.value)} rows={18} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white font-mono leading-relaxed" />
                  <p className="text-xs text-slate-600">editing draft. publish to create a formal chapter (draft will be kept).</p>
                </div>
              )}
              {selFormal && !selDraft && (
                <div className="rounded-lg border border-emerald-500/30 bg-slate-900 p-5">
                  <h3 className="font-semibold mb-2">#{selFormal.chapter_number} {selFormal.title||"Chapter"} <span className="text-xs text-emerald-400">published</span></h3>
                  <div className="max-h-96 overflow-y-auto rounded bg-slate-950 p-4">
                    <pre className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">{selFormal.content}</pre>
                  </div>
                  <p className="text-xs text-slate-600 mt-3">{selFormal.word_count} chars · published {selFormal.published_at ? new Date(selFormal.published_at).toLocaleDateString() : "-"}</p>
                </div>
              )}
              {!selDraft && !selFormal && <Placeholder text="select a draft or published chapter" />}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function Placeholder({ text }: { text: string }) {
  return <div className="rounded border border-dashed border-slate-700 p-10 text-center text-sm text-slate-600">{text}</div>;
}
