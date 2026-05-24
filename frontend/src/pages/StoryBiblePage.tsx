import { useEffect, useState, useCallback } from "react";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

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
  const [tab, setTab] = useState<"bible"|"cards"|"entries"|"plans"|"summaries"|"threads">("bible");

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
    try { const r = await fetch(`${BASE}${path}?project_id=${pid}`); if (r.ok) setter(await r.json()); } catch { /* */ }
  }, [pid]);

  useEffect(() => {
    if (!pid) return;
    fetcher("/api/story-bible", setBibles);
    fetcher("/api/character-cards", setCards);
    fetcher("/api/world-entries", setEntries);
    fetcher("/api/chapter-plans", setPlans);
    fetcher("/api/chapter-summaries", setSummaries);
    fetcher("/api/plot-threads", setThreads);
  }, [pid, fetcher]);

  const tabDefs = [
    { key: "bible" as const, label: `故事圣经 (${bibles.length})`, count: bibles.length },
    { key: "cards" as const, label: `人物卡 (${cards.length})`, count: cards.length },
    { key: "entries" as const, label: `世界观 (${entries.length})`, count: entries.length },
    { key: "plans" as const, label: `章节计划 (${plans.length})`, count: plans.length },
    { key: "summaries" as const, label: `章节摘要 (${summaries.length})`, count: summaries.length },
    { key: "threads" as const, label: `伏笔 (${threads.length})`, count: threads.length },
  ];

  function setProject(n: number) { setPid(n); if (n>0) localStorage.setItem("selectedProjectId", String(n)); else localStorage.removeItem("selectedProjectId"); }

  async function del(prefix: string, id: number, label: string) {
    if (!confirm(`delete ${label}?`)) return;
    setError(null); setSuccess(null);
    await fetch(`${BASE}${prefix}/${id}`, { method: "DELETE" });
    setSuccess(`${label} deleted`);
    // reload
    fetcher("/api/story-bible", setBibles);
    fetcher("/api/character-cards", setCards);
    fetcher("/api/world-entries", setEntries);
    fetcher("/api/chapter-plans", setPlans);
    if (prefix === "/api/story-bible" && selBible?.id === id) setSelBible(null);
    if (prefix === "/api/character-cards" && selCard?.id === id) setSelCard(null);
    if (prefix === "/api/world-entries" && selEntry?.id === id) setSelEntry(null);
    if (prefix === "/api/chapter-plans" && selPlan?.id === id) setSelPlan(null);
  }

  async function detail(prefix: string, id: number, setter: (d: any) => void) {
    setError(null); setSuccess(null);
    try { const r = await fetch(`${BASE}${prefix}/${id}`); if (r.ok) setter(await r.json()); } catch { /* */ }
  }

  async function saveForm(path: string, body: object) {
    setSaving(true); setError(null);
    try {
      const isNew = !body.hasOwnProperty("id");
      const r = await fetch(`${BASE}${path}`, { method: isNew ? "POST" : "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || `HTTP ${r.status}`);
      setShowForm(false); setEditing(false); setSuccess("saved");
      fetcher("/api/story-bible", setBibles);
      fetcher("/api/character-cards", setCards);
      fetcher("/api/world-entries", setEntries);
      fetcher("/api/chapter-plans", setPlans);
    } catch (e) { setError(e instanceof Error ? e.message : "save failed"); }
    finally { setSaving(false); }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4 flex-wrap">
        <h2 className="text-lg font-semibold">Story Bible 故事圣经</h2>
        <label className="flex items-center gap-2 text-xs text-slate-400">
          project <input type="number" min={1} value={pid||""} onChange={e => setProject(Number(e.target.value)||0)} className="w-20 rounded border border-slate-700 bg-slate-800 px-2 py-1 text-sm text-white" placeholder="ID" />
        </label>
        {pid > 0 && (
          <button onClick={() => { setShowForm(true); setEditing(false); }} className="rounded bg-cyan-600 px-3 py-1.5 text-xs text-white hover:bg-cyan-700">+ new</button>
        )}
      </div>

      {!pid ? <Placeholder text="input project id" /> : (
        <>
          <div className="flex gap-2 flex-wrap">
            {tabDefs.map(t => (
              <button key={t.key} onClick={() => { setTab(t.key); setError(null); setSuccess(null); }}
                className={`rounded px-3 py-1.5 text-xs font-medium transition ${tab===t.key?"bg-cyan-600 text-white":"border border-slate-700 text-slate-400 hover:text-white"}`}>
                {t.label}
              </button>
            ))}
          </div>

          {error && <div className="rounded border border-red-500/30 bg-red-500/5 px-4 py-3 text-sm text-red-400">{error}</div>}
          {success && <div className="rounded border border-emerald-500/30 bg-emerald-500/5 px-4 py-3 text-sm text-emerald-400">{success}</div>}

          {(showForm || editing) && <FormPopup tab={tab} pid={pid} onSave={saveForm} onCancel={() => { setShowForm(false); setEditing(false); }} saving={saving} editData={tab==="bible"?selBible:tab==="cards"?selCard:tab==="entries"?selEntry:selPlan} />}

          <div className="grid gap-4 lg:grid-cols-5">
            <div className="space-y-2 lg:col-span-2">
              {tab === "bible" && bibles.map(b => <Item key={b.id} title={b.title||"untitled"} sub={`${b.genre||""}`} active={selBible?.id===b.id} onClick={() => detail("/api/story-bible", b.id, setSelBible)}
                onEdit={() => { detail("/api/story-bible", b.id, setSelBible); setEditing(true); }} onDel={() => del("/api/story-bible", b.id, "story bible")} />)}
              {tab === "cards" && cards.map(c => <Item key={c.id} title={c.name||"unnamed"} sub={c.role} active={selCard?.id===c.id} onClick={() => detail("/api/character-cards", c.id, setSelCard)}
                onEdit={() => { detail("/api/character-cards", c.id, setSelCard); setEditing(true); }} onDel={() => del("/api/character-cards", c.id, "card")} />)}
              {tab === "entries" && entries.map(e => <Item key={e.id} title={e.name||"unnamed"} sub={`${e.entry_type} · ${e.importance}`} active={selEntry?.id===e.id} onClick={() => detail("/api/world-entries", e.id, setSelEntry)}
                onEdit={() => { detail("/api/world-entries", e.id, setSelEntry); setEditing(true); }} onDel={() => del("/api/world-entries", e.id, "entry")} />)}
              {tab === "plans" && plans.map(p => <Item key={p.id} title={`#${p.chapter_number} ${p.title||"untitled"}`} sub={p.status} active={selPlan?.id===p.id} onClick={() => detail("/api/chapter-plans", p.id, setSelPlan)}
                onEdit={() => { detail("/api/chapter-plans", p.id, setSelPlan); setEditing(true); }} onDel={() => del("/api/chapter-plans", p.id, "plan")} />)}
              {tab === "summaries" && summaries.map((s:any) => <Item key={s.id} title={`#${s.chapter_number} summary`} sub={s.key_events?.slice(0,60)||""} active={selSummary?.id===s.id} onClick={() => detail("/api/chapter-summaries", s.id, setSelSummary)}
                onEdit={() => { detail("/api/chapter-summaries", s.id, setSelSummary); setEditing(true); }} onDel={() => del("/api/chapter-summaries", s.id, "summary")} />)}
              {tab === "threads" && threads.map((t:any) => <Item key={t.id} title={t.title||"untitled"} sub={`${t.status} · ch${t.introduced_chapter||"?"}`} active={selThread?.id===t.id} onClick={() => detail("/api/plot-threads", t.id, setSelThread)}
                onEdit={() => { detail("/api/plot-threads", t.id, setSelThread); setEditing(true); }} onDel={() => del("/api/plot-threads", t.id, "thread")} />)}
              {((tab==="bible"&&bibles.length===0)||(tab==="cards"&&cards.length===0)||(tab==="entries"&&entries.length===0)||(tab==="plans"&&plans.length===0)||(tab==="summaries"&&summaries.length===0)||(tab==="threads"&&threads.length===0)) && <p className="text-xs text-slate-600 p-3">no entries</p>}
            </div>

            <div className="lg:col-span-3">
              {tab==="bible"&&selBible && <DetailBible data={selBible} />}
              {tab==="cards"&&selCard && <DetailCard data={selCard} />}
              {tab==="entries"&&selEntry && <DetailEntry data={selEntry} />}
              {tab==="plans"&&selPlan && <DetailPlan data={selPlan} />}
              {tab==="summaries"&&selSummary && <DetailSummary data={selSummary} />}
              {tab==="threads"&&selThread && <DetailThread data={selThread} />}
              {!selBible&&!selCard&&!selEntry&&!selPlan&&!selSummary&&!selThread && <Placeholder text="select an item" />}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function Item({ title, sub, active, onClick, onEdit, onDel }: { title: string; sub: string; active: boolean; onClick: () => void; onEdit: () => void; onDel: () => void }) {
  return (
    <div onClick={onClick} className={`cursor-pointer rounded border p-3 text-sm transition ${active?"border-cyan-500 bg-cyan-500/10":"border-slate-800 bg-slate-900 hover:border-slate-700"}`}>
      <div className="font-medium">{title}</div>
      <div className="text-xs text-slate-500 mt-1">{sub}</div>
      <div className="flex gap-2 mt-2">
        <button onClick={e=>{e.stopPropagation();onEdit();}} className="text-xs text-cyan-400 hover:underline">edit</button>
        <button onClick={e=>{e.stopPropagation();onDel();}} className="text-xs text-red-400 hover:underline">del</button>
      </div>
    </div>
  );
}

function DetailBible({ data }: { data: BibleRead }) {
  return <div className="rounded-lg border border-slate-800 bg-slate-900 p-5 space-y-3">
    <h3 className="font-semibold">{data.title||"untitled"} <span className="text-xs text-slate-500">{data.genre}</span></h3>
    <F label="premise" v={data.premise} /><F label="tone" v={data.tone} /><F label="theme" v={data.theme} /><F label="world rules" v={data.world_rules} /><F label="narrative style" v={data.narrative_style} />
  </div>;
}
function DetailCard({ data }: { data: CardRead }) {
  return <div className="rounded-lg border border-slate-800 bg-slate-900 p-5 space-y-3">
    <h3 className="font-semibold">{data.name||"unnamed"} <span className="text-xs text-slate-500">{data.role}</span></h3>
    <F label="personality" v={data.personality} /><F label="motivation" v={data.motivation} /><F label="conflict" v={data.conflict} /><F label="relationships" v={data.relationship_notes} /><F label="arc" v={data.arc} />
  </div>;
}
function DetailEntry({ data }: { data: EntryRead }) {
  return <div className="rounded-lg border border-slate-800 bg-slate-900 p-5 space-y-3">
    <h3 className="font-semibold">{data.name||"unnamed"} <span className="text-xs text-slate-500">{data.entry_type} · {data.importance}</span></h3>
    <F label="description" v={data.description} /><F label="rules" v={data.rules} />
  </div>;
}
function DetailPlan({ data }: { data: PlanRead }) {
  return <div className="rounded-lg border border-slate-800 bg-slate-900 p-5 space-y-3">
    <h3 className="font-semibold">#{data.chapter_number} {data.title||"untitled"} <span className="text-xs text-slate-500">{data.status}</span></h3>
    <F label="goal" v={data.goal} /><F label="key events" v={data.key_events} /><F label="POV character" v={data.pov_character} />
  </div>;
}
function F({ label, v }: { label: string; v: string }) { if (!v) return null; return <div><div className="text-xs text-slate-500">{label}</div><div className="text-sm text-slate-300">{v.slice(0,400)}</div></div>; }
function Placeholder({ text }: { text: string }) { return <div className="rounded border border-dashed border-slate-700 p-10 text-center text-sm text-slate-600">{text}</div>; }

function FormPopup({ tab, pid, onSave, onCancel, saving, editData }: { tab: string; pid: number; onSave: (path: string, body: object) => void; onCancel: () => void; saving: boolean; editData: any; }) {
  const isEdit = !!editData;
  const prefix = tab==="bible"?"/api/story-bible":tab==="cards"?"/api/character-cards":tab==="entries"?"/api/world-entries":tab==="plans"?"/api/chapter-plans":tab==="summaries"?"/api/chapter-summaries":"/api/plot-threads";

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const body: Record<string, any> = isEdit ? { id: editData.id } : { project_id: pid };
    for (const [k, v] of fd.entries()) { if (v) body[k] = v; }
    if (tab === "plans") body.chapter_number = Number(fd.get("chapter_number")) || 1;
    onSave(prefix, body);
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-lg border border-slate-800 bg-slate-900 p-4 space-y-3">
      <h3 className="text-sm font-semibold">{isEdit ? "edit" : "new"} {tab==="bible"?"story bible":tab==="cards"?"character card":tab==="entries"?"world entry":"chapter plan"}</h3>
      {tab === "bible" && <><Input name="title" label="title" /><Input name="genre" label="genre" /><TA name="premise" label="premise" /><Input name="tone" label="tone" /><TA name="theme" label="theme" /><TA name="world_rules" label="world rules" /><TA name="narrative_style" label="narrative style" /></>}
      {tab === "cards" && <><Input name="name" label="name" /><Input name="role" label="role" /><TA name="personality" label="personality" /><TA name="motivation" label="motivation" /><TA name="conflict" label="conflict" /><TA name="relationship_notes" label="relationships" /><TA name="arc" label="arc" /></>}
      {tab === "entries" && <><Input name="name" label="name" /><Input name="entry_type" label="type" placeholder="location/organization/rule/item/culture/other" /><TA name="description" label="description" /><TA name="rules" label="rules" /><Input name="importance" label="importance" placeholder="high/medium/low" /></>}
      {tab === "plans" && <><Input name="chapter_number" label="chapter number" type="number" /><Input name="title" label="title" /><TA name="goal" label="goal" /><TA name="key_events" label="key events" /><Input name="pov_character" label="POV character" /><Input name="status" label="status" placeholder="planned/in_progress/done" /></>}
      {tab === "summaries" && <><Input name="chapter_number" label="chapter number" type="number" /><TA name="summary" label="summary" /><TA name="key_events" label="key events" /><TA name="character_changes" label="character changes" /><TA name="unresolved_threads" label="unresolved threads" /></>}
      {tab === "threads" && <><Input name="title" label="title" /><TA name="description" label="description" /><Input name="status" label="status" placeholder="open/developing/resolved/dropped" /><Input name="introduced_chapter" label="introduced chapter" type="number" /><Input name="resolved_chapter" label="resolved chapter" type="number" /><TA name="notes" label="notes" /></>}
      <div className="flex gap-2">
        <button type="submit" disabled={saving} className="rounded bg-cyan-600 px-4 py-2 text-sm text-white hover:bg-cyan-700 disabled:opacity-50">{saving?"saving...":"save"}</button>
        <button type="button" onClick={onCancel} className="rounded border border-slate-700 px-4 py-2 text-sm text-slate-400 hover:text-white">cancel</button>
      </div>
    </form>
  );
}
function Input({ name, label, type, placeholder }: { name: string; label: string; type?: string; placeholder?: string }) {
  return <label className="block text-xs text-slate-500 space-y-1">{label} <input name={name} type={type||"text"} placeholder={placeholder} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label>;
}
function TA({ name, label }: { name: string; label: string }) {
  return <label className="block text-xs text-slate-500 space-y-1">{label} <textarea name={name} rows={3} className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label>;
}
function DetailSummary({ data }: { data: any }) {
  return <div className="rounded-lg border border-slate-800 bg-slate-900 p-5 space-y-3">
    <h3 className="font-semibold">#{data.chapter_number} 章节摘要</h3>
    <F label="summary" v={data.summary} /><F label="key events" v={data.key_events} /><F label="character changes" v={data.character_changes} /><F label="unresolved threads" v={data.unresolved_threads} />
  </div>;
}
function DetailThread({ data }: { data: any }) {
  return <div className="rounded-lg border border-slate-800 bg-slate-900 p-5 space-y-3">
    <h3 className="font-semibold">{data.title||"untitled"} <span className="text-xs text-slate-500">{data.status}</span></h3>
    <F label="description" v={data.description} />
    <div className="text-xs text-slate-500">introduced ch: {data.introduced_chapter||"-"} · resolved ch: {data.resolved_chapter||"-"}</div>
    <F label="notes" v={data.notes} />
  </div>;
}
