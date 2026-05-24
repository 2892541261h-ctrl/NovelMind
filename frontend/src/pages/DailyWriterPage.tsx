import { useEffect, useState, useCallback } from "react";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

interface DraftItem { id: number; project_id: number; chapter_number: number; title: string; status: string; source: string; created_at: string; updated_at: string; }
interface DraftRead extends DraftItem { content: string; writing_goal: string; prompt_snapshot: string; context_snapshot: string; }
interface FormalItem { id: number; project_id: number; chapter_number: number; title: string; status: string; word_count: number; published_at: string | null; created_at: string; updated_at: string; }
interface FormalRead extends FormalItem { content: string; source_draft_id: number | null; }
interface ProfileSummary { genre: string; worldbuilding_pattern: string; writing_style_profile: string; target_novel_direction: string; }

export function DailyWriterPage() {
  const [pid, setPid] = useState<number>(() => Number(localStorage.getItem("selectedProjectId")) || 0);
  const [hasProfile, setHasProfile] = useState<boolean | null>(null);
  const [profileSummary, setProfileSummary] = useState<ProfileSummary | null>(null);
  const [drafts, setDrafts] = useState<DraftItem[]>([]);
  const [selDraft, setSelDraft] = useState<DraftRead | null>(null);
  const [formalChs, setFormalChs] = useState<FormalItem[]>([]);
  const [selFormal, setSelFormal] = useState<FormalRead | null>(null);
  const [tab, setTab] = useState<"generate" | "drafts" | "published">("generate");
  const [success, setSuccess] = useState<string | null>(null);

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
  const [deletingDraftId, setDeletingDraftId] = useState<number | null>(null);
  const [deletingFormalId, setDeletingFormalId] = useState<number | null>(null);

  const loadDrafts = useCallback(async () => {
    if (!pid) { setDrafts([]); return; }
    try { const r = await fetch(`${BASE}/api/daily-writer/chapters?project_id=${pid}`); if (r.ok) setDrafts(await r.json()); } catch { /* */ }
  }, [pid]);

  const loadFormal = useCallback(async () => {
    if (!pid) { setFormalChs([]); return; }
    try { const r = await fetch(`${BASE}/api/formal-chapters?project_id=${pid}`); if (r.ok) setFormalChs(await r.json()); } catch { /* */ }
  }, [pid]);

  useEffect(() => {
    if (!pid) { setDrafts([]); setSelDraft(null); setFormalChs([]); setSelFormal(null); setHasProfile(null); setProfileSummary(null); return; }
    setError(null); setSuccess(null);
    loadDrafts(); loadFormal();
    fetch(`${BASE}/api/reference-novels?project_id=${pid}`)
      .then(r => r.json()).then((ns: Array<{id:number}>) => ns.length>0 ? fetch(`${BASE}/api/reference-novels/${ns[0].id}/profile`).then(r=>r.json()) : Promise.reject())
      .then(p => { setHasProfile(!!p && !p.detail); setProfileSummary(p && !p.detail ? p : null); })
      .catch(() => { setHasProfile(false); setProfileSummary(null); });
  }, [pid, loadDrafts, loadFormal]);

  function setProject(n: number) { setPid(n); n>0 ? localStorage.setItem("selectedProjectId", String(n)) : localStorage.removeItem("selectedProjectId"); }

  function switchTab(t: "generate" | "drafts" | "published") { setTab(t); setError(null); setSuccess(null); }

  async function handleGenerate() {
    if (!pid) { setError("请先输入项目 ID"); return; }
    if (!Number.isInteger(cNum) || cNum < 1) { setError("请输入有效的章节编号（>= 1）"); return; }
    setGenLoading(true); setError(null); setSuccess(null);
    try {
      const r = await fetch(`${BASE}/api/daily-writer/generate`, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({project_id:pid, chapter_number:cNum, title, writing_goal:goal, extra_instruction:extra}) });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || `HTTP ${r.status}`);
      setTab("drafts"); setSelDraft(data.draft); setEditTitle(data.draft.title); setEditContent(data.draft.content); setSelFormal(null);
      setSuccess("章节草稿生成成功！可以在 Drafts 标签页编辑和发布。");
      loadDrafts();
    } catch(e) { setError(e instanceof Error ? e.message : "生成失败，请检查后端是否启动"); }
    finally { setGenLoading(false); }
  }

  async function viewDraft(id: number) {
    setSelFormal(null); setError(null); setSuccess(null);
    try { const r = await fetch(`${BASE}/api/daily-writer/chapters/${id}`); if (r.ok) { const d = await r.json(); setSelDraft(d); setEditTitle(d.title); setEditContent(d.content); } } catch { /* */ }
  }

  async function saveDraft() {
    if (!selDraft) return; setEditSaving(true); setError(null); setSuccess(null);
    try {
      const r = await fetch(`${BASE}/api/daily-writer/chapters/${selDraft.id}`, { method:"PATCH", headers:{"Content-Type":"application/json"}, body:JSON.stringify({title:editTitle, content:editContent}) });
      if (!r.ok) throw new Error((await r.json()).detail || `HTTP ${r.status}`);
      setSelDraft(await r.json()); loadDrafts();
      setSuccess("草稿已保存");
    } catch(e) { setError(e instanceof Error ? e.message : "保存失败"); }
    finally { setEditSaving(false); }
  }

  async function deleteDraft(id: number) {
    if (!confirm("确认删除此草稿？删除后不可恢复。")) return;
    setDeletingDraftId(id);
    setError(null); setSuccess(null);
    try {
      const r = await fetch(`${BASE}/api/daily-writer/chapters/${id}`, { method:"DELETE" });
      if (!r.ok) {
        const data = await r.json().catch(() => null) as { detail?: string } | null;
        throw new Error(data?.detail || `HTTP ${r.status}`);
      }
      if (selDraft?.id === id) setSelDraft(null);
      setSuccess("草稿已删除");
      loadDrafts();
    } catch(e) { setError(e instanceof Error ? e.message : "删除草稿失败"); }
    finally { setDeletingDraftId(null); }
  }

  async function publishDraft() {
    if (!selDraft) return; setPubLoading(true); setError(null); setSuccess(null);
    try {
      const r = await fetch(`${BASE}/api/formal-chapters/publish-draft/${selDraft.id}`, { method:"POST" });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || `HTTP ${r.status}`);
      setTab("published"); setSelFormal(data.chapter); setSelDraft(null); loadFormal();
      setSuccess("发布成功！草稿已转为正式章节（草稿保留）。");
    } catch(e) { setError(e instanceof Error ? e.message : "发布失败"); }
    finally { setPubLoading(false); }
  }

  async function viewFormal(id: number) {
    setSelDraft(null); setError(null); setSuccess(null);
    try { const r = await fetch(`${BASE}/api/formal-chapters/${id}`); if (r.ok) setSelFormal(await r.json()); } catch { /* */ }
  }

  async function deleteFormal(id: number) {
    if (!confirm("确认删除此正式章节？删除后不可恢复。")) return;
    setDeletingFormalId(id);
    setError(null); setSuccess(null);
    try {
      const r = await fetch(`${BASE}/api/formal-chapters/${id}`, { method:"DELETE" });
      if (!r.ok) {
        const data = await r.json().catch(() => null) as { detail?: string } | null;
        throw new Error(data?.detail || `HTTP ${r.status}`);
      }
      if (selFormal?.id === id) setSelFormal(null);
      setSuccess("正式章节已删除");
      loadFormal();
    } catch(e) { setError(e instanceof Error ? e.message : "删除正式章节失败"); }
    finally { setDeletingFormalId(null); }
  }

  function exportMarkdown() { if (pid) window.open(`${BASE}/api/exports/project/${pid}/markdown`); }
  function exportTxt() { if (pid) window.open(`${BASE}/api/exports/project/${pid}/txt`); }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4 flex-wrap">
        <h2 className="text-lg font-semibold">Daily Writer 每日写作</h2>
        <label className="flex items-center gap-2 text-xs text-slate-400">
          项目 ID <input type="number" min={1} value={pid||""} onChange={e=>setProject(Number(e.target.value)||0)} className="w-20 rounded border border-slate-700 bg-slate-800 px-2 py-1 text-sm text-white" placeholder="ID" />
        </label>
      </div>

      {!pid ? (
        <div className="rounded border border-dashed border-slate-700 p-10 text-center text-sm text-slate-500">
          请先输入项目 ID，然后在其他页面创建的项目 ID 会自动填入
        </div>
      ) : (
        <>
          <div className={`rounded border px-4 py-3 text-sm space-y-1 ${
            hasProfile===true ? "border-emerald-500/30 bg-emerald-500/10" :
            hasProfile===false ? "border-amber-500/30 bg-amber-500/10" :
            "border-slate-800 bg-slate-900"}`}>
            {hasProfile===null ? <span className="text-slate-500">正在检查参考创作画像...</span> :
             hasProfile===true ? <>
               <span className="text-emerald-400 font-medium">参考创作画像已接入</span>
               {profileSummary && (
                 <div className="text-xs text-slate-400 space-y-0.5 mt-1">
                   {profileSummary.genre && <div>类型：{profileSummary.genre.slice(0,80)}</div>}
                   {profileSummary.writing_style_profile && <div>风格：{profileSummary.writing_style_profile.slice(0,100)}</div>}
                   {profileSummary.target_novel_direction && <div>方向：{profileSummary.target_novel_direction.slice(0,120)}</div>}
                 </div>
               )}
             </> :
             <span className="text-amber-400">未接入参考创作画像（在 Ref Novels 页面添加和分析参考小说）</span>}
          </div>

          <div className="text-xs text-slate-600 flex items-center gap-1 flex-wrap">
            <span>工作流：</span>
            <span className={tab==="generate"?"text-cyan-400":""}>生成草稿</span>
            <span className="text-slate-600">→</span>
            <span className={tab==="drafts"?"text-cyan-400":""}>编辑草稿</span>
            <span className="text-slate-600">→</span>
            <span className={tab==="published"?"text-cyan-400":""}>发布章节</span>
            <span className="text-slate-600">→</span>
            <span>导出</span>
          </div>

          <div className="flex gap-2">
            {(["generate","drafts","published"] as const).map(t => (
              <button key={t} onClick={()=>switchTab(t)} className={`rounded px-3 py-1.5 text-xs font-medium transition ${
                tab===t?"bg-cyan-600 text-white":"border border-slate-700 text-slate-400 hover:text-white"}`}>
                {t==="generate"?`生成 (新章)` : t==="drafts"?`草稿 (${drafts.length})` : `已发布 (${formalChs.length})`}
              </button>
            ))}
          </div>

          {error && <div className="rounded border border-red-500/30 bg-red-500/5 px-4 py-3 text-sm text-red-400">{error}</div>}
          {success && <div className="rounded border border-emerald-500/30 bg-emerald-500/5 px-4 py-3 text-sm text-emerald-400">{success}</div>}

          {tab === "generate" && (
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-4 space-y-3">
              <h3 className="text-sm font-semibold">生成新章节草稿</h3>
              <div className="flex gap-3">
                <label className="flex-1 text-xs text-slate-500 space-y-1">
                  章节编号 <input type="number" value={cNum} onChange={e=>setCNum(Number(e.target.value)||1)} min={1} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" />
                </label>
                <label className="flex-[3] text-xs text-slate-500 space-y-1">
                  章节标题（可选） <input value={title} onChange={e=>setTitle(e.target.value)} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" placeholder="如：新的开始" />
                </label>
              </div>
              <label className="block text-xs text-slate-500 space-y-1">
                写作目标（可选） <textarea value={goal} onChange={e=>setGoal(e.target.value)} rows={2} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" placeholder="本章要推进什么剧情？完成什么目标？" />
              </label>
              <label className="block text-xs text-slate-500 space-y-1">
                额外说明（可选） <textarea value={extra} onChange={e=>setExtra(e.target.value)} rows={2} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" placeholder="对 AI 写作的特殊要求、风格偏好等" />
              </label>
              <button onClick={handleGenerate} disabled={genLoading} className="rounded bg-cyan-600 px-5 py-2 text-sm font-medium text-white hover:bg-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed transition">
                {genLoading ? "正在生成..." : "生成章节草稿"}
              </button>
            </div>
          )}

          <div className="grid gap-4 lg:grid-cols-5">
            <div className="space-y-2 lg:col-span-2">
              {tab === "drafts" && (
                <>
                  <h3 className="text-sm font-semibold text-slate-300">草稿列表</h3>
                  {drafts.length===0 ? <p className="text-xs text-slate-600">暂无草稿，请先在生成标签页创建</p> : drafts.map(d=>(
                    <div key={d.id} onClick={()=>viewDraft(d.id)} className={`cursor-pointer rounded border p-3 text-sm transition ${
                      selDraft?.id===d.id?"border-cyan-500 bg-cyan-500/10":"border-slate-800 bg-slate-900 hover:border-slate-700"}`}>
                      <div className="font-medium">#{d.chapter_number} {d.title||"未命名"}</div>
                      <div className="text-xs text-slate-500 mt-1">{d.status} · {new Date(d.created_at).toLocaleDateString("zh-CN")}</div>
                    </div>
                  ))}
                </>
              )}
              {tab === "published" && (
                <>
                  <h3 className="text-sm font-semibold text-slate-300">已发布章节</h3>
                  <div className="flex gap-2 mb-2">
                    <button onClick={exportMarkdown} disabled={formalChs.length===0} className="text-xs text-cyan-400 hover:underline disabled:text-slate-600 disabled:no-underline">导出 MD</button>
                    <button onClick={exportTxt} disabled={formalChs.length===0} className="text-xs text-cyan-400 hover:underline disabled:text-slate-600 disabled:no-underline">导出 TXT</button>
                  </div>
                  {formalChs.length===0 ? <p className="text-xs text-slate-600">暂无已发布章节，请编辑草稿后发布</p> : formalChs.map(c=>(
                    <div key={c.id} onClick={()=>viewFormal(c.id)} className={`cursor-pointer rounded border p-3 text-sm transition ${
                      selFormal?.id===c.id?"border-emerald-500 bg-emerald-500/10":"border-slate-800 bg-slate-900 hover:border-slate-700"}`}>
                      <div className="font-medium">#{c.chapter_number} {c.title||"未命名"}</div>
                      <div className="text-xs text-slate-500 mt-1">{c.word_count} 字 · {c.published_at ? new Date(c.published_at).toLocaleDateString("zh-CN") : "-"}</div>
                    </div>
                  ))}
                </>
              )}
            </div>

            <div className="lg:col-span-3">
              {selDraft && (
                <div className="rounded-lg border border-cyan-500/20 bg-slate-900 p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold">草稿 #{selDraft.chapter_number} {selDraft.title||"未命名"}</h3>
                    <div className="flex gap-2">
                      <button onClick={saveDraft} disabled={editSaving} className="rounded bg-cyan-600 px-3 py-1 text-xs text-white hover:bg-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed transition">
                        {editSaving ? "保存中..." : "保存草稿"}
                      </button>
                      <button onClick={publishDraft} disabled={pubLoading} className="rounded bg-emerald-600 px-3 py-1 text-xs text-white hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition">
                        {pubLoading ? "发布中..." : "发布为正式章节"}
                      </button>
                      <button onClick={()=>deleteDraft(selDraft.id)} disabled={editSaving||pubLoading||deletingDraftId===selDraft.id} className="text-xs text-red-400 hover:underline disabled:text-slate-600 disabled:no-underline disabled:cursor-not-allowed">
                        {deletingDraftId===selDraft.id ? "删除中..." : "删除"}
                      </button>
                    </div>
                  </div>
                  <label className="block text-xs text-slate-500 space-y-1">
                    标题 <input value={editTitle} onChange={e=>setEditTitle(e.target.value)} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" />
                  </label>
                  <label className="block text-xs text-slate-500 space-y-1">
                    正文 <textarea value={editContent} onChange={e=>setEditContent(e.target.value)} rows={16} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white font-mono leading-relaxed resize-y" />
                  </label>
                  <p className="text-xs text-slate-600">在此编辑草稿标题和正文。点击"保存草稿"保存修改。点击"发布为正式章节"将其转为正式章节（草稿会保留，正式章节不会被覆盖）。</p>
                </div>
              )}
              {selFormal && !selDraft && (
                <div className="rounded-lg border border-emerald-500/30 bg-slate-900 p-5">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold">#{selFormal.chapter_number} {selFormal.title||"章节"} <span className="text-xs text-emerald-400 font-normal">已发布</span></h3>
                    <button onClick={()=>deleteFormal(selFormal.id)} disabled={deletingFormalId===selFormal.id} className="text-xs text-red-400 hover:underline disabled:text-slate-600 disabled:no-underline disabled:cursor-not-allowed">
                      {deletingFormalId===selFormal.id ? "删除中..." : "删除"}
                    </button>
                  </div>
                  <div className="max-h-96 overflow-y-auto rounded bg-slate-950 p-4">
                    <pre className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">{selFormal.content}</pre>
                  </div>
                  <p className="text-xs text-slate-600 mt-3">{selFormal.word_count} 字 · 发布于 {selFormal.published_at ? new Date(selFormal.published_at).toLocaleDateString("zh-CN") : "-"}</p>
                </div>
              )}
              {!selDraft && !selFormal && (
                <div className="rounded border border-dashed border-slate-700 p-10 text-center text-sm text-slate-600">
                  从左侧列表选择草稿或已发布章节查看
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
