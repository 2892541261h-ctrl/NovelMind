import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { healthCheck, testAI, getProjects } from "../api/client";
import type { HealthResponse } from "../types/api";
import { LoadingState, ErrorState } from "../components/LoadingState";

export function DashboardPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [aiStatus, setAiStatus] = useState<string | null>(null);
  const [projectCount, setProjectCount] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [h, ai, projs] = await Promise.all([
        healthCheck(),
        testAI(),
        getProjects(),
      ]);
      setHealth(h);
      setAiStatus(ai.error ? `Mock 异常: ${ai.error}` : "Mock 正常");
      setProjectCount(projs.length);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  if (loading) return <LoadingState text="正在连接后端..." />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <QuickCard label="后端状态" value={health?.status === "ok" ? "在线" : "异常"}
          color={health?.status === "ok" ? "text-emerald-400" : "text-red-400"} />
        <QuickCard label="AI Gateway" value={aiStatus ?? "-"} color="text-cyan-400" />
        <QuickCard label="项目数量" value={String(projectCount)} color="text-amber-400" />
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
        <h2 className="text-base font-semibold mb-3">快速入口</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          <Link to="/projects" className="rounded border border-slate-700 p-4 hover:border-cyan-500/50 transition text-sm">
            <span className="text-cyan-400 font-medium">项目管理</span>
            <p className="text-slate-500 mt-1">创建和管理小说项目</p>
          </Link>
          <Link to="/characters" className="rounded border border-slate-700 p-4 hover:border-cyan-500/50 transition text-sm">
            <span className="text-cyan-400 font-medium">角色管理</span>
            <p className="text-slate-500 mt-1">设计小说角色和人物关系</p>
          </Link>
          <Link to="/chapters" className="rounded border border-slate-700 p-4 hover:border-cyan-500/50 transition text-sm">
            <span className="text-cyan-400 font-medium">章节管理</span>
            <p className="text-slate-500 mt-1">撰写和管理章节内容</p>
          </Link>
          <Link to="/story-bible" className="rounded border border-slate-700 p-4 hover:border-cyan-500/50 transition text-sm">
            <span className="text-cyan-400 font-medium">故事圣经</span>
            <p className="text-slate-500 mt-1">管理世界观和设定规则</p>
          </Link>
        </div>
      </div>
    </div>
  );
}

function QuickCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
      <div className="text-xs text-slate-500 mb-1">{label}</div>
      <div className={`text-lg font-semibold ${color}`}>{value}</div>
    </div>
  );
}
