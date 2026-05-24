import { Outlet, useLocation } from "react-router-dom";
import { Sidebar } from "./Sidebar";

const titles: Record<string, string> = {
  "/": "Dashboard",
  "/projects": "Projects",
  "/characters": "Characters",
  "/chapters": "Chapters",
  "/story-bible": "Story Bible",
  "/model-settings": "Model Settings",
  "/daily-writer": "Daily Writer",
  "/reference-novels": "Reference Novels",
};

export function Layout() {
  const loc = useLocation();
  const base = "/" + (loc.pathname.split("/")[1] ?? "");
  const title = titles[base] ?? "NovelMind";

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center justify-between border-b border-slate-800 px-6">
          <h1 className="text-lg font-semibold">{title}</h1>
          <div className="rounded border border-slate-700 px-3 py-1 text-xs text-slate-500">
            provider: mock
          </div>
        </header>
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
