import { useEffect, useState, useCallback } from "react";
import { getBaseUrl, getProjects } from "../api/client";
import type { Project } from "../types/api";
import { LoadingState, ErrorState, EmptyState } from "../components/LoadingState";

const BASE = getBaseUrl();

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
  const [success, setSuccess] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [creating, setCreating] = useState(false);

  const loadProjects = useCallback(async () => {
    try { setProjects(await getProjects()); } catch { /* */ }
  }, []);

  const loadNovels = useCallback(async (pid: number) => {
    if (!pid) return;
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${BASE}/api/reference-novels?project_id=${pid}`);
      if (!res.ok) throw new Error(await res.text());
      setNovels(await res.json());
    } catch (e) { setError(e instanceof Error ? e.message : "加载失败"); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { loadProjects(); }, [loadProjects]);
  useEffect(() => { loadNovels(selectedId); }, [selectedId, loadNovels]);

  function selectProject(id: number) { setSelectedId(id); localStorage.setItem("selectedProjectId", String(id)); setSelectedNovel(null); setProfile(null); setError(null); setSuccess(null); }

  async function handleCreate(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    setCreating(true); setError(null);
    try {
      const res = await fetch(`${BASE}/api/reference-novels`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: selectedId, title: fd.get("title"), author: fd.get("author"), content: fd.get("content"), source_type: "paste" }),
      });
      if (!res.ok) throw new Error(await res.text());
      (e.target as HTMLFormElement).reset();
      setShowForm(false);
      setSuccess("参考小说已保存");
      loadNovels(selectedId);
    } catch (err) { setError(err instanceof Error ? err.message : "保存失败"); }
    finally { setCreating(false); }
  }

  async function handleDelete(novelId: number) {
    if (!confirm("确认删除此参考小说？相关的分析画像也会被删除。")) return;
    setError(null); setSuccess(null);
    await fetch(`${BASE}/api/reference-novels/${novelId}`, { method: "DELETE" });
    loadNovels(selectedId);
    if (selectedNovel?.id === novelId) { setSelectedNovel(null); setProfile(null); }
  }

  async function handleAnalyze(novelId: number) {
    setAnalyzing(true); setError(null); setSuccess(null);
    try {
      const res = await fetch(`${BASE}/api/reference-novels/${novelId}/analyze`, { method: "POST" });
      if (!res.ok) throw new Error(await res.text());
      setProfile(await res.json());
      setSuccess("分析完成！创作画像已生成，可在 Daily Writer 中使用。");
    } catch (err) { setError(err instanceof Error ? err.message : "分析失败"); }
    finally { setAnalyzing(false); }
  }

  async function selectNovel(novel: RefNovel) {
    setSelectedNovel(novel); setProfile(null); setError(null); setSuccess(null);
    try {
      const res = await fetch(`${BASE}/api/reference-novels/${novel.id}/profile`);
      if (res.ok) setProfile(await res.json());
    } catch { /* */ }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4 flex-wrap">
        <h2 className="text-lg font-semibold">参考小说分析</h2>
        <select value={selectedId || ""} onChange={(e) => selectProject(Number(e.target.value))}
          className="rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white">
          <option value="">-- 选择项目 --</option>
          {projects.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
        </select>
        {selectedId > 0 && (
          <button onClick={() => setShowForm(!showForm)} disabled={creating}
            className="rounded bg-cyan-600 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed transition">
            {showForm ? "取消" : "+ 添加参考小说"}
          </button>
        )}
      </div>

      <p className="text-xs text-slate-500 leading-relaxed">
        参考小说用于提取抽象创作规律（类型、世界观、人物原型、冲突模式、写作风格、情节推进）。
        <strong className="text-amber-400"> 不是续写、不是复制、不是改写。</strong> 提取的画像用于指导你的原创小说创作。
      </p>

      {error && <div className="rounded border border-red-500/30 bg-red-500/5 px-4 py-3 text-sm text-red-400">{error}</div>}
      {success && <div className="rounded border border-emerald-500/30 bg-emerald-500/5 px-4 py-3 text-sm text-emerald-400">{success}</div>}

      {!selectedId ? <EmptyState text="请先选择项目" /> : (
        <>
          {showForm && (
            <form onSubmit={handleCreate} className="rounded-lg border border-slate-800 bg-slate-900 p-4 space-y-3">
              <label className="block text-xs text-slate-500 space-y-1">
                参考小说标题 <input name="title" required className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" placeholder="用于标识的标题" />
              </label>
              <label className="block text-xs text-slate-500 space-y-1">
                作者（可选） <input name="author" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" placeholder="原作者名" />
              </label>
              <label className="block text-xs text-slate-500 space-y-1">
                参考文本 <textarea name="content" rows={8} required className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500 font-mono" placeholder="在此粘贴参考小说文本（仅用于分析，不会被发布或引用）" />
              </label>
              <button type="submit" disabled={creating}
                className="rounded bg-cyan-600 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed transition">
                {creating ? "保存中..." : "保存"}
              </button>
            </form>
          )}

          {loading ? <LoadingState /> :
           novels.length === 0 && !showForm ? <EmptyState text="暂无参考小说，点击上方按钮添加" /> : (
            <div className="grid gap-3 lg:grid-cols-3">
              <div className="space-y-2 lg:col-span-1">
                {novels.map((n) => (
                  <div key={n.id} onClick={() => selectNovel(n)}
                    className={`cursor-pointer rounded border p-3 text-sm transition ${selectedNovel?.id === n.id ? "border-cyan-500 bg-cyan-500/10" : "border-slate-800 bg-slate-900 hover:border-slate-700"}`}>
                    <div className="font-medium truncate">{n.title || "未命名"}</div>
                    <div className="text-xs text-slate-500 mt-1">{n.author || "未知作者"} · {n.content.length} 字</div>
                    <button onClick={(e) => { e.stopPropagation(); handleDelete(n.id); }} className="mt-2 text-xs text-red-400 hover:underline">删除</button>
                  </div>
                ))}
              </div>

              <div className="space-y-3 lg:col-span-2">
                {selectedNovel && (
                  <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold">{selectedNovel.title || "未命名"}</h3>
                      <button onClick={() => handleAnalyze(selectedNovel.id)} disabled={analyzing}
                        className="rounded bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition">
                        {analyzing ? "分析中..." : "分析生成创作画像"}
                      </button>
                    </div>

                    <div className="max-h-40 overflow-y-auto rounded bg-slate-950 p-3 mb-4">
                      <pre className="text-xs text-slate-400 whitespace-pre-wrap">{selectedNovel.content.slice(0, 1000)}{selectedNovel.content.length > 1000 ? "..." : ""}</pre>
                    </div>

                    {profile ? (
                      <div className="space-y-3">
                        <h4 className="text-sm font-semibold text-cyan-400">参考创作画像</h4>
                        <Field label="类型" value={profile.genre} />
                        <Field label="世界观构建" value={profile.worldbuilding_pattern} />
                        <Field label="人物原型" value={profile.character_archetypes} />
                        <Field label="冲突模式" value={profile.conflict_patterns} />
                        <Field label="写作风格" value={profile.writing_style_profile} />
                        <Field label="情节推进" value={profile.plot_progression_model} />
                        <Field label="创作方向" value={profile.target_novel_direction} />
                        <div className="text-xs text-slate-600">置信度: {profile.confidence} · 状态: {profile.status}</div>
                        <p className="text-xs text-amber-400">以上为抽象创作规律，不含参考小说原文、角色名或具体情节。可用于指导原创写作。</p>
                      </div>
                    ) : (
                      <p className="text-xs text-slate-500 leading-relaxed">
                        点击"分析生成创作画像"按钮，AI 将读取参考小说文本并提取抽象创作规律。
                        分析通过 backend/ai/gateway.py 调用（当前为 mock 模式）。
                        提取的画像可用于 Daily Writer 的原创写作指导。
                      </p>
                    )}
                  </div>
                )}
                {!selectedNovel && novels.length > 0 && (
                  <div className="rounded border border-dashed border-slate-700 p-10 text-center text-sm text-slate-600">
                    从左侧列表选择参考小说查看详情
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
      <div className="text-sm text-slate-300 leading-relaxed">{value.slice(0, 300)}{value.length > 300 ? "..." : ""}</div>
    </div>
  );
}
