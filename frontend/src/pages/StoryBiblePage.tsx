import { useCallback, useEffect, useState } from "react";
import type { FormEvent, ReactNode } from "react";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

type TabKey = "bible" | "cards" | "entries" | "plans" | "summaries" | "threads";

interface BibleItem { id: number; project_id: number; title: string; genre: string; created_at: string; updated_at: string; }
interface BibleRead extends BibleItem { premise: string; tone: string; theme: string; world_rules: string; narrative_style: string; }
interface CardItem { id: number; project_id: number; name: string; role: string; created_at: string; updated_at: string; }
interface CardRead extends CardItem { personality: string; motivation: string; conflict: string; relationship_notes: string; arc: string; }
interface EntryItem { id: number; project_id: number; name: string; entry_type: string; importance: string; created_at: string; updated_at: string; }
interface EntryRead extends EntryItem { description: string; rules: string; }
interface PlanItem { id: number; project_id: number; chapter_number: number; title: string; goal: string; status: string; created_at: string; updated_at: string; }
interface PlanRead extends PlanItem { key_events: string; pov_character: string; }

export function StoryBiblePage() {
  const [pid, setPid] = useState<number>(() => Number(localStorage.getItem("selectedProjectId")) || 0);
  const [tab, setTab] = useState<TabKey>("bible");

  const [bibles, setBibles] = useState<BibleItem[]>([]);
  const [cards, setCards] = useState<CardItem[]>([]);
  const [entries, setEntries] = useState<EntryItem[]>([]);
  const [plans, setPlans] = useState<PlanItem[]>([]);
  const [summaries, setSummaries] = useState<any[]>([]);
  const [threads, setThreads] = useState<any[]>([]);

  const [selBible, setSelBible] = useState<BibleRead | null>(null);
  const [selCard, setSelCard] = useState<CardRead | null>(null);
  const [selEntry, setSelEntry] = useState<EntryRead | null>(null);
  const [selPlan, setSelPlan] = useState<PlanRead | null>(null);
  const [selSummary, setSelSummary] = useState<any | null>(null);
  const [selThread, setSelThread] = useState<any | null>(null);

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);

  const fetcher = useCallback(async <T,>(path: string, setter: (d: T) => void) => {
    if (!pid) return;
    try {
      const r = await fetch(`${BASE}${path}?project_id=${pid}`);
      if (r.ok) setter(await r.json());
    } catch {
      setError("加载项目资料失败，请确认后端已启动。");
    }
  }, [pid]);

  const reloadAll = useCallback(() => {
    if (!pid) return;
    fetcher("/api/story-bible", setBibles);
    fetcher("/api/character-cards", setCards);
    fetcher("/api/world-entries", setEntries);
    fetcher("/api/chapter-plans", setPlans);
    fetcher("/api/chapter-summaries", setSummaries);
    fetcher("/api/plot-threads", setThreads);
  }, [fetcher, pid]);

  useEffect(() => {
    reloadAll();
  }, [reloadAll]);

  const tabDefs = [
    { key: "bible" as const, label: `故事圣经 (${bibles.length})` },
    { key: "cards" as const, label: `人物卡 (${cards.length})` },
    { key: "entries" as const, label: `世界观 (${entries.length})` },
    { key: "plans" as const, label: `章节计划 (${plans.length})` },
    { key: "summaries" as const, label: `章节摘要 (${summaries.length})` },
    { key: "threads" as const, label: `伏笔/线索 (${threads.length})` },
  ];

  function setProject(n: number) {
    setPid(n);
    if (n > 0) localStorage.setItem("selectedProjectId", String(n));
    else localStorage.removeItem("selectedProjectId");
  }

  function selectedForTab() {
    if (tab === "bible") return selBible;
    if (tab === "cards") return selCard;
    if (tab === "entries") return selEntry;
    if (tab === "plans") return selPlan;
    if (tab === "summaries") return selSummary;
    return selThread;
  }

  function clearSelected(prefix: string, id: number) {
    if (prefix === "/api/story-bible" && selBible?.id === id) setSelBible(null);
    if (prefix === "/api/character-cards" && selCard?.id === id) setSelCard(null);
    if (prefix === "/api/world-entries" && selEntry?.id === id) setSelEntry(null);
    if (prefix === "/api/chapter-plans" && selPlan?.id === id) setSelPlan(null);
    if (prefix === "/api/chapter-summaries" && selSummary?.id === id) setSelSummary(null);
    if (prefix === "/api/plot-threads" && selThread?.id === id) setSelThread(null);
  }

  async function del(prefix: string, id: number, label: string) {
    if (!confirm(`确认删除${label}？`)) return;
    setError(null);
    setSuccess(null);
    try {
      const r = await fetch(`${BASE}${prefix}/${id}`, { method: "DELETE" });
      if (!r.ok) throw new Error(`删除失败：HTTP ${r.status}`);
      clearSelected(prefix, id);
      setSuccess(`${label}已删除`);
      reloadAll();
    } catch (e) {
      setError(e instanceof Error ? e.message : "删除失败");
    }
  }

  async function detail(prefix: string, id: number, setter: (d: any) => void) {
    setError(null);
    setSuccess(null);
    try {
      const r = await fetch(`${BASE}${prefix}/${id}`);
      if (!r.ok) throw new Error(`加载详情失败：HTTP ${r.status}`);
      setter(await r.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载详情失败");
    }
  }

  async function saveForm(path: string, body: Record<string, any>) {
    setSaving(true);
    setError(null);
    try {
      const isNew = !Object.prototype.hasOwnProperty.call(body, "id");
      const id = body.id;
      if (!isNew) delete body.id;
      const r = await fetch(`${BASE}${isNew ? path : `${path}/${id}`}`, {
        method: isNew ? "POST" : "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(data.detail || `HTTP ${r.status}`);
      setShowForm(false);
      setEditing(false);
      setSuccess("已保存");
      reloadAll();
    } catch (e) {
      setError(e instanceof Error ? e.message : "保存失败");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-4">
        <h2 className="text-lg font-semibold">Story Bible 故事圣经</h2>
        <label className="flex items-center gap-2 text-xs text-slate-400">
          项目 ID <input type="number" min={1} value={pid || ""} onChange={(e) => setProject(Number(e.target.value) || 0)} className="w-24 rounded border border-slate-700 bg-slate-800 px-2 py-1 text-sm text-white" placeholder="ID" />
        </label>
        {pid > 0 && (
          <button onClick={() => { setShowForm(true); setEditing(false); }} className="rounded bg-cyan-600 px-3 py-1.5 text-xs text-white hover:bg-cyan-700">+ 新建</button>
        )}
      </div>

      {!pid ? <Placeholder text="请输入项目 ID" /> : (
        <>
          <div className="flex flex-wrap gap-2">
            {tabDefs.map((t) => (
              <button
                key={t.key}
                onClick={() => {
                  setTab(t.key);
                  setError(null);
                  setSuccess(null);
                  setShowForm(false);
                  setEditing(false);
                }}
                className={`rounded px-3 py-1.5 text-xs font-medium transition ${tab === t.key ? "bg-cyan-600 text-white" : "border border-slate-700 text-slate-400 hover:text-white"}`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {error && <div className="rounded border border-red-500/30 bg-red-500/5 px-4 py-3 text-sm text-red-400">{error}</div>}
          {success && <div className="rounded border border-emerald-500/30 bg-emerald-500/5 px-4 py-3 text-sm text-emerald-400">{success}</div>}

          {(showForm || editing) && (
            <FormPopup
              tab={tab}
              pid={pid}
              onSave={saveForm}
              onCancel={() => { setShowForm(false); setEditing(false); }}
              saving={saving}
              editData={editing ? selectedForTab() : null}
            />
          )}

          <div className="grid gap-4 lg:grid-cols-5">
            <div className="space-y-2 lg:col-span-2">
              {tab === "bible" && bibles.map((b) => <Item key={b.id} title={b.title || "未命名故事圣经"} sub={b.genre || "未设置类型"} active={selBible?.id === b.id} onClick={() => detail("/api/story-bible", b.id, setSelBible)} onEdit={() => { detail("/api/story-bible", b.id, setSelBible); setEditing(true); }} onDel={() => del("/api/story-bible", b.id, "故事圣经")} />)}
              {tab === "cards" && cards.map((c) => <Item key={c.id} title={c.name || "未命名人物"} sub={c.role || "未设置角色定位"} active={selCard?.id === c.id} onClick={() => detail("/api/character-cards", c.id, setSelCard)} onEdit={() => { detail("/api/character-cards", c.id, setSelCard); setEditing(true); }} onDel={() => del("/api/character-cards", c.id, "人物卡")} />)}
              {tab === "entries" && entries.map((e) => <Item key={e.id} title={e.name || "未命名世界观条目"} sub={`${e.entry_type} / ${e.importance}`} active={selEntry?.id === e.id} onClick={() => detail("/api/world-entries", e.id, setSelEntry)} onEdit={() => { detail("/api/world-entries", e.id, setSelEntry); setEditing(true); }} onDel={() => del("/api/world-entries", e.id, "世界观条目")} />)}
              {tab === "plans" && plans.map((p) => <Item key={p.id} title={`第 ${p.chapter_number} 章 ${p.title || "未命名章节计划"}`} sub={p.status || "未设置状态"} active={selPlan?.id === p.id} onClick={() => detail("/api/chapter-plans", p.id, setSelPlan)} onEdit={() => { detail("/api/chapter-plans", p.id, setSelPlan); setEditing(true); }} onDel={() => del("/api/chapter-plans", p.id, "章节计划")} />)}
              {tab === "summaries" && summaries.map((s: any) => <Item key={s.id} title={`第 ${s.chapter_number} 章摘要`} sub={s.key_events?.slice(0, 60) || "未填写关键事件"} active={selSummary?.id === s.id} onClick={() => detail("/api/chapter-summaries", s.id, setSelSummary)} onEdit={() => { detail("/api/chapter-summaries", s.id, setSelSummary); setEditing(true); }} onDel={() => del("/api/chapter-summaries", s.id, "章节摘要")} />)}
              {tab === "threads" && threads.map((t: any) => <Item key={t.id} title={t.title || "未命名伏笔"} sub={`${t.status || "open"} / 引入第 ${t.introduced_chapter || "?"} 章`} active={selThread?.id === t.id} onClick={() => detail("/api/plot-threads", t.id, setSelThread)} onEdit={() => { detail("/api/plot-threads", t.id, setSelThread); setEditing(true); }} onDel={() => del("/api/plot-threads", t.id, "伏笔/线索")} />)}
              {((tab === "bible" && bibles.length === 0) || (tab === "cards" && cards.length === 0) || (tab === "entries" && entries.length === 0) || (tab === "plans" && plans.length === 0) || (tab === "summaries" && summaries.length === 0) || (tab === "threads" && threads.length === 0)) && <p className="p-3 text-xs text-slate-600">暂无条目</p>}
            </div>

            <div className="lg:col-span-3">
              {tab === "bible" && selBible && <DetailBible data={selBible} />}
              {tab === "cards" && selCard && <DetailCard data={selCard} />}
              {tab === "entries" && selEntry && <DetailEntry data={selEntry} />}
              {tab === "plans" && selPlan && <DetailPlan data={selPlan} />}
              {tab === "summaries" && selSummary && <DetailSummary data={selSummary} />}
              {tab === "threads" && selThread && <DetailThread data={selThread} />}
              {!selectedForTab() && <Placeholder text="从左侧选择条目查看详情" />}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function Item({ title, sub, active, onClick, onEdit, onDel }: { title: string; sub: string; active: boolean; onClick: () => void; onEdit: () => void; onDel: () => void }) {
  return (
    <div onClick={onClick} className={`cursor-pointer rounded border p-3 text-sm transition ${active ? "border-cyan-500 bg-cyan-500/10" : "border-slate-800 bg-slate-900 hover:border-slate-700"}`}>
      <div className="font-medium">{title}</div>
      <div className="mt-1 text-xs text-slate-500">{sub}</div>
      <div className="mt-2 flex gap-2">
        <button onClick={(e) => { e.stopPropagation(); onEdit(); }} className="text-xs text-cyan-400 hover:underline">编辑</button>
        <button onClick={(e) => { e.stopPropagation(); onDel(); }} className="text-xs text-red-400 hover:underline">删除</button>
      </div>
    </div>
  );
}

function DetailBible({ data }: { data: BibleRead }) {
  return <DetailCardShell title={data.title || "未命名故事圣经"} sub={data.genre}>
    <F label="故事前提" v={data.premise} /><F label="基调" v={data.tone} /><F label="主题" v={data.theme} /><F label="世界规则" v={data.world_rules} /><F label="叙事风格" v={data.narrative_style} />
  </DetailCardShell>;
}
function DetailCard({ data }: { data: CardRead }) {
  return <DetailCardShell title={data.name || "未命名人物"} sub={data.role}>
    <F label="性格" v={data.personality} /><F label="动机" v={data.motivation} /><F label="冲突" v={data.conflict} /><F label="关系备注" v={data.relationship_notes} /><F label="角色弧光" v={data.arc} />
  </DetailCardShell>;
}
function DetailEntry({ data }: { data: EntryRead }) {
  return <DetailCardShell title={data.name || "未命名世界观条目"} sub={`${data.entry_type} / ${data.importance}`}>
    <F label="描述" v={data.description} /><F label="规则" v={data.rules} />
  </DetailCardShell>;
}
function DetailPlan({ data }: { data: PlanRead }) {
  return <DetailCardShell title={`第 ${data.chapter_number} 章 ${data.title || "未命名章节计划"}`} sub={data.status}>
    <F label="章节目标" v={data.goal} /><F label="关键事件" v={data.key_events} /><F label="视角人物" v={data.pov_character} />
  </DetailCardShell>;
}
function DetailSummary({ data }: { data: any }) {
  return <DetailCardShell title={`第 ${data.chapter_number} 章摘要`}>
    <F label="摘要" v={data.summary} /><F label="关键事件" v={data.key_events} /><F label="人物变化" v={data.character_changes} /><F label="未解决线索" v={data.unresolved_threads} />
  </DetailCardShell>;
}
function DetailThread({ data }: { data: any }) {
  return <DetailCardShell title={data.title || "未命名伏笔"} sub={data.status}>
    <F label="描述" v={data.description} />
    <div className="text-xs text-slate-500">引入章节：{data.introduced_chapter || "-"} / 解决章节：{data.resolved_chapter || "-"}</div>
    <F label="备注" v={data.notes} />
  </DetailCardShell>;
}

function DetailCardShell({ title, sub, children }: { title: string; sub?: string; children: ReactNode }) {
  return <div className="space-y-3 rounded-lg border border-slate-800 bg-slate-900 p-5">
    <h3 className="font-semibold">{title} {sub && <span className="text-xs text-slate-500">{sub}</span>}</h3>
    {children}
  </div>;
}

function F({ label, v }: { label: string; v: string }) {
  if (!v) return null;
  return <div><div className="text-xs text-slate-500">{label}</div><div className="text-sm text-slate-300">{v.slice(0, 400)}</div></div>;
}
function Placeholder({ text }: { text: string }) {
  return <div className="rounded border border-dashed border-slate-700 p-10 text-center text-sm text-slate-600">{text}</div>;
}

function FormPopup({ tab, pid, onSave, onCancel, saving, editData }: { tab: TabKey; pid: number; onSave: (path: string, body: Record<string, any>) => void; onCancel: () => void; saving: boolean; editData: any; }) {
  const isEdit = !!editData;
  const prefix = tab === "bible" ? "/api/story-bible" : tab === "cards" ? "/api/character-cards" : tab === "entries" ? "/api/world-entries" : tab === "plans" ? "/api/chapter-plans" : tab === "summaries" ? "/api/chapter-summaries" : "/api/plot-threads";
  const title = tab === "bible" ? "故事圣经" : tab === "cards" ? "人物卡" : tab === "entries" ? "世界观条目" : tab === "plans" ? "章节计划" : tab === "summaries" ? "章节摘要" : "伏笔/线索";

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const body: Record<string, any> = isEdit ? { id: editData.id } : { project_id: pid };
    for (const [k, v] of fd.entries()) {
      if (v) body[k] = v;
    }
    if (tab === "plans" || tab === "summaries") body.chapter_number = Number(fd.get("chapter_number")) || 1;
    if (tab === "threads") {
      body.introduced_chapter = Number(fd.get("introduced_chapter")) || 0;
      body.resolved_chapter = Number(fd.get("resolved_chapter")) || 0;
    }
    onSave(prefix, body);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3 rounded-lg border border-slate-800 bg-slate-900 p-4">
      <h3 className="text-sm font-semibold">{isEdit ? "编辑" : "新建"}{title}</h3>
      {tab === "bible" && <><Input name="title" label="标题" defaultValue={editData?.title} /><Input name="genre" label="类型" defaultValue={editData?.genre} /><TA name="premise" label="故事前提" defaultValue={editData?.premise} /><Input name="tone" label="基调" defaultValue={editData?.tone} /><TA name="theme" label="主题" defaultValue={editData?.theme} /><TA name="world_rules" label="世界规则" defaultValue={editData?.world_rules} /><TA name="narrative_style" label="叙事风格" defaultValue={editData?.narrative_style} /></>}
      {tab === "cards" && <><Input name="name" label="姓名" defaultValue={editData?.name} /><Input name="role" label="角色定位" defaultValue={editData?.role} /><TA name="personality" label="性格" defaultValue={editData?.personality} /><TA name="motivation" label="动机" defaultValue={editData?.motivation} /><TA name="conflict" label="冲突" defaultValue={editData?.conflict} /><TA name="relationship_notes" label="关系备注" defaultValue={editData?.relationship_notes} /><TA name="arc" label="角色弧光" defaultValue={editData?.arc} /></>}
      {tab === "entries" && <><Input name="name" label="名称" defaultValue={editData?.name} /><Input name="entry_type" label="类型" placeholder="location / organization / rule / item / culture / other" defaultValue={editData?.entry_type} /><TA name="description" label="描述" defaultValue={editData?.description} /><TA name="rules" label="规则" defaultValue={editData?.rules} /><Input name="importance" label="重要度" placeholder="high / medium / low" defaultValue={editData?.importance} /></>}
      {tab === "plans" && <><Input name="chapter_number" label="章节编号" type="number" defaultValue={editData?.chapter_number} /><Input name="title" label="标题" defaultValue={editData?.title} /><TA name="goal" label="章节目标" defaultValue={editData?.goal} /><TA name="key_events" label="关键事件" defaultValue={editData?.key_events} /><Input name="pov_character" label="视角人物" defaultValue={editData?.pov_character} /><Input name="status" label="状态" placeholder="planned / in_progress / done" defaultValue={editData?.status} /></>}
      {tab === "summaries" && <><Input name="chapter_number" label="章节编号" type="number" defaultValue={editData?.chapter_number} /><TA name="summary" label="摘要" defaultValue={editData?.summary} /><TA name="key_events" label="关键事件" defaultValue={editData?.key_events} /><TA name="character_changes" label="人物变化" defaultValue={editData?.character_changes} /><TA name="unresolved_threads" label="未解决线索" defaultValue={editData?.unresolved_threads} /></>}
      {tab === "threads" && <><Input name="title" label="标题" defaultValue={editData?.title} /><TA name="description" label="描述" defaultValue={editData?.description} /><Input name="status" label="状态" placeholder="open / developing / resolved / dropped" defaultValue={editData?.status} /><Input name="introduced_chapter" label="引入章节" type="number" defaultValue={editData?.introduced_chapter} /><Input name="resolved_chapter" label="解决章节" type="number" defaultValue={editData?.resolved_chapter} /><TA name="notes" label="备注" defaultValue={editData?.notes} /></>}
      <div className="flex gap-2">
        <button type="submit" disabled={saving} className="rounded bg-cyan-600 px-4 py-2 text-sm text-white hover:bg-cyan-700 disabled:opacity-50">{saving ? "保存中..." : "保存"}</button>
        <button type="button" onClick={onCancel} className="rounded border border-slate-700 px-4 py-2 text-sm text-slate-400 hover:text-white">取消</button>
      </div>
    </form>
  );
}
function Input({ name, label, type, placeholder, defaultValue }: { name: string; label: string; type?: string; placeholder?: string; defaultValue?: string | number }) {
  return <label className="block space-y-1 text-xs text-slate-500">{label} <input name={name} type={type || "text"} placeholder={placeholder} defaultValue={defaultValue ?? ""} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label>;
}
function TA({ name, label, defaultValue }: { name: string; label: string; defaultValue?: string }) {
  return <label className="block space-y-1 text-xs text-slate-500">{label} <textarea name={name} rows={3} defaultValue={defaultValue ?? ""} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label>;
}
