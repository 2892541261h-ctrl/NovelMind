import { NavLink } from "react-router-dom";
import { useTheme } from "../hooks/useTheme";

const sections = [
  { label: "创作", items: [
    { to: "/", label: "仪表盘", end: true },
    { to: "/reference-novels", label: "参考小说" },
    { to: "/story-bible", label: "故事圣经" },
    { to: "/daily-writer", label: "每日写作" },
  ]},
  { label: "管理", items: [
    { to: "/projects", label: "项目设置" },
    { to: "/characters", label: "角色管理" },
    { to: "/chapters", label: "章节管理" },
    { to: "/model-settings", label: "AI 设置" },
  ]},
];

export function Sidebar() {
  const { theme, toggle } = useTheme();
  return (
    <aside style={{background:"var(--bg-sidebar)",borderRight:"1px solid var(--border)"}}
      className="w-56 flex flex-col h-screen sticky top-0 overflow-y-auto">
      <div className="px-4 py-4">
        <div className="text-base font-bold tracking-wide" style={{color:"var(--text-primary)"}}>NovelMind</div>
        <div className="text-xs mt-0.5" style={{color:"var(--text-muted)"}}>长篇小说创作平台</div>
      </div>
      <nav className="flex-1 px-3 space-y-4">
        {sections.map(sec => (
          <div key={sec.label}>
            <div className="sidebar-section">{sec.label}</div>
            {sec.items.map(item => (
              <NavLink key={item.to} to={item.to} end={item.end}
                className={({isActive}) => `sidebar-link ${isActive?"active":""}`}>
                {item.label}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>
      <div className="px-3 py-3 border-t space-y-2" style={{borderColor:"var(--border)"}}>
        <button onClick={toggle} className="sidebar-link w-full text-left">
          {theme === "light" ? "深色模式" : "浅色模式"}
        </button>
        <div className="text-xs px-2" style={{color:"var(--text-muted)"}}>NovelMind V1 Final</div>
      </div>
    </aside>
  );
}
