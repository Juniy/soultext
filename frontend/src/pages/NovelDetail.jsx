import React, { useState, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { BookOpen, Users, Clock, Sparkles, FileText, Layers, Award, GitBranch, ChevronDown, ChevronUp, ExternalLink, Eye, Download, Archive, AlertTriangle } from "lucide-react";
import GraphView from "../components/GraphView";

export default function NovelDetail() {
  const { id } = useParams();
  const [novel, setNovel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [settings, setSettings] = useState({ writing_style: "", pov: "第三人称", tone: "", pace: "适中", custom_instructions: "" });
  const [graphData, setGraphData] = useState(null);
  const [consistencyIssues, setConsistencyIssues] = useState([]);
  const [evalResult, setEvalResult] = useState(null);
  const [exportMsg, setExportMsg] = useState("");
  const [foreshadowClues, setForeshadowClues] = useState([]);

  useEffect(() => { loadNovel(); }, [id]);
  async function loadNovel() {
    try { const r = await fetch("/api/novels/" + id); setNovel(await r.json()); } catch (e) {} finally { setLoading(false); }
  }
  async function loadGraphData() {
    try {
      const [chars, events, scenes] = await Promise.all([
        fetch("/api/graph/query?novel_id=" + encodeURIComponent(id) + "&node_type=character").then(r => r.json()),
        fetch("/api/graph/query?novel_id=" + encodeURIComponent(id) + "&node_type=timeline").then(r => r.json()),
        fetch("/api/graph/query?novel_id=" + encodeURIComponent(id) + "&node_type=scene").then(r => r.json()),
      ]);
      setGraphData({ characters: chars, timeline: events, scenes: scenes });
    } catch (e) {}
  }
  async function loadConsistency() {
    try { const r = await fetch("/api/graph/consistency?novel_id=" + encodeURIComponent(id)); const d = await r.json(); setConsistencyIssues(d.issues || []); } catch (e) {}
  }
  async function exportNovelTxt() { await doExport("txt"); }
  async function exportNovelEpub() { await doExport("epub"); }
  async function doExport(fmt) {
    try {
      const r = await fetch("/api/novels/" + id + "/export?fmt=" + fmt, { method: "POST" });
      const d = await r.json();
      if (d.message) setExportMsg(fmt.toUpperCase() + " 导出成功: " + d.filename);
    } catch(e) { setExportMsg("导出失败: " + e.message); }
    setTimeout(() => setExportMsg(""), 5000);
  }
  async function loadForeshadowClues() {
    try { const r = await fetch("/api/novels/" + id + "/foreshadowing"); const d = await r.json(); setForeshadowClues(d.clues || []); } catch(e) {}
  }
  async function genOutline() {
    try { await fetch("/api/novels/" + id + "/generate/outline", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(settings) }); loadNovel(); } catch (e) {}
  }
  async function genChapter() {
    const num = (novel?.chapters?.length || 0) + 1;
    try {
      await fetch("/api/novels/" + id + "/generate/chapter", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ novel_id: id, chapter_number: num, outline: novel?.outline, settings }),
      });
      loadNovel();
    } catch (e) {}
  }
  async function evalLatest() {
    try {
      const n = await (await fetch("/api/novels/" + id)).json();
      const lc = n.chapters?.[n.chapters.length - 1];
      if (lc) {
        const r = await fetch("/api/evaluate", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: lc.content || "" }) });
        setEvalResult(await r.json());
      }
    } catch (e) {}
  }

  useEffect(() => { if (novel) { loadGraphData(); loadConsistency(); loadForeshadowClues(); } }, [novel?.id]);

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-pulse text-gray-500">加载中...</div></div>;
  if (!novel) return <div className="text-center py-12 text-gray-500">找不到小说</div>;

  const p = novel.word_count_target > 0 ? Math.min(100, Math.round((novel.word_count_current / novel.word_count_target) * 100)) : 0;
  const tabs = [
    { id: "overview", label: "概览", icon: BookOpen },
    { id: "chapters", label: "章节", icon: FileText },
    { id: "characters", label: "人物", icon: Users },
    { id: "timeline", label: "时间轴", icon: Clock },
    { id: "world", label: "世界观", icon: Layers },
    { id: "graph", label: "关系图", icon: GitBranch },
    { id: "foreshadowing", label: "伏笔管理", icon: Eye },
  ];

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-soul-600 to-purple-600 rounded-xl flex items-center justify-center text-white text-xl font-bold">{novel.title?.charAt(0) || "?"}</div>
            <div>
              <h2 className="text-xl font-bold text-white">{novel.title}</h2>
              <p className="text-gray-500 text-sm mt-1"><span className="tag-blue">{novel.genre}</span><span className="ml-2 text-gray-500">{novel.chapters?.length || 0}? ? {(novel.word_count_current || 0).toLocaleString()}?</span></p>
              {novel.description && <p className="text-gray-400 text-sm mt-2">{novel.description}</p>}
            </div>
          </div>
        </div>
        <div className="mt-4">
          <div className="flex justify-between text-xs text-gray-500 mb-1"><span>进度</span><span>目标: 500万字</span></div>
          <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-soul-600 to-purple-500 rounded-full transition-all duration-500" style={{ width: p + "%" }} />
          </div>
          <div className="text-right text-xs text-soul-400 mt-1">{p}%</div>
        </div>
      </div>

      <div className="flex overflow-x-auto gap-1 bg-gray-900/80 rounded-lg p-1 border border-gray-800">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm whitespace-nowrap transition-all ${activeTab === t.id ? "bg-soul-600/20 text-soul-300 border border-soul-600/30" : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/50"}`}>
            <t.icon size={16} /> {t.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === "overview" && (
        <div className="grid md:grid-cols-3 gap-4">
          <div className="md:col-span-2 space-y-4">
            <div className="card">
              <div className="card-header"><Sparkles size={18} className="text-soul-400" /> AI 生成设置</div>
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">写作风格</label>
                    <select className="select-field w-full" value={settings.writing_style} onChange={e => setSettings({ ...settings, writing_style: e.target.value })}>
                      <option value="">??</option><option value="简明">简明拢要</option><option value="华丽">华丽辞藻</option><option value="简明">简明拢要</option><option value="华丽">华丽辞藻</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">写作风格</label>
                    <select className="select-field w-full" value={settings.pov} onChange={e => setSettings({ ...settings, pov: e.target.value })}>
                      <option value="简明">简明拢要</option><option value="华丽">华丽辞藻</option><option value="全知视角">全知视角</option>
                    </select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">写作风格</label>
                    <select className="select-field w-full" value={settings.tone} onChange={e => setSettings({ ...settings, tone: e.target.value })}>
                      <option value="">??</option><option value="简明">简明拢要</option><option value="华丽">华丽辞藻</option><option value="朴素">朴素平实</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">写作风格</label>
                    <select className="select-field w-full" value={settings.pace} onChange={e => setSettings({ ...settings, pace: e.target.value })}>
                      <option value="舒缓">舒缓细腻的叙事</option><option value="紧凑">紧凑明快的叙事</option><option value="张弛">张弛有度的叙事</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">自定义指令</label>
                  <textarea className="input-field w-full h-16 resize-none" value={settings.custom_instructions} onChange={e => setSettings({ ...settings, custom_instructions: e.target.value })} placeholder="输入备注..." />
                </div>
                <div className="flex gap-3">
                  <button onClick={genOutline} className="btn-primary flex items-center gap-2"><Sparkles size={16} /> 生成大纲</button>
                  <button onClick={genChapter} className="btn-secondary flex items-center gap-2" disabled={!novel.outline}><FileText size={16} /> 生成下一章</button>
                </div>
              </div>
            </div>
            {novel.outline && (
              <div className="card">
                <div className="card-header"><BookOpen size={18} className="text-green-400" /> 故事大纲</div>
                <div className="text-sm text-gray-400 whitespace-pre-wrap font-serif leading-relaxed">
                  {typeof novel.outline === "string" ? novel.outline : novel.outline?.content || JSON.stringify(novel.outline, null, 2)}
                </div>
              </div>
            )}
          </div>
          <div className="space-y-4">
            <div className="card">
              <div className="card-header"><Award size={18} className="text-amber-400" /> 小说评估</div>
              <button onClick={evalLatest} className="btn-secondary w-full text-sm">同步评估</button>
              {evalResult && (
                <div className="mt-3 space-y-2">
                  <div className="text-center"><span className="text-2xl font-bold text-soul-400">{evalResult.overall_score}</span><span className="text-gray-500 text-sm ml-1">?</span></div>
                  <div className="text-center text-sm text-gray-400">{evalResult.grade}</div>
                  <div className="text-xs text-gray-500">{evalResult.summary}</div>
                </div>
              )}
            </div>
                        <div className="card">
              <div className="card-header"><Download size={18} className="text-green-400" /> 故事大纲</div>
              <div className="space-y-2">
                <button onClick={exportNovelTxt} className="btn-secondary w-full text-sm flex items-center justify-center gap-2"><Download size={14} /> 导出 TXT</button>
                <button onClick={exportNovelEpub} className="btn-secondary w-full text-sm flex items-center justify-center gap-2"><Archive size={14} /> 导出 EPUB</button>
                {exportMsg && <div className="text-xs text-green-400 text-center">{exportMsg}</div>}
              </div>
            </div>
            {consistencyIssues.length > 0 && (
              <div className="card">
                <div className="card-header"><Award size={18} className="text-amber-400" /> 一致性问题</div>
                <div className="space-y-2 text-sm">
                  {consistencyIssues.slice(0, 5).map((issue, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs">
                      <span className={`px-1.5 py-0.5 rounded ${issue.severity === "warning" ? "bg-amber-600/20 text-amber-400" : "bg-blue-600/20 text-blue-400"}`}>{issue.severity}</span>
                      <span className="text-gray-400">{issue.message}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {novel.graph_stats && (
              <div className="card">
                <div className="card-header"><GitBranch size={18} className="text-purple-400" /> 图数据统计</div>
                <div className="space-y-2 text-sm">
                  {Object.entries(novel.graph_stats.node_types || {}).map(([k, v]) => v > 0 && <div key={k} className="flex justify-between"><span className="text-gray-500">{k}</span><span className="text-white">{v}</span></div>)}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Chapters Tab */}
      {activeTab === "chapters" && (
        <ChapterView chapters={novel.chapters || []} id={id} settings={settings} onRefresh={loadNovel} />
      )}

      {/* Characters Tab */}
      {activeTab === "characters" && (
        <CharacterView chars={novel.character_network} />
      )}

      {/* Timeline Tab */}
      {activeTab === "timeline" && (
        <TimelineView events={graphData?.timeline?.events || novel.timeline || []} />
      )}

      {/* World Tab */}
      {activeTab === "world" && (
        <WorldView scenes={graphData?.scenes?.scenes || []} />
      )}

      {/* Graph Tab */}
      {activeTab === "graph" && (
        <GraphTabView novelId={id} graphData={graphData} />
      )}

      {/* Foreshadowing Tab */}
      {activeTab === "foreshadowing" && (
        <ForeshadowingView novelId={id} clues={foreshadowClues} onRefresh={loadForeshadowClues} currentChapter={novel?.chapters?.length || 0} />
      )}
    </div>
  );
}

/* ====== Chapter View ====== */
function ChapterView({ chapters, id, settings, onRefresh }) {
  const [expanded, setExpanded] = useState(null);
  const [genFeedback, setGenFeedback] = useState("");
  const [generating, setGenerating] = useState(false);

  async function handleGenChapter() {
    setGenerating(true);
    const num = chapters.length + 1;
    try {
      await fetch("/api/novels/" + id + "/generate/chapter", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ novel_id: id, chapter_number: num, settings }),
      });
      onRefresh();
    } catch (e) { } finally { setGenerating(false); }
  }

  async function handleRevise() {
    if (!genFeedback.trim() || !chapters.length) return;
    const last = chapters[chapters.length - 1];
    try {
      await fetch("/api/novels/" + id + "/generate/revise", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ feedback: genFeedback, text: last.content, settings }),
      });
      setGenFeedback("");
    } catch (e) { }
  }

  return (
    <div className="card">
      <div className="card-header flex items-center justify-between">
        <span className="flex items-center gap-2"><FileText size={18} className="text-soul-400" /> 章节列表 ({chapters.length})</span>
        <div className="flex gap-2">
          <button onClick={handleGenChapter} disabled={generating} className="btn-primary text-xs px-3 py-1.5">
            {generating ? "???..." : "?????"}
          </button>
        </div>
      </div>
      {chapters.length === 0 ? (
        <div className="text-center py-8 text-gray-500">还没有生成任何章节</div>
      ) : (
        <div className="space-y-2">
          {chapters.map((ch, i) => (
            <div key={i} className="bg-gray-800/40 rounded-lg overflow-hidden">
              <button onClick={() => setExpanded(expanded === i ? null : i)}
                className="w-full flex items-center justify-between p-3 hover:bg-gray-800/60 transition-colors">
                <div className="flex items-center gap-3">
                  <span className="w-7 h-7 rounded-full bg-soul-600/20 text-soul-400 text-xs flex items-center justify-center font-medium">{ch.chapter_number || i + 1}</span>
                  <span className="text-sm text-gray-200">{ch.title || `第${ch.chapter_number || i + 1}章`}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-500">{ch.word_count || 0}?</span>
                  {expanded === i ? <ChevronUp size={14} className="text-gray-500" /> : <ChevronDown size={14} className="text-gray-500" />}
                </div>
              </button>
              {expanded === i && (
                <div className="px-3 pb-3">
                  <div className="text-sm text-gray-400 whitespace-pre-wrap font-serif leading-relaxed max-h-96 overflow-y-auto border-t border-gray-700 pt-3">
                    {ch.content || "暂无内容"}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
      {chapters.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-800">
          <label className="block text-xs text-gray-500 mb-2">输入修改反馈</label>
          <div className="flex gap-2">
            <textarea className="input-field flex-1 h-16 resize-none text-sm" value={genFeedback} onChange={e => setGenFeedback(e.target.value)} placeholder="输入反馈意见..." />
            <button onClick={handleRevise} disabled={!genFeedback.trim()} className="btn-secondary text-xs px-3 self-end">修订</button>
          </div>
        </div>
      )}
    </div>
  );
}

/* ====== Character View ====== */
function CharacterView({ chars }) {
  const characterList = chars?.characters ? Object.values(chars.characters) : [];
  const relationships = chars?.relationships || [];

  if (!characterList.length) return (
    <div className="card">
      <div className="card-header"><Users size={18} className="text-soul-400" /> 人物</div>
      <div className="text-center py-8 text-gray-500">还没有时间轴数据，生成章节后自动创建</div>
    </div>
  );

  return (
    <div className="grid md:grid-cols-2 gap-4">
      <div className="card">
        <div className="card-header"><Users size={18} className="text-soul-400" /> 角色 ({characterList.length})</div>
        <div className="grid gap-3">
          {characterList.map((ch, i) => (
            <div key={ch.id || i} className="bg-gray-800/40 rounded-lg p-3">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-8 h-8 rounded-full bg-soul-600/30 flex items-center justify-center text-soul-400 text-sm font-bold">{ch.name?.charAt(0) || "?"}</div>
                <div>
                  <div className="text-sm font-medium text-white">{ch.name || ch.id}</div>
                  <div className="text-xs text-gray-500">{ch.node_type || "character"} ? {ch.gender || ""} {ch.age || ""}</div>
                </div>
              </div>
              {(ch.personality || ch.tags) && (
                <div className="flex flex-wrap gap-1 mb-2">
                  {(ch.personality || ch.tags || []).slice(0, 5).map((t, j) => (
                    <span key={j} className="text-xs bg-soul-600/10 text-soul-400 px-1.5 py-0.5 rounded">{t}</span>
                  ))}
                </div>
              )}
              {ch.background && <p className="text-xs text-gray-500 line-clamp-2">{ch.background}</p>}
              {ch.motivation && <p className="text-xs text-gray-600 mt-1">动机: {ch.motivation}</p>}
            </div>
          ))}
        </div>
      </div>
      {relationships.length > 0 && (
        <div className="card">
          <div className="card-header"><GitBranch size={18} className="text-purple-400" /> 关系图谱 ({relationships.length})</div>
          <div className="space-y-2">
            {relationships.map((r, i) => (
              <div key={i} className="flex items-center gap-2 text-sm bg-gray-800/30 rounded-lg p-2">
                <span className="text-white font-medium">{r.source}</span>
                <span className="text-xs tag-gray">{r.type}</span>
                <span className="text-white font-medium">{r.target}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/* ====== Timeline View ====== */
function TimelineView({ events }) {
  if (!events || events.length === 0) return (
    <div className="card">
      <div className="card-header"><Clock size={18} className="text-soul-400" /> 时间轴</div>
      <div className="text-center py-8 text-gray-500">还没有时间轴数据，生成章节后自动创建</div>
    </div>
  );

  return (
    <div className="card">
      <div className="card-header"><Clock size={18} className="text-soul-400" /> 时间轴 ({events.length})</div>
      <div className="relative">
        <div className="absolute left-4 top-0 bottom-0 w-px bg-soul-600/30" />
        <div className="space-y-4 pl-10">
          {events.map((ev, i) => (
            <div key={i} className="relative">
              <div className="absolute -left-6 top-1 w-3 h-3 rounded-full bg-soul-600 border-2 border-gray-900" />
              <div className="bg-gray-800/40 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs text-soul-400">{ev.timestamp || ev.time || `事件 ${i + 1}`}</span>
                  <span className="text-xs tag-gray">{ev.node_type || "event"}</span>
                </div>
                <div className="text-sm text-white font-medium">{ev.name || ev.title || ev.id}</div>
                {ev.description && <p className="text-xs text-gray-500 mt-1">{ev.description}</p>}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ====== World View ====== */
function WorldView({ scenes }) {
  if (!scenes || scenes.length === 0) return (
    <div className="card">
      <div className="card-header"><Layers size={18} className="text-soul-400" /> 场景/世界观</div>
      <div className="text-center py-8 text-gray-500">还没有场景数据</div>
    </div>
  );

  return (
    <div className="grid md:grid-cols-2 gap-4">
      <div className="card">
        <div className="card-header"><Layers size={18} className="text-soul-400" /> 场景列表 ({scenes.length})</div>
        <div className="space-y-2">
          {scenes.map((s, i) => (
            <div key={i} className="bg-gray-800/40 rounded-lg p-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-white font-medium">{s.title || s.name || s.id}</span>
                <span className="text-xs text-gray-500">?? {i + 1}</span>
              </div>
              {s.summary && <p className="text-xs text-gray-500">{s.summary}</p>}
              {s.location_id && <p className="text-xs text-gray-600 mt-1">??: {s.location_id}</p>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ====== Graph View Tab ====== */
function GraphTabView({ novelId, graphData }) {
  const [allNodes, setAllNodes] = useState({});
  const [allEdges, setAllEdges] = useState([]);

  useEffect(() => {
    async function loadGraph() {
      try {
        const r = await fetch("/api/graph/query?novel_id=" + encodeURIComponent(novelId));
        const stats = await r.json();
        if (stats.total_nodes > 0) {
          const chars = await fetch("/api/graph/query?novel_id=" + encodeURIComponent(novelId) + "&node_type=character").then(r => r.json());
          if (chars.characters) {
            const nodes = { ...chars.characters };
            const edges = (chars.relationships || []).map(r => ({ source: r.source, target: r.target, type: r.type || "related" }));
            setAllNodes(nodes);
            setAllEdges(edges);
          }
        }
      } catch (e) { }
    }
    loadGraph();
  }, [novelId]);

  return (
    <div className="card">
      <div className="card-header"><GitBranch size={18} className="text-soul-400" /> 关系图谱</div>
      {Object.keys(allNodes).length > 0 ? (
        <GraphView nodes={allNodes} edges={allEdges} width={800} height={500} />
      ) : (
        <div className="text-center py-8 text-gray-500">
          还没有时间轴数据，生成章节后自动创建</div>
      )}
    </div>
  );
}


/* ====== Foreshadowing View ====== */
function ForeshadowingView({ novelId, clues, onRefresh, currentChapter }) {
  const [newClue, setNewClue] = useState({ description: "", clue_type: "general", importance: 3, planted_chapter: currentChapter, expected_recall_chapter: currentChapter + 10, related_entities: "", keywords: "", notes: "" });
  const [showAdd, setShowAdd] = useState(false);
  const [expandedClue, setExpandedClue] = useState(null);
  const [filterStatus, setFilterStatus] = useState("all");

  async function addClue() {
    try {
      const body = {
        description: newClue.description,
        clue_type: newClue.clue_type,
        importance: parseInt(newClue.importance),
        planted_chapter: parseInt(newClue.planted_chapter),
        expected_recall_chapter: parseInt(newClue.expected_recall_chapter),
        related_entities: newClue.related_entities.split(",").map(s => s.trim()).filter(Boolean),
        keywords: newClue.keywords.split(",").map(s => s.trim()).filter(Boolean),
        notes: newClue.notes,
      };
      await fetch("/api/novels/" + novelId + "/foreshadowing", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      setShowAdd(false);
      setNewClue({ description: "", clue_type: "general", importance: 3, planted_chapter: currentChapter, expected_recall_chapter: currentChapter + 10, related_entities: "", keywords: "", notes: "" });
      onRefresh();
    } catch (e) {}
  }

  async function fulfillClue(clueId) {
    try {
      await fetch("/api/novels/" + novelId + "/foreshadowing/" + clueId + "/fulfill", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ chapter: currentChapter }) });
      onRefresh();
    } catch (e) {}
  }

  async function deleteClue(clueId) {
    if (!confirm("确定要删除该伏笔吗？")) return;
    try {
      await fetch("/api/novels/" + novelId + "/foreshadowing/" + clueId, { method: "DELETE" });
      onRefresh();
    } catch (e) {}
  }

  const filteredClues = filterStatus === "all" ? clues : clues.filter(c => c.status === filterStatus);

  return (
    <div className="grid md:grid-cols-3 gap-4">
      <div className="md:col-span-2 space-y-4">
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <span className="flex items-center gap-2"><Eye size={18} className="text-soul-400" /> 伏笔管理 ({clues.length})</span>
            <button onClick={() => setShowAdd(!showAdd)} className="btn-primary text-xs px-3 py-1.5">{showAdd ? "取消" : "+ 添加伏笔"}</button>
          </div>
          {showAdd && (
            <div className="bg-gray-800/40 rounded-lg p-4 mb-4 space-y-3">
              <div>
                <label className="block text-xs text-gray-500 mb-1">伏笔描述 *</label>
                <textarea className="input-field w-full h-16 resize-none" value={newClue.description} onChange={e => setNewClue({...newClue, description: e.target.value})} placeholder="描述伏笔的具体内容..." />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">类型</label>
                  <select className="select-field w-full" value={newClue.clue_type} onChange={e => setNewClue({...newClue, clue_type: e.target.value})}>
                    <option value="general">??</option>
                    <option value="character">人物</option>
                    <option value="object">物品</option>
                    <option value="event">事件</option>
                    <option value="prophecy">预言</option>
                    <option value="dialogue">对话</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">重要程度</label>
                  <select className="select-field w-full" value={newClue.importance} onChange={e => setNewClue({...newClue, importance: parseInt(e.target.value)})}>
                    <option value={5}>朴素平实</option>
                    <option value={4}>朴素平实</option>
                    <option value={3}>朴素平实</option>
                    <option value={2}>朴素平实</option>
                    <option value={1}>朴素平实</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">埋设章节</label>
                  <input className="input-field w-full" type="number" value={newClue.planted_chapter} onChange={e => setNewClue({...newClue, planted_chapter: parseInt(e.target.value)})} />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">预期回收章节</label>
                  <input className="input-field w-full" type="number" value={newClue.expected_recall_chapter} onChange={e => setNewClue({...newClue, expected_recall_chapter: parseInt(e.target.value)})} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">关联实体 (用逗号分隔)</label>
                  <input className="input-field w-full" value={newClue.related_entities} onChange={e => setNewClue({...newClue, related_entities: e.target.value})} placeholder="张三,李四" />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">关键词 (用逗号分隔)</label>
                  <input className="input-field w-full" value={newClue.keywords} onChange={e => setNewClue({...newClue, keywords: e.target.value})} placeholder="剑,江湖,恩怨" />
                </div>
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">??</label>
                <textarea className="input-field w-full h-12 resize-none" value={newClue.notes} onChange={e => setNewClue({...newClue, notes: e.target.value})} placeholder="输入备注..." />
              </div>
              <button onClick={addClue} disabled={!newClue.description.trim()} className="btn-primary w-full">添加伏笔</button>
            </div>
          )}
          <div className="flex gap-2 mb-3">
            {["all", "planted", "active", "fulfilled"].map(s => (
              <button key={s} onClick={() => setFilterStatus(s)}
                className={`text-xs px-2.5 py-1 rounded transition-colors ${filterStatus === s ? "bg-soul-600/20 text-soul-400" : "bg-gray-800 text-gray-500 hover:text-gray-300"}`}>
                {s === "all" ? "全部" : s === "planted" ? "已埋设" : s === "active" ? "激活中" : "已回攸"}
              </button>
            ))}
          </div>
          {filteredClues.length === 0 ? (
            <div className="text-center py-6 text-gray-500">暂无伏笔</div>
          ) : (
            <div className="space-y-2">
              {filteredClues.map((clue, i) => (
                <div key={clue.id || i} className="bg-gray-800/40 rounded-lg overflow-hidden">
                  <button onClick={() => setExpandedClue(expandedClue === clue.id ? null : clue.id)}
                    className="w-full flex items-center justify-between p-3 hover:bg-gray-800/60 transition-colors">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className={`w-2 h-2 rounded-full shrink-0 ${clue.status === "fulfilled" ? "bg-green-500" : clue.status === "active" ? "bg-yellow-500" : clue.importance >= 4 ? "bg-red-500" : "bg-blue-500"}`} />
                      <span className={"text-sm " + (clue.status === "fulfilled" ? "text-gray-500 line-through" : "text-gray-200")}>{clue.description?.substring(0, 60)}{(clue.description?.length || 0) > 60 ? "..." : ""}</span>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <span className={"text-xs px-1.5 py-0.5 rounded " + (clue.importance >= 4 ? "bg-red-600/20 text-red-400" : clue.importance >= 3 ? "bg-amber-600/20 text-amber-400" : "bg-gray-700 text-gray-500")}>{'*'.repeat(clue.importance)}</span>
                      <span className={"text-xs " + (clue.status === "fulfilled" ? "text-green-500" : clue.status === "active" ? "text-yellow-500" : "text-blue-400")}>{clue.status}</span>
                    </div>
                  </button>
                  {expandedClue === clue.id && (
                    <div className="px-3 pb-3 text-xs text-gray-400 border-t border-gray-700 pt-3 space-y-1">
                      <p><span className="text-gray-500">??:</span> {clue.description}</p>
                      <p><span className="text-gray-500">??:</span> {clue.clue_type} <span className="text-gray-500">| ???:</span> {clue.planted_chapter} <span className="text-gray-500">| ????:</span> {clue.expected_recall_chapter || "???"}</p>
                      {clue.actual_recall_chapter > 0 && <p><span className="text-gray-500">实际回收章节:</span> {clue.actual_recall_chapter}</p>}
                      {clue.related_entities?.length > 0 && <p><span className="text-gray-500">????:</span> {clue.related_entities.join(", ")}</p>}
                      {clue.keywords?.length > 0 && <p><span className="text-gray-500">???:</span> <span className="flex flex-wrap gap-1 mt-1">{clue.keywords.map((kw, j) => <span key={j} className="bg-soul-600/10 text-soul-400 px-1.5 py-0.5 rounded text-xs">{kw}</span>)}</span></p>}
                      {clue.notes && <p><span className="text-gray-500">??:</span> {clue.notes}</p>}
                      <div className="flex gap-2 pt-2">
                        {clue.status !== "fulfilled" && <button onClick={() => fulfillClue(clue.id)} className="btn-primary text-xs px-2 py-1">????</button>}
                        <button onClick={() => deleteClue(clue.id)} className="text-xs px-2 py-1 rounded bg-red-600/20 text-red-400 hover:bg-red-600/30">??</button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      <div className="space-y-4">
        <div className="card">
          <div className="card-header"><Eye size={18} className="text-soul-400" /> 关系图谱</div>
          <div className="space-y-3">
            <div className="text-center p-4 bg-gray-800/40 rounded-lg">
              <div className="text-3xl font-bold text-soul-400">{clues.length}</div>
              <div className="text-xs text-gray-500">总伏笔数</div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="bg-gray-800/40 rounded-lg p-2">
                <div className="text-lg font-bold text-blue-400">{clues.filter(c => c.status === "planted" || c.status === "active").length}</div>
                <div className="text-xs text-gray-500">???</div>
              </div>
              <div className="bg-gray-800/40 rounded-lg p-2">
                <div className="text-lg font-bold text-green-400">{clues.filter(c => c.status === "fulfilled").length}</div>
                <div className="text-xs text-gray-500">???</div>
              </div>
              <div className="bg-gray-800/40 rounded-lg p-2">
                <div className="text-lg font-bold text-amber-400">{clues.length > 0 ? Math.round(clues.filter(c => c.status === "fulfilled").length/clues.length*100) : 0}%</div>
                <div className="text-xs text-gray-500">???</div>
              </div>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-header text-xs text-gray-500">状态图例</div>
          <div className="space-y-1 text-xs text-gray-500">
            <p><span className="w-2 h-2 rounded-full bg-red-500 inline-block mr-1"></span> 重要伏笔 - 待回收</p>
            <p><span className="w-2 h-2 rounded-full bg-blue-500 inline-block mr-1"></span> 普通伏笔 - 已埋设</p>
            <p><span className="w-2 h-2 rounded-full bg-green-500 inline-block mr-1"></span> 已回收 - 已完成</p>
          </div>
        </div>
      </div>
    </div>
  );
}
