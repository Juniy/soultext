import React, { useState, useEffect } from "react";
import { Settings, Server, Database, BookOpen, CheckCircle, XCircle, Key, Save } from "lucide-react";

export default function SettingsPage() {
  const [status, setStatus] = useState(null);
  const [llmSettings, setLlmSettings] = useState({ provider: "openai", api_key: "", base_url: "", model: "" });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [testing, setTesting] = useState(false);

  useEffect(() => { loadStatus(); loadLlmSettings(); }, []);
  async function loadStatus() {
    try { const r = await fetch("/api/system/status"); setStatus(await r.json()); } catch (e) { }
  }
  async function loadLlmSettings() {
    try {
      const r = await fetch("/api/llm/settings");
      if (r.ok) {
        const d = await r.json();
        setLlmSettings({ provider: d.provider || "openai", api_key: d.has_api_key ? "****" : "", base_url: d.base_url || "", model: d.model || "" });
      }
    } catch (e) { }
  }
  async function saveLlmSettings() {
    setSaving(true);
    try {
      const body = { provider: llmSettings.provider };
      if (llmSettings.api_key && llmSettings.api_key !== "****") body.api_key = llmSettings.api_key;
      if (llmSettings.base_url) body.base_url = llmSettings.base_url;
      if (llmSettings.model) body.model = llmSettings.model;
      const r = await fetch("/api/llm/settings", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      if (r.ok) { setSaved(true); setTimeout(() => setSaved(false), 3000); loadStatus(); }
    } catch (e) { } finally { setSaving(false); }
  }
  async function testConnection() {
    setTesting(true);
    setTestResult(null);
    try {
      const r = await fetch("/api/llm/test", { method: "POST" });
      const d = await r.json();
      setTestResult(d);
    } catch (e) {
      setTestResult({ success: false, message: "连接测试失败: " + e.message });
    } finally { setTesting(false); }
  }

  const modules = [
    { label: "图数据库", key: "graph_store", desc: "人物/场景/时间轴关系存储" },
    { label: "知识库", key: "knowledge_base", desc: "写作技巧与规则引擎" },
    { label: "生成引擎", key: "generator", desc: "AI 小说生成流水线" },
    { label: "评估系统", key: "evaluator", desc: "自动质量评分与优化" },
    { label: "LLM 状态", key: "llm", desc: "语言模型连接", getValue: (s) => s.llm?.has_api_key ? "已配置" : "未配置" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2"><Settings className="text-soul-400" size={24} /> 系统设置</h2>
      </div>

      {/* LLM API 配置 */}
      <div className="card">
        <div className="card-header"><Key size={18} className="text-soul-400" /> LLM API 配置</div>
        <p className="text-xs text-gray-500 mb-4">配置 AI 语言模型，支持 OpenAI、DeepSeek、Anthropic 等 API 服务</p>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-gray-500 mb-1">服务提供商</label>
            <select className="select-field w-full" value={llmSettings.provider}
              onChange={e => {
                const p = e.target.value;
                const urls = {
                  openai: "https://api.openai.com/v1",
                  deepseek: "https://api.deepseek.com/v1",
                  anthropic: "https://api.anthropic.com/v1",
                  ollama: "http://localhost:11434/v1"
                };
                const models = {
                  openai: "gpt-4o",
                  deepseek: "deepseek-chat",
                  anthropic: "claude-3-5-sonnet-20241022",
                  ollama: "qwen2.5"
                };
                setLlmSettings({ ...llmSettings, provider: p, base_url: urls[p] || llmSettings.base_url, model: models[p] || llmSettings.model });
              }}>
              <option value="openai">OpenAI</option>
              <option value="deepseek">DeepSeek</option>
              <option value="anthropic">Anthropic</option>
              <option value="ollama">Ollama 本地部署</option>
              <option value="custom">自定义</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">模型名称</label>
            <input className="input-field w-full" value={llmSettings.model} onChange={e => setLlmSettings({ ...llmSettings, model: e.target.value })} placeholder="gpt-4o" />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">API 地址</label>
            <input className="input-field w-full" value={llmSettings.base_url} onChange={e => setLlmSettings({ ...llmSettings, base_url: e.target.value })} placeholder="https://api.openai.com/v1" />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">API Key</label>
            <input className="input-field w-full" type="password" value={llmSettings.api_key} onChange={e => setLlmSettings({ ...llmSettings, api_key: e.target.value })} placeholder="sk-..." />
          </div>
        </div>
        <div className="flex gap-3 mt-4">
          <button onClick={saveLlmSettings} disabled={saving} className="btn-primary flex items-center gap-2">
            <Save size={16} /> {saving ? "保存中..." : saved ? "已保存 ✓" : "保存设置"}
          </button>
          <button onClick={testConnection} disabled={testing} className="btn-secondary flex items-center gap-2">
            {testing ? "测试中..." : "测试连接"}
          </button>
        </div>
        {testResult && (
          <div className={`mt-3 p-3 rounded-lg text-sm ${testResult.success ? 'bg-green-900/40 text-green-300' : 'bg-red-900/40 text-red-300'}`}>
            {testResult.success ? "✓ 连接成功: " + testResult.message : "✗ " + testResult.message}
          </div>
        )}
      </div>

      {/* 系统状态 */}
      <div className="card">
        <div className="card-header"><Server size={18} className="text-soul-400" /> 系统状态</div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {modules.map(m => (
            <div key={m.key} className="bg-gray-800/40 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-white">{m.label}</span>
                {status ? (
                  m.getValue ? (
                    <span className={`text-xs ${status.llm?.has_api_key ? "text-green-400" : "text-amber-400"}`}>{m.getValue(status)}</span>
                  ) : status[m.key] ? <CheckCircle size={18} className="text-green-500" /> : <XCircle size={18} className="text-red-500" />
                ) : <div className="w-4 h-4 rounded-full border-2 border-gray-600 border-t-transparent animate-spin" />}
              </div>
              <div className="text-xs text-gray-500">{m.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* 数据统计 */}
      {status && (
        <div className="card">
          <div className="card-header"><Database size={18} className="text-soul-400" /> 数据统计</div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: "小说", value: status.novels },
              { label: "节点", value: status.nodes },
              { label: "关系", value: status.edges },
              { label: "版本", value: "v0.1.0" }
            ].map((s, i) => (
              <div key={i} className="text-center p-4 bg-gray-800/40 rounded-lg">
                <div className="text-2xl font-bold text-soul-400">{s.value}</div>
                <div className="text-xs text-gray-500 mt-1">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 项目信息 */}
      <div className="card">
        <div className="card-header"><BookOpen size={18} className="text-amber-400" /> 项目信息</div>
        <div className="grid sm:grid-cols-2 gap-4 text-sm">
          {[
            { l: "名称", v: "Soultext" },
            { l: "版本", v: "0.1.0" },
            { l: "定位", v: "直击灵魂的 AI 小说创作引擎" },
            { l: "容量", v: "500 万字+" },
            { l: "系统模块", v: "8 大核心引擎" },
            { l: "技术栈", v: "FastAPI + React + NetworkX" },
            { l: "LLM 提供商", v: status?.llm?.provider || "未配置" },
            { l: "当前模型", v: status?.llm?.model || "-" }
          ].map((item, i) => (
            <div key={i} className="flex justify-between border-b border-gray-800 pb-2">
              <span className="text-gray-500">{item.l}</span>
              <span className="text-white">{item.v}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
