import { useEffect, useState, useCallback } from "react";
import { getProjects, getProjectCharacters, createCharacter, deleteCharacter } from "../api/client";
import type { Project, Character } from "../types/api";
import { LoadingState, ErrorState, EmptyState } from "../components/LoadingState";
import { statusBadge } from "../utils/format";

export function CharactersPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedId, setSelectedId] = useState<number>(() => Number(localStorage.getItem("selectedProjectId")) || 0);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  const loadProjects = useCallback(async () => {
    try { setProjects(await getProjects()); } catch { /* ignore */ }
  }, []);

  const loadChars = useCallback(async (pid: number) => {
    if (!pid) { setCharacters([]); setLoading(false); return; }
    setLoading(true); setError(null);
    try { setCharacters(await getProjectCharacters(pid)); } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { loadProjects(); }, [loadProjects]);
  useEffect(() => { loadChars(selectedId); }, [selectedId, loadChars]);

  function selectProject(id: number) {
    setSelectedId(id);
    localStorage.setItem("selectedProjectId", String(id));
  }

  async function handleCreate(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    try {
      await createCharacter(selectedId, {
        project_id: selectedId,
        name: fd.get("name") as string,
        role_type: fd.get("role_type") as string,
        personality: fd.get("personality") as string,
        goal: fd.get("goal") as string,
      });
      setShowForm(false);
      loadChars(selectedId);
    } catch (err) { alert(err instanceof Error ? err.message : "创建失败"); }
  }

  async function handleDelete(charId: number) {
    if (!confirm("确认删除？")) return;
    try { await deleteCharacter(charId); loadChars(selectedId); } catch (err) {
      alert(err instanceof Error ? err.message : "删除失败");
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold">角色管理</h2>
        <select value={selectedId || ""} onChange={(e) => selectProject(Number(e.target.value))}
          className="rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white">
          <option value="">-- 选择项目 --</option>
          {projects.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
        </select>
        {selectedId > 0 && (
          <button onClick={() => setShowForm(!showForm)}
            className="rounded bg-cyan-600 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-700">
            {showForm ? "取消" : "+ 新建角色"}
          </button>
        )}
      </div>

      {!selectedId ? <EmptyState text="请先选择一个项目" /> : (
        <>
          {showForm && (
            <form onSubmit={handleCreate} className="rounded-lg border border-slate-800 bg-slate-900 p-4 space-y-3">
              <input name="name" placeholder="角色名称 *" required className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" />
              <input name="role_type" placeholder="角色类型（主角/配角/反派）" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" />
              <input name="personality" placeholder="性格特点" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" />
              <textarea name="goal" placeholder="角色目标" rows={2} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500" />
              <button type="submit" className="rounded bg-cyan-600 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-700">创建</button>
            </form>
          )}
          {loading ? <LoadingState /> :
           error ? <ErrorState message={error} onRetry={() => loadChars(selectedId)} /> :
           characters.length === 0 ? <EmptyState text="还没有角色" /> : (
            <div className="grid gap-3">
              {characters.map((c) => (
                <div key={c.id} className="rounded-lg border border-slate-800 bg-slate-900 p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="font-medium">{c.name}</span>
                      {c.role_type && <span className={`ml-2 rounded px-2 py-0.5 text-xs ${statusBadge(c.status)}`}>{c.role_type}</span>}
                    </div>
                    <button onClick={() => handleDelete(c.id)} className="text-xs text-red-400 hover:underline">删除</button>
                  </div>
                  {c.personality && <p className="mt-1 text-xs text-slate-400">性格：{c.personality}</p>}
                  {c.goal && <p className="mt-1 text-xs text-slate-500">目标：{c.goal}</p>}
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
