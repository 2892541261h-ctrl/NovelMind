import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getProject } from "../api/client";
import type { Project } from "../types/api";
import { LoadingState, ErrorState } from "../components/LoadingState";
import { formatDate, statusBadge } from "../utils/format";

export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const id = Number(projectId);

  useEffect(() => {
    if (!id) return;
    setLoading(true); setError(null);
    getProject(id).then(setProject).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!project) return <ErrorState message="项目不存在" />;

  function setSelectedProject(projectId: number): void {
    localStorage.setItem("selectedProjectId", String(projectId));
  }

  return (
    <div className="space-y-4">
      <Link to="/projects" className="text-sm text-cyan-400 hover:underline">&larr; 返回项目列表</Link>
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
        <div className="flex items-center gap-3 mb-4">
          <h2 className="text-xl font-bold">{project.title}</h2>
          <span className={`rounded px-2 py-0.5 text-xs ${statusBadge(project.status)}`}>{project.status}</span>
        </div>
        <dl className="grid gap-3 text-sm sm:grid-cols-2">
          <div><dt className="text-slate-500">类型</dt><dd>{project.genre || "-"}</dd></div>
          <div><dt className="text-slate-500">目标字数</dt><dd>{project.target_word_count.toLocaleString() || "-"}</dd></div>
          <div className="sm:col-span-2"><dt className="text-slate-500">简介</dt><dd className="mt-1 text-slate-300">{project.description || "暂无简介"}</dd></div>
          <div><dt className="text-slate-500">创建时间</dt><dd className="text-slate-400">{formatDate(project.created_at)}</dd></div>
          <div><dt className="text-slate-500">更新时间</dt><dd className="text-slate-400">{formatDate(project.updated_at)}</dd></div>
        </dl>
      </div>
      <div className="flex gap-3">
        <Link
          to="/characters"
          onClick={() => setSelectedProject(project.id)}
          className="rounded bg-cyan-600 px-4 py-2 text-sm text-white hover:bg-cyan-700"
        >
          管理角色
        </Link>
        <Link
          to="/chapters"
          onClick={() => setSelectedProject(project.id)}
          className="rounded border border-cyan-600 px-4 py-2 text-sm text-cyan-400 hover:bg-cyan-600/10"
        >
          管理章节
        </Link>
      </div>
    </div>
  );
}
