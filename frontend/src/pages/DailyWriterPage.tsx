import { useEffect, useState, useCallback } from "react";
const BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
interface DraftItem { id: number; project_id: number; chapter_number: number; title: string; status: string; source: string; created_at: string; updated_at: string; }
interface DraftRead extends DraftItem { content: string; writing_goal: string; prompt_snapshot: string; context_snapshot: string; }
interface FormalItem { id: number; project_id: number; chapter_number: number; title: string; status: string; word_count: number; published_at: string|null; created_at: string; updated_at: string; }
interface FormalRead extends FormalItem { content: string; source_draft_id: number|null; }
interface ProfileSummary { genre: string; worldbuilding_pattern: string; writing_style_profile: string; target_novel_direction: string; }

export function DailyWriterPage() {
  const [pid, setPid] = useState<number>(()=>Number(localStorage.getItem("selectedProjectId"))||0);
  const [hasProfile, setHasProfile] = useState<boolean|null>(null);
  const [profileSummary, setProfileSummary] = useState<ProfileSummary|null>(null);
  const [drafts, setDrafts] = useState<DraftItem[]>([]);
  const [selDraft, setSelDraft] = useState<DraftRead|null>(null);
  const [formalChs, setFormalChs] = useState<FormalItem[]>([]);
  const [selFormal, setSelFormal] = useState<FormalRead|null>(null);
  const [tab, setTab] = useState<"generate"|"drafts"|"published">("generate");
  const [success, setSuccess] = useState<string|null>(null);
  const [error, setError] = useState<string|null>(null);
  const [cNum, setCNum] = useState(1);
  const [title, setTitle] = useState(""); const [goal, setGoal] = useState(""); const [extra, setExtra] = useState("");
  const [genLoading, setGenLoading] = useState(false);
  const [editTitle, setEditTitle] = useState(""); const [editContent, setEditContent] = useState("");
  const [editSaving, setEditSaving] = useState(false); const [pubLoading, setPubLoading] = useState(false);
  const [deletingDraftId, setDeletingDraftId] = useState<number|null>(null);
  const [deletingFormalId, setDeletingFormalId] = useState<number|null>(null);
  const [v12Counts, setV12Counts] = useState<any>(null);
  const [reviewing, setReviewing] = useState(false); const [reviewResult, setReviewResult] = useState<any>(null);
  const [rewriting, setRewriting] = useState(false); const [rewriteResult, setRewriteResult] = useState<any>(null);

  const loadDrafts = useCallback(async()=>{if(!pid){setDrafts([]);return}try{const r=await fetch(`${BASE}/api/daily-writer/chapters?project_id=${pid}`);if(r.ok)setDrafts(await r.json())}catch{}}, [pid]);
  const loadFormal = useCallback(async()=>{if(!pid){setFormalChs([]);return}try{const r=await fetch(`${BASE}/api/formal-chapters?project_id=${pid}`);if(r.ok)setFormalChs(await r.json())}catch{}}, [pid]);

  useEffect(()=>{
    if(!pid){setDrafts([]);setSelDraft(null);setFormalChs([]);setSelFormal(null);setHasProfile(null);setProfileSummary(null);setV12Counts(null);return}
    setError(null);setSuccess(null);loadDrafts();loadFormal();
    fetch(`${BASE}/api/reference-novels?project_id=${pid}`).then(r=>r.json()).then((ns:any[])=>ns.length>0?fetch(`${BASE}/api/reference-novels/${ns[0].id}/profile`).then(r=>r.json()):Promise.reject()).then(p=>{setHasProfile(!!p&&!p.detail);setProfileSummary(p&&!p.detail?p:null)}).catch(()=>{setHasProfile(false);setProfileSummary(null)});
    Promise.all([fetch(`${BASE}/api/story-bible?project_id=${pid}`).then(r=>r.json()).catch(()=>[]),fetch(`${BASE}/api/character-cards?project_id=${pid}`).then(r=>r.json()).catch(()=>[]),fetch(`${BASE}/api/world-entries?project_id=${pid}`).then(r=>r.json()).catch(()=>[]),fetch(`${BASE}/api/chapter-plans?project_id=${pid}`).then(r=>r.json()).catch(()=>[])]).then(([b,c,e,p])=>{const nc=Math.max(...formalChs.map(x=>x.chapter_number),0)+1;setV12Counts({bibles:b.length,cards:c.length,entries:e.length,plans:p.length,nextChapter:nc,hasPlan:p.some((x:any)=>x.chapter_number===nc)})}).catch(()=>{});
    fetch(`${BASE}/api/daily-writer/chapters?project_id=${pid}`).then(r=>r.json()).then((ds:any[])=>{if(ds.length===0)setCNum(Math.max(...formalChs.map(c=>c.chapter_number),0)+1)}).catch(()=>{});
  },[pid,loadDrafts,loadFormal]);

  function setProject(n:number){setPid(n);n>0?localStorage.setItem("selectedProjectId",String(n)):localStorage.removeItem("selectedProjectId")}
  function switchTab(t:"generate"|"drafts"|"published"){setTab(t);setError(null);setSuccess(null)}

  async function handleGenerate(){if(!pid){setError("请先输入项目 ID");return}if(cNum<1){setError("请输入有效的章节编号");return}setGenLoading(true);setError(null);setSuccess(null);try{const r=await fetch(`${BASE}/api/daily-writer/generate`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({project_id:pid,chapter_number:cNum,title,writing_goal:goal,extra_instruction:extra})});const d=await r.json();if(!r.ok)throw new Error(d.detail||`HTTP ${r.status}`);setTab("drafts");setSelDraft(d.draft);setEditTitle(d.draft.title);setEditContent(d.draft.content);setSelFormal(null);setSuccess("章节草稿生成成功");loadDrafts()}catch(e){setError(e instanceof Error?e.message:"生成失败")}finally{setGenLoading(false)}}
  async function viewDraft(id:number){setSelFormal(null);setError(null);setSuccess(null);try{const r=await fetch(`${BASE}/api/daily-writer/chapters/${id}`);if(r.ok){const d=await r.json();setSelDraft(d);setEditTitle(d.title);setEditContent(d.content)}}catch{}}
  async function saveDraft(){if(!selDraft)return;setEditSaving(true);setError(null);setSuccess(null);try{const r=await fetch(`${BASE}/api/daily-writer/chapters/${selDraft.id}`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify({title:editTitle,content:editContent})});if(!r.ok)throw new Error((await r.json()).detail||`HTTP ${r.status}`);setSelDraft(await r.json());loadDrafts();setSuccess("草稿已保存")}catch(e){setError(e instanceof Error?e.message:"保存失败")}finally{setEditSaving(false)}}
  async function deleteDraft(id:number){if(!confirm("确认删除此草稿？"))return;setDeletingDraftId(id);setError(null);setSuccess(null);try{const r=await fetch(`${BASE}/api/daily-writer/chapters/${id}`,{method:"DELETE"});if(!r.ok){const d=await r.json().catch(()=>null)as any;throw new Error(d?.detail||`HTTP ${r.status}`)}if(selDraft?.id===id)setSelDraft(null);setSuccess("草稿已删除");loadDrafts()}catch(e){setError(e instanceof Error?e.message:"删除草稿失败")}finally{setDeletingDraftId(null)}}
  async function publishDraft(){if(!selDraft)return;setPubLoading(true);setError(null);setSuccess(null);try{const r=await fetch(`${BASE}/api/formal-chapters/publish-draft/${selDraft.id}`,{method:"POST"});const d=await r.json();if(!r.ok)throw new Error(d.detail||`HTTP ${r.status}`);setTab("published");setSelFormal(d.chapter);setSelDraft(null);loadFormal();setSuccess("发布成功！草稿已转为正式章节（草稿保留）")}catch(e){setError(e instanceof Error?e.message:"发布失败")}finally{setPubLoading(false)}}
  async function viewFormal(id:number){setSelDraft(null);setError(null);setSuccess(null);try{const r=await fetch(`${BASE}/api/formal-chapters/${id}`);if(r.ok)setSelFormal(await r.json())}catch{}}
  async function deleteFormal(id:number){if(!confirm("确认删除此正式章节？"))return;setDeletingFormalId(id);setError(null);setSuccess(null);try{const r=await fetch(`${BASE}/api/formal-chapters/${id}`,{method:"DELETE"});if(!r.ok){const d=await r.json().catch(()=>null)as any;throw new Error(d?.detail||`HTTP ${r.status}`)}if(selFormal?.id===id)setSelFormal(null);setSuccess("正式章节已删除");loadFormal()}catch(e){setError(e instanceof Error?e.message:"删除正式章节失败")}finally{setDeletingFormalId(null)}}
  async function reviewDraft(){if(!selDraft)return;setReviewing(true);setError(null);setReviewResult(null);try{const r=await fetch(`${BASE}/api/chapter-reviews/review-draft/${selDraft.id}`,{method:"POST"});const d=await r.json();if(!r.ok)throw new Error(d.detail||`HTTP ${r.status}`);setReviewResult(d);setSuccess("质量检查完成")}catch(e){setError(e instanceof Error?e.message:"检查失败")}finally{setReviewing(false)}}
  async function reviewFormal(){if(!selFormal)return;setReviewing(true);setError(null);setReviewResult(null);try{const r=await fetch(`${BASE}/api/chapter-reviews/review-formal/${selFormal.id}`,{method:"POST"});const d=await r.json();if(!r.ok)throw new Error(d.detail||`HTTP ${r.status}`);setReviewResult(d);setSuccess("质量检查完成")}catch(e){setError(e instanceof Error?e.message:"检查失败")}finally{setReviewing(false)}}
  async function suggestRewrite(){if(!selDraft)return;setRewriting(true);setError(null);setRewriteResult(null);try{const r=await fetch(`${BASE}/api/chapter-reviews/suggest-rewrite-draft/${selDraft.id}`,{method:"POST"});const d=await r.json();if(!r.ok)throw new Error(d.detail||`HTTP ${r.status}`);setRewriteResult(d);setSuccess("改写建议已生成（未自动修改正文）")}catch(e){setError(e instanceof Error?e.message:"建议生成失败")}finally{setRewriting(false)}}
  function exportMD(){if(pid)window.open(`${BASE}/api/exports/project/${pid}/markdown`)}
  function exportTXT(){if(pid)window.open(`${BASE}/api/exports/project/${pid}/txt`)}

  const c1="var(--text-primary)",c2="var(--text-secondary)",c3="var(--text-muted)";

  return (
    <div style={{maxWidth:1100}} className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div><h2 className="text-xl font-bold" style={{color:c1}}>每日写作</h2><p className="text-sm mt-0.5" style={{color:c3}}>创作你的原创小说章节</p></div>
        <label className="flex items-center gap-2 text-sm" style={{color:c2}}>项目 ID <input type="number" min={1} value={pid||""} onChange={e=>setProject(Number(e.target.value)||0)} className="!w-20" /></label>
      </div>
      {!pid ? <div className="empty-state">请先输入项目 ID</div> : <>
        <div className="flex flex-wrap items-center gap-2">
          <div className="badge text-xs" style={{background:hasProfile===true?"var(--emerald-bg)":"var(--amber-bg)",color:hasProfile===true?"var(--emerald-text)":"var(--amber-text)"}}>{hasProfile===null?"检查中...":hasProfile?"参考画像已接入":"未接入参考画像"}</div>
          {v12Counts && <span className="text-xs" style={{color:c3}}>故事圣经: {v12Counts.bibles>0?"已建立":"未建立"} · 人物卡: {v12Counts.cards} · 世界观: {v12Counts.entries} · 计划: {v12Counts.plans} · 下一章: #{v12Counts.nextChapter}</span>}
        </div>
        <div className="flex gap-2 flex-wrap">
          {(["generate","drafts","published"] as const).map(t=><button key={t} onClick={()=>switchTab(t)} className={`tab-btn ${tab===t?"active":""}`}>{t==="generate"?`生成草稿`:`${t==="drafts"?"草稿":"已发布"} (${t==="drafts"?drafts.length:formalChs.length})`}</button>)}
          <div className="flex-1"/><button onClick={exportMD} disabled={formalChs.length===0} className="btn btn-secondary text-xs">导出 Markdown</button><button onClick={exportTXT} disabled={formalChs.length===0} className="btn btn-secondary text-xs">导出 TXT</button>
        </div>
        {success && <div className="toast toast-success">{success}</div>}{error && <div className="toast toast-error">{error}</div>}
        <div className="grid gap-4" style={{gridTemplateColumns:"1fr 1fr"}}>
          <div className="space-y-4">
            {tab==="generate"&&<div className="card space-y-3"><h3 className="font-semibold" style={{color:c1}}>生成新章</h3>
              <label className="text-xs block space-y-1" style={{color:c2}}>章节编号 <input type="number" min={1} value={cNum} onChange={e=>setCNum(Number(e.target.value)||1)} className="!w-full" /></label>
              <label className="text-xs block space-y-1" style={{color:c2}}>章节标题 <input value={title} onChange={e=>setTitle(e.target.value)} placeholder="如：新的开始" /></label>
              <label className="text-xs block space-y-1" style={{color:c2}}>写作目标 <textarea value={goal} onChange={e=>setGoal(e.target.value)} rows={2} placeholder="本章要推进什么剧情？" /></label>
              <label className="text-xs block space-y-1" style={{color:c2}}>额外要求 <textarea value={extra} onChange={e=>setExtra(e.target.value)} rows={2} placeholder="对 AI 写作的特殊要求" /></label>
              <button onClick={handleGenerate} disabled={genLoading} className="btn btn-primary w-full justify-center">{genLoading?"正在生成...":"生成草稿"}</button>
            </div>}
            {tab==="drafts"&&<div className="card space-y-2"><h3 className="font-semibold" style={{color:c1}}>草稿列表</h3>{drafts.length===0?<div className="text-sm" style={{color:c3}}>暂无草稿，请先生成一章</div>:drafts.map(d=><div key={d.id} onClick={()=>viewDraft(d.id)} className="p-3 rounded-lg cursor-pointer border" style={{borderColor:selDraft?.id===d.id?"var(--accent)":"var(--border)",background:selDraft?.id===d.id?"var(--bg-card-hover)":"var(--bg-card)"}}><div className="text-sm font-medium" style={{color:c1}}>#{d.chapter_number} {d.title||"未命名"}</div><div className="text-xs mt-0.5" style={{color:c3}}>{d.status} · {new Date(d.created_at).toLocaleDateString("zh-CN")}</div></div>)}</div>}
            {tab==="published"&&<div className="card space-y-2"><h3 className="font-semibold" style={{color:c1}}>正式章节</h3>{formalChs.length===0?<div className="text-sm" style={{color:c3}}>暂无已发布章节</div>:formalChs.map(c=><div key={c.id} onClick={()=>viewFormal(c.id)} className="p-3 rounded-lg cursor-pointer border" style={{borderColor:selFormal?.id===c.id?"var(--emerald)":"var(--border)",background:selFormal?.id===c.id?"var(--bg-card-hover)":"var(--bg-card)"}}><div className="text-sm font-medium" style={{color:c1}}>#{c.chapter_number} {c.title||"未命名"}</div><div className="text-xs mt-0.5" style={{color:c3}}>{c.word_count} 字 · {c.published_at?new Date(c.published_at).toLocaleDateString("zh-CN"):"-"}</div></div>)}</div>}
          </div>
          <div className="space-y-4">
            {selDraft&&<div className="card space-y-3">
              <div className="flex items-center justify-between flex-wrap gap-2"><h3 className="font-semibold" style={{color:c1}}>草稿 #{selDraft.chapter_number} {selDraft.title||"未命名"}</h3>
                <div className="flex gap-1 flex-wrap"><button onClick={saveDraft} disabled={editSaving} className="btn btn-primary text-xs">{editSaving?"保存中...":"保存"}</button><button onClick={publishDraft} disabled={pubLoading} className="btn btn-secondary text-xs" style={{background:"var(--emerald-bg)",color:"var(--emerald-text)",borderColor:"var(--emerald)"}}>{pubLoading?"发布中...":"发布"}</button><button onClick={()=>deleteDraft(selDraft.id)} disabled={!!deletingDraftId} className="btn btn-danger text-xs">{deletingDraftId===selDraft.id?"删除中...":"删除"}</button><button onClick={reviewDraft} disabled={reviewing} className="btn btn-secondary text-xs" style={{color:"var(--purple-text)",background:"var(--purple-bg)"}}>{reviewing?"检查中...":"质量检查"}</button><button onClick={suggestRewrite} disabled={rewriting} className="btn btn-secondary text-xs" style={{color:"var(--amber-text)",background:"var(--amber-bg)"}}>{rewriting?"建议中...":"改写建议"}</button></div>
              </div>
              <label className="text-xs block space-y-1" style={{color:c2}}>标题 <input value={editTitle} onChange={e=>setEditTitle(e.target.value)} /></label>
              <label className="text-xs block space-y-1" style={{color:c2}}>正文 <textarea value={editContent} onChange={e=>setEditContent(e.target.value)} rows={14} className="leading-relaxed" /></label>
              <p className="text-xs" style={{color:c3}}>发布为正式章节不会删除草稿，也不会覆盖已有正式章节。</p>
              {reviewResult&&<div className="rounded-lg p-3 text-xs space-y-1" style={{background:"var(--bg-input)"}}><span className="font-medium" style={{color:"var(--purple-text)"}}>质量评分</span><div className="grid grid-cols-4 gap-1" style={{color:c2}}>{["综合","连贯","人物","节奏","风格","原创","目标"].map((l,i)=><span key={i}>{l} {[reviewResult.overall_score,reviewResult.continuity_score,reviewResult.character_consistency_score,reviewResult.pacing_score,reviewResult.style_score,reviewResult.originality_score,reviewResult.goal_alignment_score][i]}</span>)}</div>{reviewResult.issues&&<div style={{color:"var(--red-text)"}}>{reviewResult.issues.slice(0,300)}</div>}{reviewResult.suggestions&&<div style={{color:"var(--amber-text)"}}>{reviewResult.suggestions.slice(0,300)}</div>}</div>}
              {rewriteResult&&<div className="rounded-lg p-3 text-xs" style={{background:"var(--bg-input)"}}><span className="font-medium" style={{color:"var(--amber-text)"}}>改写建议（未修改正文）</span><div style={{color:c2}}>{rewriteResult.suggested_revision_notes?.slice(0,300)}</div></div>}
            </div>}
            {selFormal&&!selDraft&&<div className="card space-y-3">
              <div className="flex items-center justify-between"><h3 className="font-semibold" style={{color:c1}}>#{selFormal.chapter_number} {selFormal.title||"章节"} <span className="badge" style={{background:"var(--emerald-bg)",color:"var(--emerald-text)"}}>已发布</span></h3><div className="flex gap-1"><button onClick={reviewFormal} disabled={reviewing} className="btn btn-secondary text-xs" style={{color:"var(--purple-text)",background:"var(--purple-bg)"}}>{reviewing?"检查中...":"质量检查"}</button><button onClick={()=>deleteFormal(selFormal.id)} disabled={!!deletingFormalId} className="btn btn-danger text-xs">{deletingFormalId===selFormal.id?"删除中...":"删除"}</button></div></div>
              <div className="rounded-lg p-4 text-sm leading-relaxed whitespace-pre-wrap" style={{background:"var(--bg-input)",color:c1,maxHeight:"60vh",overflowY:"auto"}}>{selFormal.content}</div>
              <div className="text-xs" style={{color:c3}}>{selFormal.word_count} 字 · 发布于 {selFormal.published_at?new Date(selFormal.published_at).toLocaleDateString("zh-CN"):"-"}</div>
              {reviewResult&&<div className="rounded-lg p-3 text-xs space-y-1" style={{background:"var(--bg-input)"}}><span className="font-medium" style={{color:"var(--purple-text)"}}>质量评分</span><div className="grid grid-cols-4 gap-1" style={{color:c2}}>{["综合","连贯","人物","节奏","风格","原创","目标"].map((l,i)=><span key={i}>{l} {[reviewResult.overall_score,reviewResult.continuity_score,reviewResult.character_consistency_score,reviewResult.pacing_score,reviewResult.style_score,reviewResult.originality_score,reviewResult.goal_alignment_score][i]}</span>)}</div></div>}
            </div>}
            {!selDraft&&!selFormal&&<div className="empty-state">选择草稿或正式章节查看</div>}
          </div>
        </div>
      </>}
    </div>
  );
}
