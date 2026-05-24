export function ModelSettingsPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Model Settings</h2>
      <div className="rounded-lg border border-dashed border-slate-700 p-10 text-center">
        <p className="text-slate-400 mb-2">模型设置页面 — 后续用于配置 AI Provider 和模型参数。</p>
        <p className="text-sm text-slate-600">后续将支持：</p>
        <ul className="mt-3 text-sm text-slate-500 space-y-1">
          <li>— 选择 AI Provider（当前仅 mock）</li>
          <li>— 配置模型参数（temperature、max_tokens 等）</li>
          <li>— 管理 API Key 引用（不直接展示明文）</li>
          <li>— 测试模型连通性</li>
        </ul>
      </div>
    </div>
  );
}
