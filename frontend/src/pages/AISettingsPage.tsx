import { useEffect, useState } from "react";
import { getBaseUrl } from "../api/client";

const BASE = getBaseUrl();

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
  const [partialErrors, setPartialErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState<number | null>(null);
  const [testResult, setTestResult] = useState<{ok:boolean;message:string} | null>(null);
  const [keyStatuses, setKeyStatuses] = useState<Record<number,{has:boolean;masked:string}>>({});
  const [keyInputs, setKeyInputs] = useState<Record<number, string>>({});

  async function load() {
    setLoading(true); setError(null); setPartialErrors({});
    const settle = await Promise.allSettled([
      fetch(`${BASE}/api/ai/providers`).then(r=>r.json()),
      fetch(`${BASE}/api/ai/models`).then(r=>r.json()),
      fetch(`${BASE}/api/ai/usage-logs`).then(r=>r.json()),
      fetch(`${BASE}/api/ai/usage-logs/summary`).then(r=>r.json()),
    ]);
    const [p, m, l, s] = settle;
    if (p.status === "rejected") { setError("后端可能未启动"); setLoading(false); return; }
    const plist = Array.isArray(p.value) ? p.value : [];
    setProviders(plist);
    if (m.status === "rejected") setPartialErrors(prev=>({...prev,models:"模型列表暂时不可用"}));
    else setModels(Array.isArray(m.value) ? m.value : []);
    if (l.status === "rejected") setPartialErrors(prev=>({...prev,logs:"调用日志暂时不可用"}));
    else setLogs(Array.isArray(l.value) ? l.value : []);
    if (s.status === "rejected") setPartialErrors(prev=>({...prev,summary:"调用统计暂时不可用"}));
    else setSummary(s.value);
    setLoading(false);
    for (const pv of plist) {
      if (pv.api_key_mode === "direct_local") {
        fetch(`${BASE}/api/ai/providers/${pv.id}/local-key/status`).then(r=>r.json()).then(d=>{
          setKeyStatuses(prev=>({...prev,[pv.id]:{has:d.has_direct_api_key,masked:d.masked_api_key}}));
        }).catch(()=>{});
      }
    }
  }

  useEffect(() => { load(); }, []);

  async function handleSave(formEl: HTMLFormElement, path: string, isNew: boolean) {
    setSaving(true); setError(null);
    const fd = new FormData(formEl);
    const body: Record<string,any> = {};
    for (const [k, v] of fd.entries()) {
      if (k === "is_active" || k === "is_default") body[k] = v === "on";
      else if (v) body[k] = v;
    }
    try {
      const r = await fetch(`${BASE}${path}`, {method:isNew?"POST":"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail||`HTTP ${r.status}`);
      setShowForm(false); setEditing(null); setSuccess("已保存"); load();
    } catch(e) { setError(e instanceof Error ? e.message : "保存失败"); }
    finally { setSaving(false); }
  }

  async function saveLocalKey(providerId: number) {
    const key = keyInputs[providerId] || "";
    if (!key.trim()) { setError("请输入 API Key"); return; }
    setSaving(true); setError(null);
    try {
      const r = await fetch(`${BASE}/api/ai/providers/${providerId}/local-key`, {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({api_key:key})});
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail||`HTTP ${r.status}`);
      setKeyStatuses(prev=>({...prev,[providerId]:{has:true,masked:d.masked_api_key}}));
      setKeyInputs(prev=>{const n={...prev};delete n[providerId];return n;});
      setSuccess("密钥已保存到本机用户目录");
    } catch(e) { setError(e instanceof Error ? e.message : "保存密钥失败"); }
    finally { setSaving(false); }
  }

  async function deleteLocalKey(providerId: number) {
    setError(null);
    try {
      await fetch(`${BASE}/api/ai/providers/${providerId}/local-key`, {method:"DELETE"});
      setKeyStatuses(prev=>({...prev,[providerId]:{has:false,masked:""}}));
      setSuccess("本机密钥已删除");
    } catch(e) { setError(e instanceof Error ? e.message : "删除密钥失败"); }
  }

  async function testConnection(providerId: number) {
    setTesting(providerId); setTestResult(null); setError(null);
    try {
      const r = await fetch(`${BASE}/api/ai/providers/${providerId}/test`, {method:"POST"});
      const d = await r.json();
      setTestResult({ok:!!d.ok,message:d.message||(d.ok?"连接成功":"连接失败")});
    } catch(e) { setTestResult({ok:false,message:"测试请求失败，请检查后端是否启动"}); }
    finally { setTesting(null); }
  }

  async function del(path: string) {
    if (!confirm("确认删除？")) return;
    await fetch(`${BASE}${path}`, {method:"DELETE"}); setSuccess("已删除"); load();
  }
  async function setDefaultModel(id: number) {
    await fetch(`${BASE}/api/ai/models/${id}/set-default`, {method:"POST"});
    setSuccess("已设为默认模型"); load();
  }

  const tabs = [
    {key:"providers" as const, label:`服务商 (${providers.length})`},
    {key:"models" as const, label:`模型 (${models.length})`},
    {key:"logs" as const, label:`调用日志 (${logs.length})`},
  ];

  return (
    <div className="space-y-4" style={{maxWidth:900}}>
      <h2 className="text-xl font-bold" style={{color:"var(--text-primary)"}}>AI 设置</h2>
      {error && <div className="toast toast-error">{error}</div>}
      {success && <div className="toast toast-success">{success}</div>}
      <p className="text-xs" style={{color:"var(--text-muted)"}}>配置 AI 服务商和模型。支持环境变量和本机直填两种方式。真实密钥仅保存在你的电脑上，不会提交到 GitHub。</p>

      {loading ? <p className="text-sm" style={{color:"var(--text-muted)"}}>加载中...</p> : (
        <div className="flex flex-wrap gap-2">
          {tabs.map(t=><button key={t.key} onClick={()=>{setTab(t.key);setError(null);setSuccess(null);setTestResult(null)}} className={`tab-btn ${tab===t.key?"active":""}`}>{t.label}</button>)}
          {!error && <button onClick={()=>{setShowForm(true);setEditing(null);setTestResult(null)}} className="btn btn-primary text-xs">+ 新增服务商</button>}
        </div>
      )}

      {(showForm||editing) && (
        <form onSubmit={e=>{e.preventDefault();handleSave(e.currentTarget, editing?`${editing.prefix}/${editing.id}`:tab==="providers"?"/api/ai/providers":tab==="models"?"/api/ai/models":"",!editing)}} className="card space-y-3">
          <h3 className="font-semibold text-sm" style={{color:"var(--text-primary)"}}>{editing?"编辑":"新增"}{tab==="providers"?"服务商":"模型"}</h3>
          {tab==="providers"&&<>
            <label className="text-xs block space-y-1" style={{color:"var(--text-secondary)"}}>服务商名称 <input name="name" placeholder="例如 OAI" /></label>
            <label className="text-xs block space-y-1" style={{color:"var(--text-secondary)"}}>类型 <select name="provider_type"><option value="mock">Mock 本地演示</option><option value="oai_compat">OAI 兼容接口</option></select></label>
            <label className="text-xs block space-y-1" style={{color:"var(--text-secondary)"}}>Base URL <input name="base_url" placeholder="https://your-api-endpoint/v1" /></label>
            <label className="text-xs block space-y-1" style={{color:"var(--text-secondary)"}}>密钥模式 <select name="api_key_mode"><option value="env_var">环境变量</option><option value="direct_local">本机直填</option></select></label>
            <label className="text-xs block space-y-1" style={{color:"var(--text-secondary)"}}>环境变量名<input name="api_key_env_var" placeholder="OAI_API_KEY" /></label>
            <label className="text-xs block space-y-1" style={{color:"var(--text-secondary)"}}>默认模型 <input name="default_model" placeholder="gpt-4o-mini" /></label>
            <label className="flex items-center gap-2 text-xs" style={{color:"var(--text-secondary)"}}><input type="checkbox" name="is_active" /> 启用</label>
          </>}
          {tab==="models"&&<>
            <label className="text-xs block space-y-1" style={{color:"var(--text-secondary)"}}>服务商 ID <input name="provider_id" type="number" /></label>
            <label className="text-xs block space-y-1" style={{color:"var(--text-secondary)"}}>模型标识 <input name="model" placeholder="gpt-4o-mini" /></label>
            <label className="text-xs block space-y-1" style={{color:"var(--text-secondary)"}}>显示名称 <input name="display_name" /></label>
            <div className="flex gap-3">
              <label className="flex-1 block text-xs space-y-1" style={{color:"var(--text-secondary)"}}>入价$/1M <input name="input_price_per_1m_tokens" step="0.01" /></label>
              <label className="flex-1 block text-xs space-y-1" style={{color:"var(--text-secondary)"}}>出价$/1M <input name="output_price_per_1m_tokens" step="0.01" /></label>
            </div>
            <label className="flex items-center gap-2 text-xs" style={{color:"var(--text-secondary)"}}><input type="checkbox" name="is_default" /> 默认模型</label>
            <label className="flex items-center gap-2 text-xs" style={{color:"var(--text-secondary)"}}><input type="checkbox" name="is_active" /> 启用</label>
          </>}
          <div className="flex gap-2"><button type="submit" disabled={saving} className="btn btn-primary text-xs">{saving?"保存中...":"保存"}</button><button type="button" onClick={()=>{setShowForm(false);setEditing(null)}} className="btn btn-secondary text-xs">取消</button></div>
        </form>
      )}

      {partialErrors.providers && <div className="toast toast-warning">{partialErrors.providers}</div>}
      {testResult && <div className={`toast ${testResult.ok?"toast-success":"toast-error"}`}>{testResult.message}</div>}

      {tab==="providers" && providers.map(p=>(
        <div key={p.id} className="card space-y-3">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <span className="font-medium" style={{color:"var(--text-primary)"}}>{p.name||"未命名"}</span>
              <span className="ml-2 badge" style={{background:"var(--bg-input)",color:"var(--text-secondary)"}}>{p.provider_type}</span>
              {p.is_active && <span className="ml-2 badge" style={{background:"var(--emerald-bg)",color:"var(--emerald-text)"}}>已启用</span>}
              <span className="ml-2 badge" style={{background:"var(--bg-input)",color:"var(--text-muted)"}}>{p.api_key_mode==="direct_local"?"本机直填":"环境变量"}</span>
            </div>
            <div className="flex gap-2 flex-wrap">
              <button onClick={()=>testConnection(p.id)} disabled={testing===p.id} className="btn btn-secondary text-xs">{testing===p.id?"测试中...":"测试连接"}</button>
              <button onClick={()=>{setEditing({id:p.id,prefix:"/api/ai/providers"});setTab("providers")}} className="btn btn-secondary text-xs">编辑</button>
              <button onClick={()=>del(`/api/ai/providers/${p.id}`)} className="btn btn-danger text-xs">删除</button>
            </div>
          </div>
          <div className="text-xs space-y-1" style={{color:"var(--text-secondary)"}}>
            <div>Base URL: {p.base_url||"未设置"} · 默认模型: {p.default_model||"未设置"}</div>
            {p.api_key_env_var && <div>环境变量: {p.api_key_env_var}</div>}
          </div>
          {p.api_key_mode==="direct_local" && (
            <div className="flex items-center gap-2 flex-wrap">
              {keyStatuses[p.id]?.has ? (
                <>
                  <span className="badge" style={{background:"var(--emerald-bg)",color:"var(--emerald-text)"}}>密钥已保存</span>
                  <span className="text-xs" style={{color:"var(--text-muted)"}}>{keyStatuses[p.id]?.masked}</span>
                  <button onClick={()=>deleteLocalKey(p.id)} className="btn btn-danger text-xs">删除密钥</button>
                </>
              ) : (
                <div className="flex items-center gap-2">
                  <input type="password" value={keyInputs[p.id]||""} onChange={e=>setKeyInputs(prev=>({...prev,[p.id]:e.target.value}))}
                    placeholder="粘贴 API Key" className="!w-64" />
                  <button onClick={()=>saveLocalKey(p.id)} disabled={saving} className="btn btn-primary text-xs">保存密钥</button>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
      {tab==="providers" && !loading && !error && providers.length===0 && <p className="empty-state">暂无 AI 服务商，请先新增服务商配置。</p>}

      {partialErrors.models && <div className="toast toast-warning">{partialErrors.models}</div>}
      {tab==="models" && models.map(m=>(
        <div key={m.id} className="card flex items-center justify-between flex-wrap gap-2">
          <div>
            <span className="font-medium" style={{color:"var(--text-primary)"}}>{m.display_name||m.name||"未命名"}</span>
            <span className="ml-2 text-xs" style={{color:"var(--text-muted)"}}>{m.model}</span>
            {m.is_default&&<span className="ml-2 badge" style={{background:"var(--cyan-bg)",color:"var(--cyan-text)"}}>默认</span>}
            {m.is_active&&<span className="ml-2 badge" style={{background:"var(--emerald-bg)",color:"var(--emerald-text)"}}>启用</span>}
          </div>
          <div className="flex gap-2">
            {!m.is_default&&<button onClick={()=>setDefaultModel(m.id)} className="btn btn-secondary text-xs">设为默认</button>}
            <button onClick={()=>{setEditing({id:m.id,prefix:"/api/ai/models"});setTab("models")}} className="btn btn-secondary text-xs">编辑</button>
            <button onClick={()=>del(`/api/ai/models/${m.id}`)} className="btn btn-danger text-xs">删除</button>
          </div>
        </div>
      ))}
      {tab==="models" && !loading && !error && !partialErrors.models && models.length===0 && <p className="empty-state">暂无模型，请先新增模型配置。</p>}

      {tab==="logs" && <>
        {partialErrors.summary && <div className="toast toast-warning">{partialErrors.summary}</div>}
        {partialErrors.logs && <div className="toast toast-warning">{partialErrors.logs}</div>}
        {summary && <div className="card grid grid-cols-4 gap-3 text-xs">
          <div><span style={{color:"var(--text-muted)"}}>调用次数</span><div className="text-lg" style={{color:"var(--text-primary)"}}>{summary.total_calls??0}</div></div>
          <div><span style={{color:"var(--text-muted)"}}>成功/失败</span><div className="text-lg" style={{color:"var(--text-primary)"}}>{summary.total_success??0}/{summary.total_error??0}</div></div>
          <div><span style={{color:"var(--text-muted)"}}>总 Token</span><div className="text-lg" style={{color:"var(--text-primary)"}}>{summary.total_tokens??0}</div></div>
          <div><span style={{color:"var(--text-muted)"}}>预估费用</span><div className="text-lg" style={{color:"var(--text-primary)"}}>${summary.total_estimated_cost!=null?Number(summary.total_estimated_cost).toFixed(6):"0.00"}</div></div>
        </div>}
        {logs.map(l=>(<div key={l.id} className="card flex items-center justify-between flex-wrap gap-2 text-xs">
          <div><span style={{color:l.status==="error"?"var(--red-text)":"var(--text-secondary)"}}>{l.feature_name}</span><span className="ml-2" style={{color:"var(--text-muted)"}}>{l.model} · {l.provider_type} · {l.total_tokens||"?"}t · {l.latency_ms}ms {l.estimated_cost!=null?`$${Number(l.estimated_cost).toFixed(6)}`:""}</span>{l.error_message&&<div style={{color:"var(--red-text)"}} className="mt-0.5">{l.error_message.slice(0,100)}</div>}</div>
          <span style={{color:"var(--text-muted)"}}>{new Date(l.created_at).toLocaleString("zh-CN")}</span>
        </div>))}
        {!loading && !error && !partialErrors.logs && logs.length===0 && <p className="empty-state">暂无调用日志，完成一次 AI 生成后会显示记录。</p>}
      </>}
    </div>
  );
}
