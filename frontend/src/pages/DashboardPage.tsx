import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export function DashboardPage() {
  const [pid, setPid] = useState<number>(() => Number(localStorage.getItem("selectedProjectId")) || 0);
  const [summary, setSummary] = useState<any>(null);
  const [health, setHealth] = useState<string>("checking...");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${BASE}/health`).then(r=>r.json()).then(d=>setHealth(d.status==="ok"?"在线":"异常")).catch(()=>setHealth("不可达"));
    if (!pid) return;
    fetch(`${BASE}/api/project-dashboard/summary?project_id=${pid}`)
      .then(r=>r.json()).then(setSummary).catch(()=>setError("项目摘要加载失败"));
  }, [pid]);

  function setProject(n: number) { setPid(n); if(n>0) localStorage.setItem("selectedProjectId",String(n)); else localStorage.removeItem("selectedProjectId"); }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4 flex-wrap">
        <h2 className="text-lg font-semibold">Dashboard</h2>
        <label className="flex items-center gap-2 text-xs text-slate-400">
          项目 ID <input type="number" min={1} value={pid||""} onChange={e=>setProject(Number(e.target.value)||0)} className="w-20 rounded border border-slate-700 bg-slate-800 px-2 py-1 text-sm text-white" />
        </label>
        <span className={`text-xs px-2 py-0.5 rounded ${health==="在线"?"bg-emerald-500/20 text-emerald-400":"bg-red-500/20 text-red-400"}`}>后端 {health}</span>
      </div>

      {!pid ? (
        <div className="rounded border border-dashed border-slate-700 p-10 text-center text-sm text-slate-500">输入项目 ID 查看摘要（从其他页面创建的项目 ID 会自动填入）</div>
      ) : !summary ? (
        error ? <div className="text-sm text-red-400">{error}</div> : <div className="text-sm text-slate-500">加载中...</div>
      ) : (
        <>
          <div className="grid gap-3 sm:grid-cols-3 md:grid-cols-4">
            <Stat label="故事圣经" v={summary.has_story_bible?"已建立":"未建立"} color={summary.has_story_bible?"emerald":"slate"} />
            <Stat label="参考画像" v={summary.has_reference_profile?"已接入":"未接入"} color={summary.has_reference_profile?"emerald":"slate"} />
            <Stat label="人物卡" v={summary.character_card_count} color="cyan" />
            <Stat label="世界观条目" v={summary.world_entry_count} color="cyan" />
            <Stat label="章节计划" v={summary.chapter_plan_count} color="cyan" />
            <Stat label="草稿" v={summary.draft_count} color="amber" />
            <Stat label="正式章节" v={summary.formal_chapter_count} color="emerald" />
            <Stat label="下一章" v={`#${summary.next_chapter_number}`} color="purple" />
            <Stat label="章节摘要" v={summary.chapter_summary_count} color="cyan" />
            <Stat label="未解决伏笔" v={summary.open_plot_thread_count} color={summary.open_plot_thread_count>0?"amber":"slate"} />
            <Stat label="质量检查" v={summary.review_count} color="cyan" />
            <Stat label="AI 调用" v={summary.usage_call_count} color="purple" />
            {summary.estimated_total_cost > 0 && <Stat label="估算成本" v={`$${Number(summary.estimated_total_cost).toFixed(6)}`} color="slate" />}
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
            <h3 className="text-sm font-semibold mb-3">V1 工作流入口</h3>
            <div className="grid gap-3 sm:grid-cols-3">
              <Entry to="/reference-novels" title="参考小说分析" desc="添加参考小说，提取抽象创作画像" />
              <Entry to="/story-bible" title="故事圣经" desc="管理世界观、人物卡、章节计划、伏笔" />
              <Entry to="/daily-writer" title="Daily Writer" desc="生成草稿、编辑、质量检查、发布正式章节" />
              <Entry to="/model-settings" title="AI 设置" desc="配置 Provider、模型、查看用量和成本" />
              <Entry to="/projects" title="项目管理" desc="创建和管理小说项目" />
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function Stat({ label, v, color }: { label: string; v: string|number; color: string }) {
  const cc: Record<string,string> = {emerald:"text-emerald-400",cyan:"text-cyan-400",amber:"text-amber-400",purple:"text-purple-400",slate:"text-slate-400"};
  return <div className="rounded border border-slate-800 bg-slate-900 p-3 text-center">
    <div className="text-xs text-slate-500">{label}</div>
    <div className={`text-lg font-semibold mt-1 ${cc[color]||"text-slate-300"}`}>{v}</div>
  </div>;
}

function Entry({ to, title, desc }: { to: string; title: string; desc: string }) {
  return <Link to={to} className="rounded border border-slate-700 p-3 hover:border-cyan-500/50 transition text-sm">
    <div className="text-cyan-400 font-medium">{title}</div>
    <div className="text-xs text-slate-500 mt-1">{desc}</div>
  </Link>;
}
