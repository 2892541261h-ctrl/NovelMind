export function StoryBiblePage() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Story Bible</h2>
      <div className="rounded-lg border border-dashed border-slate-700 p-10 text-center">
        <p className="text-slate-400 mb-2">Story Bible 是小说世界观、角色、地点、规则和剧情线的完整设定档案。</p>
        <p className="text-sm text-slate-600">后续将支持：</p>
        <ul className="mt-3 text-sm text-slate-500 space-y-1">
          <li>— 从数据库加载并展示 Story Bible 数据</li>
          <li>— 从 Reference Creation Profile 生成原创 Story Bible</li>
          <li>— 在线编辑和版本管理</li>
        </ul>
      </div>
    </div>
  );
}
