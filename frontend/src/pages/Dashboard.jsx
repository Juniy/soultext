import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, BookOpen, Sparkles, BarChart3, ArrowRight, Target, Library } from "lucide-react";

export default function Dashboard({ status }) {
  const [novels, setNovels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newNovel, setNewNovel] = useState({ title: "", genre: "玄幻", description: "" });
  const navigate = useNavigate();
  const genres = ["玄幻","仙侠","都市","历史","科幻","悬疑","言情","奇幻","武侠"];
  useEffect(() => { loadNovels(); }, []);
  async function loadNovels() {
    try { const r = await fetch("/api/novels"); setNovels(await r.json()); }
    catch(e){} finally { setLoading(false); }
  }
  async function createNovel() {
    try {
      const r = await fetch("/api/novels", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(newNovel) });
      const novel = await r.json();
      setShowCreate(false); setNewNovel({title:"",genre:"玄幻",description:""});
      navigate("/novel/"+novel.id);
    } catch(e) { console.error(e); }
  }
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2"><Sparkles className="text-soul-400" size={24} /> Soultext 创作控制台</h2>
          <p className="text-gray-500 text-sm mt-1">管理你的所有小说项目</p>
        </div>
        <button onClick={()=>setShowCreate(true)} className="btn-primary flex items-center gap-2"><Plus size={16} /> 新建作品</button>
      </div>
      {showCreate && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50" onClick={()=>setShowCreate(false)}>
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 w-full max-w-md mx-4" onClick={e=>e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-white mb-4">创建新作品</h3>
            <div className="space-y-4">
              <input className="input-field w-full" value={newNovel.title} onChange={e=>setNewNovel({...newNovel,title:e.target.value})} placeholder="作品名称" />
              <div className="flex flex-wrap gap-2">
                {genres.map(g => (
                  <button key={g} onClick={()=>setNewNovel({...newNovel,genre:g})}
                    className={`px-3 py-1.5 rounded-lg text-sm transition-all ${newNovel.genre===g ? "bg-soul-600 text-white" : "bg-gray-800 text-gray-400 hover:bg-gray-700"}`}>{g}</button>
                ))}
              </div>
              <textarea className="input-field w-full h-20 resize-none" value={newNovel.description} onChange={e=>setNewNovel({...newNovel,description:e.target.value})} placeholder="一句话灵感..." />
              <div className="flex gap-3 justify-end">
                <button onClick={()=>setShowCreate(false)} className="btn-secondary">取消</button>
                <button onClick={createNovel} className="btn-primary" disabled={!newNovel.title}>创建</button>
              </div>
            </div>
          </div>
        </div>
      )}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label:"作品总数", value:novels.length, icon:BookOpen, color:"text-blue-400" },
          { label:"字数目标", value:"500万+", icon:Target, color:"text-purple-400" },
          { label:"写作技巧", value:status?.nodes||0, icon:Library, color:"text-green-400" },
          { label:"运行状态", value:status?.graph_store?"在线":"离线", icon:BarChart3, color:status?.graph_store?"text-green-400":"text-red-400" },
        ].map((s,i) => (
          <div key={i} className="card flex items-center gap-4">
            <div className={`${s.color} bg-gray-800 rounded-lg p-2.5`}><s.icon size={20} /></div>
            <div><div className="stat-value text-lg">{s.value}</div><div className="stat-label">{s.label}</div></div>
          </div>
        ))}
      </div>
      <div className="card">
        <div className="card-header"><BookOpen size={18} className="text-soul-400" /> 作品列表</div>
        {loading ? <div className="text-center py-8 text-gray-500 animate-pulse">加载中...</div> :
         novels.length === 0 ? (
          <div className="text-center py-12">
            <BookOpen size={48} className="mx-auto text-gray-700 mb-3" />
            <p className="text-gray-500">还没有作品</p>
            <button onClick={()=>setShowCreate(true)} className="btn-primary mt-4"><Plus size={16} className="inline mr-1" /> 创建首部作品</button>
          </div>
        ) : (
          <div className="grid gap-3">
            {novels.map(n => {
              const p = n.word_count_target > 0 ? Math.min(100, Math.round((n.word_count_current/n.word_count_target)*100)) : 0;
              return (
                <div key={n.id} onClick={()=>navigate("/novel/"+n.id)}
                  className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg hover:bg-gray-800 cursor-pointer transition-all group">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-soul-600/20 rounded-lg flex items-center justify-center text-soul-400 font-bold">{n.title.charAt(0)}</div>
                    <div>
                      <div className="font-medium text-white group-hover:text-soul-300 transition-colors">{n.title}</div>
                      <div className="text-xs text-gray-500">{n.genre} · {n.chapters?.length||0} 章 · {(n.word_count_current||0).toLocaleString()} 字</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right"><div className="text-xs text-gray-500">完成度</div><div className="text-sm font-medium text-soul-400">{p}%</div></div>
                    <ArrowRight size={16} className="text-gray-600 group-hover:text-soul-400 transition-colors" />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
