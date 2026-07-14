import React, { useState, useEffect } from "react";
import { BarChart3, Award, CheckCircle, Sparkles, FileText } from "lucide-react";

export default function Evaluation() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [standards, setStandards] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => { fetch("/api/evaluate/standards").then(r=>r.json()).then(setStandards).catch(()=>{}); }, []);

  async function evaluate() {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const r = await fetch("/api/evaluate", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({text}) });
      setResult(await r.json());
    } catch(e){} finally { setLoading(false); }
  }

  const grades = { "S":"from-yellow-400 to-amber-600","A":"from-green-400 to-emerald-600","B":"from-blue-400 to-indigo-600",
                   "C":"from-gray-400 to-gray-600","D":"from-orange-400 to-red-500","F":"from-red-400 to-red-700" };
  function gc(g) { for(const [k,v] of Object.entries(grades)) { if(g?.startsWith(k)) return v; } return "from-gray-400 to-gray-600"; }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2"><BarChart3 className="text-soul-400" size={24} /> 小说质量评估</h2>
        <p className="text-gray-500 text-sm mt-1">多维度评价作品质量，自动识别改进方向</p>
      </div>
      <div className="grid md:grid-cols-2 gap-6">
        <div className="card">
          <div className="card-header"><FileText size={18} className="text-soul-400" /> 输入文本</div>
          <textarea className="input-field w-full h-64 resize-none font-serif" value={text} onChange={e=>setText(e.target.value)} placeholder="粘贴需要评估的小说内容..." />
          <button onClick={evaluate} disabled={loading||!text.trim()} className="btn-primary mt-3 w-full flex items-center justify-center gap-2">
            {loading ? "评估中..." : <><Sparkles size={16} /> 开始评估</>}
          </button>
        </div>
        <div className="space-y-4">
          {result ? (<>
            <div className="card text-center">
              <div className={`text-5xl font-bold mb-2 bg-gradient-to-r ${gc(result.grade)} bg-clip-text text-transparent`}>{result.grade?.split(" - ")[0]||"?"}</div>
              <div className="text-gray-400 text-sm">{result.grade}</div>
              <div className="text-3xl font-bold text-white mt-2">{result.overall_score}</div>
              <div className="text-gray-500 text-xs mt-1">综合评分</div>
              <p className="text-gray-400 text-sm mt-3">{result.summary}</p>
            </div>
            <div className="card">
              <div className="card-header"><BarChart3 size={16} className="text-soul-400" /> 各维度评分</div>
              <div className="space-y-3">
                {Object.entries(result.criteria||{}).map(([k,c]) => (
                  <div key={k}>
                    <div className="flex justify-between text-sm mb-1"><span className="text-gray-300">{c.name}</span><span className="text-soul-400 font-medium">{c.score}</span></div>
                    <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-soul-600 to-purple-500 rounded-full transition-all" style={{width:c.score+"%"}} />
                    </div>
                    {c.details && <div className="text-xs text-gray-500 mt-0.5">{c.details}</div>}
                    {c.suggestions?.length > 0 && (
                      <div className="text-xs text-amber-400 mt-0.5">{c.suggestions.slice(0,2).map((s,i)=><div key={i}>- {s}</div>)}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </>) : (
            <div className="card h-full flex items-center justify-center">
              <div className="text-center"><Award size={48} className="mx-auto text-gray-700 mb-3" /><p className="text-gray-500">输入文本并点击评估</p></div>
            </div>
          )}
        </div>
      </div>
      {standards?.dimensions && (
        <div className="card">
          <div className="card-header"><CheckCircle size={18} className="text-green-400" /> 评价标准</div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {standards.dimensions.map((d,i) => (
              <div key={i} className="bg-gray-800/40 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1"><span className="text-sm font-medium text-white">{d.name}</span><span className="tag-blue">{d.weight}</span></div>
                <div className="text-xs text-gray-500">{d.desc}</div>
              </div>
            ))}
          </div>
          <div className="mt-3 text-xs text-gray-600">目标等级：{standards.target} · 自优化：{standards.auto_optimize}</div>
        </div>
      )}
    </div>
  );
}
