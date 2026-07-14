import React, { useState, useEffect } from "react";
import { Library, Search, BookOpen, Lightbulb } from "lucide-react";

const catColors = {"情感技巧":"tag-red","人物技巧":"tag-blue","情节技巧":"tag-amber","场景技巧":"tag-green","文笔技巧":"tag-purple","结构技巧":"tag-gray","节奏技巧":"tag-amber","修改技巧":"tag-purple"};

export default function KnowledgeBase() {
  const [categories, setCategories] = useState(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetch("/api/knowledge/categories").then(r=>r.json()).then(d=>{setCategories(d);setLoading(false)}).catch(()=>setLoading(false)); }, []);

  async function search() {
    if (!query.trim()) { setResults(null); return; }
    const r = await fetch("/api/knowledge/search?q="+encodeURIComponent(query));
    setResults(await r.json());
  }

  if (loading) return <div className="animate-pulse text-center py-12 text-gray-500">加载中...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2"><Library className="text-soul-400" size={24} /> 写作技巧库</h2>
        <p className="text-gray-500 text-sm mt-1">整合 doc/ 下所有写作技巧，赋能 AI 创作</p>
      </div>
      <div className="card">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
            <input className="input-field w-full pl-9" value={query} onChange={e=>setQuery(e.target.value)} onKeyDown={e=>e.key==="Enter"&&search()} placeholder="搜索写作技巧..." />
          </div>
          <button onClick={search} className="btn-primary">搜索</button>
        </div>
      </div>
      {results ? (
        <div className="card">
          <div className="card-header"><Search size={18} className="text-soul-400" /> 搜索结果 ({results.length})</div>
          {results.length === 0 ? <div className="text-center py-8 text-gray-500">未找到</div> : (
            <div className="space-y-3">{(results||[]).map(r => (
              <div key={r.id} className="p-4 bg-gray-800/50 rounded-lg">
                <div className="flex items-center gap-2 mb-2"><span className="font-medium text-white">{r.title}</span><span className={catColors[r.category]||"tag-gray"}>{r.category}</span></div>
                <p className="text-sm text-gray-400 mb-2">{r.summary}</p>
                <div className="flex flex-wrap gap-2">{(r.key_points||[]).slice(0,4).map((p,i) => <span key={i} className="text-xs bg-gray-800 text-gray-500 px-2 py-1 rounded">{p}</span>)}</div>
              </div>
            ))}</div>
          )}
        </div>
      ) : categories ? (
        <div className="grid md:grid-cols-2 gap-4">
          {Object.entries(categories).map(([cat, techs]) => (
            <div key={cat} className="card">
              <div className="card-header"><Lightbulb size={18} className="text-soul-400" />{cat}<span className="text-xs text-gray-600 font-normal"> ({techs.length} 条)</span></div>
              <div className="space-y-3">{(techs||[]).map(t => (
                <details key={t.id} className="group">
                  <summary className="flex items-center gap-2 cursor-pointer text-sm text-gray-300 hover:text-white py-1.5"><BookOpen size={14} className="text-gray-600 group-open:text-soul-400" /> {t.title}</summary>
                  <div className="pl-6 mt-1 text-xs text-gray-500"><p>{t.summary}</p></div>
                </details>
              ))}</div>
            </div>
          ))}
        </div>
      ) : <div className="text-center py-12 text-gray-500">知识库未加载</div>}
    </div>
  );
}
