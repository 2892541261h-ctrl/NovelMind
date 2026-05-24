import { useMemo, useState } from "react";

type PageKey =
  | "dashboard"
  | "projects"
  | "writer"
  | "story-bible"
  | "model-settings"
  | "daily-writer";

type Page = {
  key: PageKey;
  label: string;
  description: string;
};

const pages: Page[] = [
  {
    key: "dashboard",
    label: "Dashboard",
    description: "查看项目状态、章节进度和今日待办。"
  },
  {
    key: "projects",
    label: "Projects",
    description: "管理小说项目和基础元数据。"
  },
  {
    key: "writer",
    label: "Writer",
    description: "章节写作工作台占位。"
  },
  {
    key: "story-bible",
    label: "Story Bible",
    description: "维护世界观、角色、地点和时间线。"
  },
  {
    key: "model-settings",
    label: "Model Settings",
    description: "后续在这里配置模型路由，目前仅显示 mock。"
  },
  {
    key: "daily-writer",
    label: "Daily Writer",
    description: "每日自动写作流程占位，默认关闭。"
  }
];

const mockProject = {
  name: "demo-project",
  genre: "长篇小说",
  status: "骨架阶段",
  chapters: 0
};

export default function App() {
  const [activeKey, setActiveKey] = useState<PageKey>("dashboard");
  const activePage = useMemo(
    () => pages.find((page) => page.key === activeKey) ?? pages[0],
    [activeKey]
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="flex min-h-screen">
        <aside className="w-64 border-r border-slate-800 bg-slate-950/95 px-4 py-5">
          <div className="mb-8">
            <div className="text-lg font-semibold tracking-wide">NovelMind</div>
            <div className="mt-1 text-sm text-slate-400">AI 长篇小说创作平台</div>
          </div>

          <nav className="space-y-1">
            {pages.map((page) => (
              <button
                key={page.key}
                type="button"
                onClick={() => setActiveKey(page.key)}
                className={[
                  "w-full rounded-md px-3 py-2 text-left text-sm transition",
                  activeKey === page.key
                    ? "bg-cyan-500 text-slate-950"
                    : "text-slate-300 hover:bg-slate-900 hover:text-white"
                ].join(" ")}
              >
                {page.label}
              </button>
            ))}
          </nav>
        </aside>

        <main className="flex min-w-0 flex-1 flex-col">
          <header className="flex h-16 items-center justify-between border-b border-slate-800 px-6">
            <div>
              <div className="text-sm text-slate-400">当前页面</div>
              <h1 className="text-xl font-semibold">{activePage.label}</h1>
            </div>
            <div className="rounded-md border border-slate-800 px-3 py-2 text-sm text-slate-300">
              provider: mock
            </div>
          </header>

          <section className="flex-1 p-6">
            <div className="grid gap-4 lg:grid-cols-3">
              <div className="rounded-lg border border-slate-800 bg-slate-900 p-5 lg:col-span-2">
                <h2 className="text-lg font-semibold">{activePage.label}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-300">
                  {activePage.description}
                </p>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
                <h2 className="text-lg font-semibold">项目概览</h2>
                <dl className="mt-4 space-y-3 text-sm">
                  <div className="flex justify-between gap-4">
                    <dt className="text-slate-400">项目</dt>
                    <dd>{mockProject.name}</dd>
                  </div>
                  <div className="flex justify-between gap-4">
                    <dt className="text-slate-400">类型</dt>
                    <dd>{mockProject.genre}</dd>
                  </div>
                  <div className="flex justify-between gap-4">
                    <dt className="text-slate-400">状态</dt>
                    <dd>{mockProject.status}</dd>
                  </div>
                  <div className="flex justify-between gap-4">
                    <dt className="text-slate-400">章节</dt>
                    <dd>{mockProject.chapters}</dd>
                  </div>
                </dl>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
