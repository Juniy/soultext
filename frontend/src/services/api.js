const API_BASE = "/api";

async function request(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API Error: ${res.status}`);
  return res.json();
}

export const api = {
  listNovels: () => request("/novels"),
  createNovel: (data) => request("/novels", { method: "POST", body: JSON.stringify(data) }),
  getNovel: (id) => request(`/novels/${id}`),
  generateOutline: (id, s) => request(`/novels/${id}/generate/outline`, { method: "POST", body: JSON.stringify(s||{}) }),
  generateChapter: (id, d) => request(`/novels/${id}/generate/chapter`, { method: "POST", body: JSON.stringify(d) }),
  evaluate: (text, ctx) => request("/evaluate", { method: "POST", body: JSON.stringify({text,context:ctx}) }),
  getStandards: () => request("/evaluate/standards"),
  getKnowledgeCategories: () => request("/knowledge/categories"),
  searchKnowledge: (q) => request(`/knowledge/search?q=${encodeURIComponent(q)}`),
  queryGraph: (p) => { const q=new URLSearchParams(p).toString(); return request(`/graph/query?${q}`); },
  checkConsistency: (id) => request(`/graph/consistency?novel_id=${encodeURIComponent(id)}`),
  systemStatus: () => request("/system/status"),
};
