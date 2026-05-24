import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { getProjects, createProject, deleteProject } from "../api/client";
import type { Project } from "../types/api";
import { LoadingState, ErrorState, EmptyState } from "../components/LoadingState";
import { formatDate, statusBadge } from "../utils/format";

export function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const navigate = useNavigate();

  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try { setProjects(await getProjects()); } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  async function handleCreate(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    try {
      await createProject({
        title: fd.get("title") as string,
        genre: fd.get("genre") as string,
        description: fd.get("description") as string,
      });
      setShowForm(false);
      load();
    } catch (err) {
      alert(err instanceof Error ? err.message : "创建失败");
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("确认删除此项目？关联的角色和章节不会自动删除。")) return;
    try { await deleteProject(id); load(); } catch (err) {
      alert(err instanceof Error ? err.message : "删除失败");
    }
  }

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">项目管理</h2>
        <button onClick={() => setShowForm(!showForm)}
          className="rounded bg-cyan-600 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-700 transition">
          {showForm ? "取消" : "+ 新建项目"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="rounded-lg border border-slate-800 bg-slate-900 p-4 space-y-3">
          <input name="title" placeholder="项目标题 *" required className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" />
          <input name="genre" placeholder="类型（如：都市、奇幻）" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" />
          <textarea name="description" placeholder="项目简介" rows={2} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" />
          <button type="submit" className="rounded bg-cyan-600 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-700">创建</button>
        </form>
      )}

      {projects.length === 0 ? <EmptyState text="还没有项目，点击上方按钮创建第一个" /> : (
        <div className="grid gap-3">
          {projects.map((p) => (
            <div key={p.id} className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900 p-4">
              <div className="flex-1 min-w-0 cursor-pointer" onClick={() => navigate(`/projects/${p.id}`)}>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-white truncate">{p.title}</span>
                  <span className={`rounded px-2 py-0.5 text-xs ${statusBadge(p.status)}`}>{p.status}</span>
                </div>
                <div className="mt-1 text-xs text-slate-500">{p.genre || "未分类"} · {p.description?.slice(0, 60) || "暂无简介"}</div>
                <div className="mt-1 text-xs text-slate-600">创建于 {formatDate(p.created_at)}</div>
              </div>
              <button onClick={() => handleDelete(p.id)}
                className="ml-3 rounded px-3 py-1 text-xs text-red-400 hover:bg-red-500/10 transition">删除</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
