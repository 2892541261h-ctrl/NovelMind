import { useEffect, useState, useCallback } from "react";
import { getProjects, getProjectChapters, createChapter, deleteChapter } from "../api/client";
import type { Project, Chapter } from "../types/api";
import { LoadingState, ErrorState, EmptyState } from "../components/LoadingState";
import { statusBadge } from "../utils/format";

export function ChaptersPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedId, setSelectedId] = useState<number>(() => Number(localStorage.getItem("selectedProjectId")) || 0);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  const loadProjects = useCallback(async () => {
    try { setProjects(await getProjects()); } catch { /* ignore */ }
  }, []);

  const loadChapters = useCallback(async (pid: number) => {
    if (!pid) { setChapters([]); setLoading(false); return; }
    setLoading(true); setError(null);
    try { setChapters(await getProjectChapters(pid)); } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { loadProjects(); }, [loadProjects]);
  useEffect(() => { loadChapters(selectedId); }, [selectedId, loadChapters]);

  function selectProject(id: number) {
    setSelectedId(id);
    localStorage.setItem("selectedProjectId", String(id));
  }

  async function handleCreate(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    try {
      await createChapter(selectedId, {
        project_id: selectedId,
        chapter_number: Number(fd.get("chapter_number")) || 0,
        title: fd.get("title") as string,
        goal: fd.get("goal") as string,
        summary: fd.get("summary") as string,
      });
      setShowForm(false);
      loadChapters(selectedId);
    } catch (err) { alert(err instanceof Error ? err.message : "创建失败"); }
  }

  async function handleDelete(chId: number) {
    if (!confirm("确认删除？")) return;
    try { await deleteChapter(chId); loadChapters(selectedId); } catch (err) {
      alert(err instanceof Error ? err.message : "删除失败");
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold">章节管理</h2>
        <select value={selectedId || ""} onChange={(e) => selectProject(Number(e.target.value))}
          className="rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white">
          <option value="">-- 选择项目 --</option>
          {projects.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
        </select>
        {selectedId > 0 && (
          <button onClick={() => setShowForm(!showForm)}
            className="rounded bg-cyan-600 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-700">
            {showForm ? "取消" : "+ 新建章节"}
          </button>
        )}
      </div>

      {!selectedId ? <EmptyState text="请先选择一个项目" /> : (
        <>
          {showForm && (
            <form onSubmit={handleCreate} className="rounded-lg border border-slate-800 bg-slate-900 p-4 space-y-3">
              <div className="flex gap-3">
                <input name="chapter_number" type="number" placeholder="章节编号" className="w-32 rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" />
                <input name="title" placeholder="章节标题 *" required className="flex-1 rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" />
              </div>
              <input name="goal" placeholder="本章目标" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" />
              <textarea name="summary" placeholder="章节摘要" rows={2} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" />
              <button type="submit" className="rounded bg-cyan-600 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-700">创建</button>
            </form>
          )}
          {loading ? <LoadingState /> :
           error ? <ErrorState message={error} onRetry={() => loadChapters(selectedId)} /> :
           chapters.length === 0 ? <EmptyState text="还没有章节" /> : (
            <div className="grid gap-3">
              {chapters.map((c) => (
                <div key={c.id} className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900 p-4">
                  <div>
                    <span className="text-xs text-slate-500 mr-2">#{c.chapter_number}</span>
                    <span className="font-medium">{c.title}</span>
                    <span className={`ml-2 rounded px-2 py-0.5 text-xs ${statusBadge(c.status)}`}>{c.status}</span>
                    {c.goal && <p className="mt-1 text-xs text-slate-400">目标：{c.goal}</p>}
                    {c.summary && <p className="mt-1 text-xs text-slate-500">{c.summary.slice(0, 80)}{c.summary.length > 80 ? "..." : ""}</p>}
                  </div>
                  <button onClick={() => handleDelete(c.id)} className="ml-3 text-xs text-red-400 hover:underline">删除</button>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
