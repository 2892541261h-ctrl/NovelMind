import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export function DashboardPage() {
  const [pid, setPid] = useState<number>(() => Number(localStorage.getItem("selectedProjectId")) || 0);
  const [s, setS] = useState<any>(null);
  const [health, setHealth] = useState("checking...");

  useEffect(() => {
    fetch(`${BASE}/health`).then(r=>r.json()).then(d=>setHealth(d.status==="ok"?"在线":"异常")).catch(()=>setHealth("不可达"));
    if (!pid) return;
    fetch(`${BASE}/api/project-dashboard/summary?project_id=${pid}`).then(r=>r.json()).then(setS).catch(()=>{});
  }, [pid]);

  function setProject(n: number) { setPid(n); n>0?localStorage.setItem("selectedProjectId",String(n)):localStorage.removeItem("selectedProjectId"); }

  return (
    <div style={{maxWidth:960}} className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-xl font-bold" style={{color:"var(--text-primary)"}}>下午好，创作者</h2>
          <p className="text-sm mt-1" style={{color:"var(--text-muted)"}}>继续你的创作之旅。</p>
        </div>
        <label className="flex items-center gap-2 text-sm" style={{color:"var(--text-secondary)"}}>
          当前项目
          <input type="number" min={1} value={pid||""} onChange={e=>setProject(Number(e.target.value)||0)}
            className="!w-20" placeholder="ID" />
          <span className="badge" style={{background:health==="在线"?"var(--emerald-bg)":"var(--red-bg)",color:health==="在线"?"var(--emerald-text)":"var(--red-text)"}}>{health}</span>
        </label>
      </div>

      {!pid ? (
        <div className="empty-state">输入项目 ID 查看创作进度</div>
      ) : !s ? (
        <div className="text-sm" style={{color:"var(--text-muted)"}}>加载中...</div>
      ) : (
        <>
          <div className="grid gap-3" style={{gridTemplateColumns:"repeat(auto-fill,minmax(120px,1fr))"}}>
            <Stat label="章节计划" v={s.chapter_plan_count||0} color="var(--purple-text)" bg="var(--purple-bg)" />
            <Stat label="正式章节" v={s.formal_chapter_count||0} color="var(--emerald-text)" bg="var(--emerald-bg)" />
            <Stat label="草稿" v={s.draft_count||0} color="var(--amber-text)" bg="var(--amber-bg)" />
            <Stat label="人物卡" v={s.character_card_count||0} color="var(--cyan-text)" bg="var(--cyan-bg)" />
            <Stat label="伏笔" v={s.open_plot_thread_count||0} color={s.open_plot_thread_count>0?"var(--amber-text)":"var(--text-muted)"} bg={s.open_plot_thread_count>0?"var(--amber-bg)":"transparent"} />
            <Stat label="AI 调用" v={s.usage_call_count||0} color="var(--purple-text)" bg="var(--purple-bg)" />
            {s.estimated_total_cost>0 && <Stat label="估算成本" v={`$${Number(s.estimated_total_cost).toFixed(4)}`} color="var(--text-secondary)" bg="transparent" />}
            <Stat label="下一章" v={`#${s.next_chapter_number||1}`} color="var(--accent)" bg="transparent" />
            <Stat label="故事圣经" v={s.has_story_bible?"已建立":"未建立"} color={s.has_story_bible?"var(--emerald-text)":"var(--text-muted)"} bg={s.has_story_bible?"var(--emerald-bg)":"transparent"} />
          </div>

          <div className="grid gap-4" style={{gridTemplateColumns:"2fr 1fr"}}>
            <div className="card space-y-4">
              <h3 className="font-semibold" style={{color:"var(--text-primary)"}}>下一步建议</h3>
              <div className="space-y-2">
                <Hint to="/story-bible" label="完善故事设定" desc="建立世界观、人物卡和伏笔线索" badge={s.has_story_bible?"已完成":"建议优先"} done={s.has_story_bible} />
                <Hint to="/daily-writer" label="生成下一章草稿" desc={`当前建议章节 #${s.next_chapter_number||1}`} badge={s.draft_count>0?`${s.draft_count} 个草稿`:"开始写作"} done={s.draft_count>0} />
                <Hint to="/story-bible" label="检查章节连续性" desc={`${s.open_plot_thread_count} 个未解决伏笔`} badge={s.open_plot_thread_count>0?"需要关注":"状态良好"} done={s.open_plot_thread_count===0} />
                <Hint to="/daily-writer" label="导出小说" desc={`${s.formal_chapter_count} 个正式章节可导出`} badge={s.formal_chapter_count>0?"可导出":"暂无章节"} done={s.formal_chapter_count>0} />
              </div>
            </div>

            <div className="card space-y-3">
              <h3 className="font-semibold" style={{color:"var(--text-primary)"}}>项目健康度</h3>
              <Gauge label="设定完整度" pct={s.has_story_bible?0.8:0.1} />
              <Gauge label="人物一致性" pct={Math.min(s.character_card_count/5,1)} />
              <Gauge label="情节连贯性" pct={Math.min(s.chapter_summary_count/3,1)} />
              <Gauge label="伏笔完成度" pct={s.open_plot_thread_count===0?1:Math.max(0.3,1-s.open_plot_thread_count*0.15)} />
            </div>
          </div>

          <div className="card">
            <h3 className="font-semibold mb-3" style={{color:"var(--text-primary)"}}>创作工作流</h3>
            <div className="grid gap-3" style={{gridTemplateColumns:"repeat(auto-fill,minmax(140px,1fr))"}}>
              <FlowEntry to="/reference-novels" step="1" label="参考小说" desc="提炼创作画像" />
              <FlowEntry to="/story-bible" step="2" label="故事圣经" desc="建立世界观" />
              <FlowEntry to="/story-bible" step="3" label="人物与计划" desc="人物卡+章节计划" />
              <FlowEntry to="/daily-writer" step="4" label="每日写作" desc="生成+编辑草稿" />
              <FlowEntry to="/daily-writer" step="5" label="质量检查" desc="Review+改写建议" />
              <FlowEntry to="/daily-writer" step="6" label="发布导出" desc="发布章节+导出" />
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function Stat({label,v,color,bg}:{label:string;v:any;color:string;bg:string}) {
  return <div className="stat-card" style={{background:bg||"var(--bg-card)"}}><div className="text-xs" style={{color:"var(--text-muted)"}}>{label}</div><div className="text-lg font-bold mt-1" style={{color}}>{v}</div></div>;
}
function Hint({to,label,desc,badge,done}:{to:string;label:string;desc:string;badge:string;done:boolean}) {
  return <Link to={to} className="flex items-center justify-between gap-3 p-3 rounded-lg border" style={{borderColor:"var(--border)",background:"var(--bg-card)"}}>
    <div><div className="text-sm font-medium" style={{color:"var(--text-primary)"}}>{label}</div><div className="text-xs mt-0.5" style={{color:"var(--text-muted)"}}>{desc}</div></div>
    <span className="badge text-xs" style={{background:done?"var(--emerald-bg)":"var(--amber-bg)",color:done?"var(--emerald-text)":"var(--amber-text)"}}>{badge}</span>
  </Link>;
}
function Gauge({label,pct}:{label:string;pct:number}) {
  return <div><div className="flex justify-between text-xs mb-1"><span style={{color:"var(--text-secondary)"}}>{label}</span><span style={{color:"var(--text-muted)"}}>{Math.round(pct*100)}%</span></div><div className="h-1.5 rounded-full" style={{background:"var(--bg-input)"}}><div className="h-full rounded-full transition-all" style={{width:`${pct*100}%`,background:pct>0.6?"var(--emerald)":pct>0.3?"var(--amber)":"var(--red)"}}/></div></div>;
}
function FlowEntry({to,step,label,desc}:{to:string;step:string;label:string;desc:string}) {
  return <Link to={to} className="flex items-center gap-3 p-3 rounded-lg border" style={{borderColor:"var(--border)",background:"var(--bg-card)"}}>
    <span className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold" style={{background:"var(--accent)",color:"var(--accent-text)"}}>{step}</span>
    <div><div className="text-sm font-medium" style={{color:"var(--text-primary)"}}>{label}</div><div className="text-xs" style={{color:"var(--text-muted)"}}>{desc}</div></div>
  </Link>;
}
