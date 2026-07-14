import React from "react";
import { NavLink } from "react-router-dom";
import { BarChart3, Library, Settings, Home, Sparkles } from "lucide-react";

export default function Sidebar({ open, onToggle, status }) {
  const links = [
    { to: "/", label: "控制台", icon: Home },
    { to: "/evaluate", label: "质量评估", icon: BarChart3 },
    { to: "/knowledge", label: "写作技巧", icon: Library },
    { to: "/settings", label: "系统设置", icon: Settings },
  ];
  return (
    <aside className={`${open ? "w-56" : "w-0"} transition-all duration-300 bg-gray-900/90 backdrop-blur-sm border-r border-gray-800 flex flex-col shrink-0 overflow-hidden`}>
      <div className="h-14 flex items-center gap-2.5 px-4 border-b border-gray-800 shrink-0">
        <Sparkles className="text-soul-400" size={22} />
        <span className="font-semibold text-base bg-gradient-to-r from-soul-400 to-pink-400 bg-clip-text text-transparent">Soultext</span>
      </div>
      <nav className="flex-1 py-3 px-2 space-y-1 overflow-y-auto">
        {links.map(l => (
          <NavLink key={l.to} to={l.to} end={l.to === "/"}
            className={({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
              isActive ? "bg-soul-600/20 text-soul-300 border border-soul-600/30" : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/50"}`}>
            <l.icon size={18} /> {l.label}
          </NavLink>
        ))}
      </nav>
      <div className="p-3 border-t border-gray-800">
        {status && (
          <div className="text-xs text-gray-500 space-y-1">
            <div className="flex items-center gap-1.5">
              <span className={`w-1.5 h-1.5 rounded-full ${status.graph_store ? "bg-green-500" : "bg-red-500"}`} />
              <span>{status.graph_store ? "服务运行中" : "服务离线"}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Sparkles size={12} className="text-soul-400" />
              <span>{status.novels || 0} 部作品</span>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
