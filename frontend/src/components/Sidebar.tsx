import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/projects", label: "Projects" },
  { to: "/story-bible", label: "Story Bible" },
  { to: "/characters", label: "Characters" },
  { to: "/chapters", label: "Chapters" },
  { to: "/model-settings", label: "Model Settings" },
  { to: "/daily-writer", label: "Daily Writer" },
];

export function Sidebar() {
  return (
    <aside className="w-56 border-r border-slate-800 bg-slate-950/95 px-4 py-5 flex flex-col">
      <div className="mb-8">
        <div className="text-lg font-semibold tracking-wide text-white">NovelMind</div>
        <div className="mt-1 text-xs text-slate-500">AI 长篇小说创作平台</div>
      </div>
      <nav className="flex-1 space-y-0.5">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) =>
              `block rounded-md px-3 py-2 text-sm transition ${
                isActive
                  ? "bg-cyan-500/20 text-cyan-300 font-medium"
                  : "text-slate-400 hover:bg-slate-900 hover:text-white"
              }`
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
