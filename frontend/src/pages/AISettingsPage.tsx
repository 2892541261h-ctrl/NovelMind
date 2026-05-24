import { useEffect, useState } from "react";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export function AISettingsPage() {
  const [tab, setTab] = useState<"providers"|"models"|"logs">("providers");
  const [providers, setProviders] = useState<any[]>([]);
  const [models, setModels] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [selProviderId, setSelProviderId] = useState<number>(0);

  async function load() {
    try {
      const [p, m, l, s] = await Promise.all([
        fetch(`${BASE}/api/ai/providers`).then(r=>r.json()),
        fetch(`${BASE}/api/ai/models`).then(r=>r.json()),
        fetch(`${BASE}/api/ai/usage-logs`).then(r=>r.json()),
        fetch(`${BASE}/api/ai/usage-logs/summary`).then(r=>r.json()),
      ]);
      setProviders(p); setModels(m); setLogs(l); setSummary(s);
    } catch { /* */ }
  }

  useEffect(() => { load(); }, []);

  async function handleSave(formEl: HTMLFormElement, path: string, isNew: boolean) {
    setSaving(true); setError(null);
    const fd = new FormData(formEl);
    const body: Record<string, any> = {};
    for (const [k, v] of fd.entries()) {
      if (k === "is_active" || k === "is_default") body[k] = v === "on";
      else if (v) body[k] = v;
    }
    try {
      const r = await fetch(`${BASE}${path}`, { method: isNew ? "POST" : "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || `HTTP ${r.status}`);
      setShowForm(false); setEditing(null); setSuccess("saved"); load();
    } catch (e) { setError(e instanceof Error ? e.message : "save failed"); }
    finally { setSaving(false); }
  }

  async function del(path: string) {
    if (!confirm("confirm delete?")) return;
    await fetch(`${BASE}${path}`, { method: "DELETE" }); load();
  }

  async function setDefaultModel(id: number) {
    await fetch(`${BASE}/api/ai/models/${id}/set-default`, { method: "POST" }); load();
  }

  const tabs = [
    { key: "providers" as const, label: `Provider (${providers.length})` },
    { key: "models" as const, label: `Model (${models.length})` },
    { key: "logs" as const, label: `Usage Logs (${logs.length})` },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">AI Settings</h2>
      {error && <div className="rounded border border-red-500/30 bg-red-500/5 px-4 py-3 text-sm text-red-400">{error}</div>}
      {success && <div className="rounded border border-emerald-500/30 bg-emerald-500/5 px-4 py-3 text-sm text-emerald-400">{success}</div>}
      <p className="text-xs text-amber-400">API Key only stores environment variable name. Real keys are read from environment at runtime. Do NOT paste real API keys here.</p>

      <div className="flex gap-2 flex-wrap">
        {tabs.map(t => <button key={t.key} onClick={()=>setTab(t.key)} className={`rounded px-3 py-1.5 text-xs font-medium ${tab===t.key?"bg-cyan-600 text-white":"border border-slate-700 text-slate-400 hover:text-white"}`}>{t.label}</button>)}
        <button onClick={()=>{setShowForm(true);setEditing(null);}} className="rounded bg-cyan-600 px-3 py-1.5 text-xs text-white hover:bg-cyan-700">+ New</button>
      </div>

      {(showForm||editing) && (
        <form onSubmit={e=>{e.preventDefault(); handleSave(e.currentTarget, editing?`${editing.prefix}/${editing.id}`:`${tab==="providers"?"/api/ai/providers":tab==="models"?"/api/ai/models":""}`, !editing);}} className="rounded-lg border border-slate-800 bg-slate-900 p-4 space-y-3">
          {tab==="providers"&&<><label className="block text-xs text-slate-500 space-y-1">name <input name="name" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label><label className="block text-xs text-slate-500 space-y-1">type <input name="provider_type" placeholder="mock / oai_compat" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label><label className="block text-xs text-slate-500 space-y-1">base_url <input name="base_url" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label><label className="block text-xs text-slate-500 space-y-1">env var name <input name="api_key_env_var" placeholder="e.g. OAI_API_KEY" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label><label className="block text-xs text-slate-500 space-y-1">default model <input name="default_model" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label><label className="flex items-center gap-2 text-xs text-slate-500"><input type="checkbox" name="is_active" /> is_active</label></>}
          {tab==="models"&&<><label className="block text-xs text-slate-500 space-y-1">provider_id <input name="provider_id" type="number" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label><label className="block text-xs text-slate-500 space-y-1">name <input name="name" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label><label className="block text-xs text-slate-500 space-y-1">model <input name="model" placeholder="e.g. gpt-4o" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label><label className="block text-xs text-slate-500 space-y-1">display name <input name="display_name" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label><label className="block text-xs text-slate-500 space-y-1">context window <input name="context_window" type="number" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label><div className="flex gap-3"><label className="flex-1 block text-xs text-slate-500 space-y-1">input price ($/1M) <input name="input_price_per_1m_tokens" step="0.01" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label><label className="flex-1 block text-xs text-slate-500 space-y-1">output price ($/1M) <input name="output_price_per_1m_tokens" step="0.01" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label></div><label className="block text-xs text-slate-500 space-y-1">currency <input name="currency" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label><div className="flex gap-3"><label className="flex items-center gap-2 text-xs text-slate-500"><input type="checkbox" name="is_default" /> is_default</label><label className="flex items-center gap-2 text-xs text-slate-500"><input type="checkbox" name="is_active" /> is_active</label></div></>}
          <div className="flex gap-2"><button type="submit" disabled={saving} className="rounded bg-cyan-600 px-4 py-2 text-sm text-white hover:bg-cyan-700 disabled:opacity-50">{saving?"saving...":"save"}</button><button type="button" onClick={()=>{setShowForm(false);setEditing(null);}} className="rounded border border-slate-700 px-4 py-2 text-sm text-slate-400 hover:text-white">cancel</button></div>
        </form>
      )}

      {tab==="providers"&&providers.map(p=><div key={p.id} className="rounded-lg border border-slate-800 bg-slate-900 p-3 flex items-center justify-between"><div><span className="font-medium">{p.name||"unnamed"}</span><span className="ml-2 text-xs text-slate-500">{p.provider_type} · {p.default_model||"no default"}</span>{p.is_active&&<span className="ml-2 text-xs text-emerald-400">active</span>}</div><div className="flex gap-2"><button onClick={()=>{setEditing({id:p.id,prefix:"/api/ai/providers"});setTab("providers");}} className="text-xs text-cyan-400 hover:underline">edit</button><button onClick={()=>del(`/api/ai/providers/${p.id}`)} className="text-xs text-red-400 hover:underline">del</button></div></div>)}

      {tab==="models"&&models.map(m=><div key={m.id} className="rounded-lg border border-slate-800 bg-slate-900 p-3 flex items-center justify-between"><div><span className="font-medium">{m.display_name||m.name||"unnamed"}</span><span className="ml-2 text-xs text-slate-500">model: {m.model}</span>{m.is_default&&<span className="ml-2 text-xs text-cyan-400">default</span>}{m.is_active&&<span className="ml-2 text-xs text-emerald-400">active</span>}</div><div className="flex gap-2">{!m.is_default&&<button onClick={()=>setDefaultModel(m.id)} className="text-xs text-cyan-400 hover:underline">set default</button>}<button onClick={()=>{setEditing({id:m.id,prefix:"/api/ai/models"});setTab("models");}} className="text-xs text-cyan-400 hover:underline">edit</button><button onClick={()=>del(`/api/ai/models/${m.id}`)} className="text-xs text-red-400 hover:underline">del</button></div></div>)}

      {tab==="logs"&&<>
        {summary&&<div className="rounded-lg border border-slate-800 bg-slate-900 p-4 text-xs grid grid-cols-3 gap-3">
          <div><span className="text-slate-500">total calls</span><div className="text-lg">{summary.total_calls}</div></div>
          <div><span className="text-slate-500">success/error</span><div className="text-lg">{summary.total_success}/{summary.total_error}</div></div>
          <div><span className="text-slate-500">est. cost</span><div className="text-lg">${summary.total_estimated_cost?.toFixed(6)||"0"}</div></div>
        </div>}
        {logs.map(l=><div key={l.id} className="rounded border border-slate-800 bg-slate-900 p-3 text-xs flex items-center justify-between">
          <div>
            <span className={`${l.status==="error"?"text-red-400":"text-slate-300"}`}>{l.feature_name}</span>
            <span className="ml-2 text-slate-500">{l.model} · {l.provider_type} · {l.total_tokens||"?"}t · {l.latency_ms}ms {l.estimated_cost!=null?`$${Number(l.estimated_cost).toFixed(6)}`:""}</span>
            {l.error_message&&<div className="text-red-400 mt-0.5">{l.error_message.slice(0,100)}</div>}
          </div>
          <span className="text-slate-600">{new Date(l.created_at).toLocaleString("zh-CN")}</span>
        </div>)}
        {logs.length===0&&<p className="text-xs text-slate-600 p-3">no logs</p>}
      </>}
    </div>
  );
}
