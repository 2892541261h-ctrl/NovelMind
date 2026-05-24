export function DailyWriterPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Daily Writer</h2>
      <div className="rounded-lg border border-dashed border-slate-700 p-10 text-center">
        <p className="text-slate-400 mb-2">Daily Writer — 每日自动生成小说章节。</p>
        <p className="text-sm text-slate-600">后续将支持：</p>
        <ul className="mt-3 text-sm text-slate-500 space-y-1">
          <li>— 配置每日生成计划</li>
          <li>— 预览下一章信息</li>
          <li>— 查看生成历史和状态</li>
          <li>— 手动触发单章生成</li>
        </ul>
        <p className="mt-4 text-xs text-slate-600">当前默认关闭。章节安全规则：不覆盖已有章节，目标文件存在时自动失败。</p>
      </div>
    </div>
  );
}
