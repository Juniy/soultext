import React, { useState, useEffect } from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import { Menu, X } from "lucide-react";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import NovelDetail from "./pages/NovelDetail";
import Evaluation from "./pages/Evaluation";
import KnowledgeBase from "./pages/KnowledgeBase";
import SettingsPage from "./pages/SettingsPage";

const titles = {
  "/": "控制台",
  "/evaluate": "质量评估",
  "/knowledge": "写作技巧库",
  "/settings": "系统设置",
};

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [status, setStatus] = useState(null);
  const loc = useLocation();

  useEffect(() => {
    fetch("/api/system/status").then(r => r.json()).then(setStatus).catch(() => setStatus({error:1}));
  }, []);

  const title = Object.entries(titles).find(([k]) => loc.pathname === k)?.[1] || (loc.pathname.startsWith("/novel") ? "小说创作" : "Soultext");

  return (
    <div className="flex h-screen overflow-hidden bg-gray-950 text-gray-100">
      <Sidebar open={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} status={status} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-14 bg-gray-900/80 backdrop-blur-sm border-b border-gray-800 flex items-center justify-between px-4 lg:px-6 shrink-0">
          <div className="flex items-center gap-3">
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-gray-400 hover:text-white p-1">
              {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            <h1 className="text-sm font-medium text-gray-300 hidden sm:block">{title}</h1>
          </div>
          {status && (
            <div className="flex items-center gap-2 text-xs">
              <span className={`w-2 h-2 rounded-full ${status.graph_store ? "bg-green-500" : "bg-red-500"}`} />
              <span className="text-gray-500 hidden md:inline">{status.nodes||0} 节点 | {status.edges||0} 关系</span>
            </div>
          )}
        </header>
        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          <div className="max-w-7xl mx-auto animate-fade-in">
            <Routes>
              <Route path="/" element={<Dashboard status={status} />} />
              <Route path="/novel/:id" element={<NovelDetail />} />
              <Route path="/evaluate" element={<Evaluation />} />
              <Route path="/knowledge" element={<KnowledgeBase />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </div>
        </main>
      </div>
    </div>
  );
}
