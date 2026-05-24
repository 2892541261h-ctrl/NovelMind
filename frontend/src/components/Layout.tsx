import { Outlet, useLocation } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { useTheme } from "../hooks/useTheme";

const titles: Record<string, string> = {
  "/": "仪表盘",
  "/projects": "项目设置",
  "/reference-novels": "参考小说",
  "/story-bible": "故事圣经",
  "/characters": "角色管理",
  "/chapters": "章节管理",
  "/daily-writer": "每日写作",
  "/model-settings": "AI 设置",
};

export function Layout() {
  const loc = useLocation();
  const base = "/" + (loc.pathname.split("/")[1] ?? "");
  const title = titles[base] ?? "NovelMind";
  const { theme } = useTheme();

  return (
    <div style={{background:"var(--bg-primary)"}} className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 min-w-0 flex flex-col">
        <header style={{background:"var(--bg-header)",borderBottom:"1px solid var(--border)"}}
          className="flex items-center justify-between h-14 px-6 sticky top-0 z-10">
          <h1 className="text-lg font-semibold" style={{color:"var(--text-primary)"}}>{title}</h1>
          <div className="flex items-center gap-3">
            <span style={{color:"var(--text-muted)"}} className="text-xs">
              {theme === "light" ? "浅色" : "深色"} · mock
            </span>
          </div>
        </header>
        <main className="flex-1 overflow-auto p-6 max-w-7xl mx-auto w-full">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
