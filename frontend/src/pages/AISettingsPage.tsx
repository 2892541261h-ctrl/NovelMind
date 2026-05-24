import { useEffect, useState } from "react";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export function AISettingsPage() {
  const [tab, setTab] = useState<"providers" | "models" | "logs">("providers");
  const [providers, setProviders] = useState<any[]>([]);
  const [models, setModels] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function load() {
    try {
      const [p, m, l, s] = await Promise.all([
        fetch(`${BASE}/api/ai/providers`).then((r) => r.json()),
        fetch(`${BASE}/api/ai/models`).then((r) => r.json()),
        fetch(`${BASE}/api/ai/usage-logs`).then((r) => r.json()),
        fetch(`${BASE}/api/ai/usage-logs/summary`).then((r) => r.json()),
      ]);
      setProviders(p);
      setModels(m);
      setLogs(l);
      setSummary(s);
    } catch {
      setError("AI 设置数据加载失败，请确认后端已启动。");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleSave(formEl: HTMLFormElement, path: string, isNew: boolean) {
    setSaving(true);
    setError(null);
    const fd = new FormData(formEl);
    const body: Record<string, any> = {};
    for (const [k, v] of fd.entries()) {
      if (k === "is_active" || k === "is_default") body[k] = v === "on";
      else if (v) body[k] = v;
    }
    try {
      const r = await fetch(`${BASE}${path}`, {
        method: isNew ? "POST" : "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || `HTTP ${r.status}`);
      setShowForm(false);
      setEditing(null);
      setSuccess("已保存");
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "保存失败");
    } finally {
      setSaving(false);
    }
  }

  async function del(path: string) {
    if (!confirm("确认删除此配置？")) return;
    await fetch(`${BASE}${path}`, { method: "DELETE" });
    setSuccess("已删除");
    load();
  }

  async function setDefaultModel(id: number) {
    await fetch(`${BASE}/api/ai/models/${id}/set-default`, { method: "POST" });
    setSuccess("已设为默认模型");
    load();
  }

  const tabs = [
    { key: "providers" as const, label: `Provider 配置 (${providers.length})` },
    { key: "models" as const, label: `模型 (${models.length})` },
    { key: "logs" as const, label: `用量日志 (${logs.length})` },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">AI 设置</h2>
      {error && <div className="rounded border border-red-500/30 bg-red-500/5 px-4 py-3 text-sm text-red-400">{error}</div>}
      {success && <div className="rounded border border-emerald-500/30 bg-emerald-500/5 px-4 py-3 text-sm text-emerald-400">{success}</div>}
      <p className="text-xs text-amber-400">
        这里只保存 API Key 的环境变量名，真实密钥由后端运行环境读取。请不要在页面中粘贴真实 API Key。
      </p>

      <div className="flex flex-wrap gap-2">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => {
              setTab(t.key);
              setError(null);
              setSuccess(null);
            }}
            className={`rounded px-3 py-1.5 text-xs font-medium ${tab === t.key ? "bg-cyan-600 text-white" : "border border-slate-700 text-slate-400 hover:text-white"}`}
          >
            {t.label}
          </button>
        ))}
        <button onClick={() => { setShowForm(true); setEditing(null); }} className="rounded bg-cyan-600 px-3 py-1.5 text-xs text-white hover:bg-cyan-700">+ 新建</button>
      </div>

      {(showForm || editing) && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSave(
              e.currentTarget,
              editing ? `${editing.prefix}/${editing.id}` : `${tab === "providers" ? "/api/ai/providers" : tab === "models" ? "/api/ai/models" : ""}`,
              !editing,
            );
          }}
          className="space-y-3 rounded-lg border border-slate-800 bg-slate-900 p-4"
        >
          {tab === "providers" && (
            <>
              <label className="block space-y-1 text-xs text-slate-500">名称 <input name="name" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label>
              <label className="block space-y-1 text-xs text-slate-500">类型 <input name="provider_type" placeholder="mock / oai_compat" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label>
              <label className="block space-y-1 text-xs text-slate-500">Base URL <input name="base_url" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label>
              <label className="block space-y-1 text-xs text-slate-500">API Key 环境变量名 <input name="api_key_env_var" placeholder="例如 OAI_API_KEY" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label>
              <label className="block space-y-1 text-xs text-slate-500">默认模型 <input name="default_model" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label>
              <label className="flex items-center gap-2 text-xs text-slate-500"><input type="checkbox" name="is_active" /> 启用</label>
            </>
          )}
          {tab === "models" && (
            <>
              <label className="block space-y-1 text-xs text-slate-500">Provider ID <input name="provider_id" type="number" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label>
              <label className="block space-y-1 text-xs text-slate-500">名称 <input name="name" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label>
              <label className="block space-y-1 text-xs text-slate-500">模型标识 <input name="model" placeholder="例如 gpt-4o" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label>
              <label className="block space-y-1 text-xs text-slate-500">显示名称 <input name="display_name" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label>
              <label className="block space-y-1 text-xs text-slate-500">上下文窗口 <input name="context_window" type="number" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label>
              <div className="flex gap-3">
                <label className="block flex-1 space-y-1 text-xs text-slate-500">输入价格（$/1M tokens） <input name="input_price_per_1m_tokens" step="0.01" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label>
                <label className="block flex-1 space-y-1 text-xs text-slate-500">输出价格（$/1M tokens） <input name="output_price_per_1m_tokens" step="0.01" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label>
              </div>
              <label className="block space-y-1 text-xs text-slate-500">币种 <input name="currency" className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white" /></label>
              <div className="flex gap-3">
                <label className="flex items-center gap-2 text-xs text-slate-500"><input type="checkbox" name="is_default" /> 默认</label>
                <label className="flex items-center gap-2 text-xs text-slate-500"><input type="checkbox" name="is_active" /> 启用</label>
              </div>
            </>
          )}
          <div className="flex gap-2">
            <button type="submit" disabled={saving} className="rounded bg-cyan-600 px-4 py-2 text-sm text-white hover:bg-cyan-700 disabled:opacity-50">{saving ? "保存中..." : "保存"}</button>
            <button type="button" onClick={() => { setShowForm(false); setEditing(null); }} className="rounded border border-slate-700 px-4 py-2 text-sm text-slate-400 hover:text-white">取消</button>
          </div>
        </form>
      )}

      {tab === "providers" && providers.map((p) => (
        <div key={p.id} className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900 p-3">
          <div>
            <span className="font-medium">{p.name || "未命名"}</span>
            <span className="ml-2 text-xs text-slate-500">{p.provider_type} / {p.default_model || "未设置默认模型"}</span>
            {p.is_active && <span className="ml-2 text-xs text-emerald-400">已启用</span>}
          </div>
          <div className="flex gap-2">
            <button onClick={() => { setEditing({ id: p.id, prefix: "/api/ai/providers" }); setTab("providers"); }} className="text-xs text-cyan-400 hover:underline">编辑</button>
            <button onClick={() => del(`/api/ai/providers/${p.id}`)} className="text-xs text-red-400 hover:underline">删除</button>
          </div>
        </div>
      ))}

      {tab === "models" && models.map((m) => (
        <div key={m.id} className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900 p-3">
          <div>
            <span className="font-medium">{m.display_name || m.name || "未命名"}</span>
            <span className="ml-2 text-xs text-slate-500">模型：{m.model}</span>
            {m.is_default && <span className="ml-2 text-xs text-cyan-400">默认</span>}
            {m.is_active && <span className="ml-2 text-xs text-emerald-400">启用</span>}
          </div>
          <div className="flex gap-2">
            {!m.is_default && <button onClick={() => setDefaultModel(m.id)} className="text-xs text-cyan-400 hover:underline">设为默认</button>}
            <button onClick={() => { setEditing({ id: m.id, prefix: "/api/ai/models" }); setTab("models"); }} className="text-xs text-cyan-400 hover:underline">编辑</button>
            <button onClick={() => del(`/api/ai/models/${m.id}`)} className="text-xs text-red-400 hover:underline">删除</button>
          </div>
        </div>
      ))}

      {tab === "logs" && (
        <>
          {summary && (
            <div className="grid grid-cols-3 gap-3 rounded-lg border border-slate-800 bg-slate-900 p-4 text-xs">
              <div><span className="text-slate-500">调用次数</span><div className="text-lg">{summary.total_calls}</div></div>
              <div><span className="text-slate-500">成功/失败</span><div className="text-lg">{summary.total_success}/{summary.total_error}</div></div>
              <div><span className="text-slate-500">预估费用</span><div className="text-lg">${summary.total_estimated_cost?.toFixed(6) || "0"}</div></div>
            </div>
          )}
          {logs.map((l) => (
            <div key={l.id} className="flex items-center justify-between rounded border border-slate-800 bg-slate-900 p-3 text-xs">
              <div>
                <span className={`${l.status === "error" ? "text-red-400" : "text-slate-300"}`}>{l.feature_name}</span>
                <span className="ml-2 text-slate-500">{l.model} / {l.provider_type} / {l.total_tokens || "?"}t / {l.latency_ms}ms {l.estimated_cost != null ? `$${Number(l.estimated_cost).toFixed(6)}` : ""}</span>
                {l.error_message && <div className="mt-0.5 text-red-400">{l.error_message.slice(0, 100)}</div>}
              </div>
              <span className="text-slate-600">{new Date(l.created_at).toLocaleString("zh-CN")}</span>
            </div>
          ))}
          {logs.length === 0 && <p className="p-3 text-xs text-slate-600">暂无用量日志</p>}
        </>
      )}
    </div>
  );
}
