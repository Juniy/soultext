# Soultext - AI 小说创作引擎

> 直击灵魂的长篇小说 AI 创作系统

## 项目愿景

写出直击灵魂、感人至深、引人入胜的长篇小说（500万字以上），通过 AI 辅助实现从灵感到成书的完整创作流程。

## 核心架构

soultext/
  backend/          Python FastAPI 后端
    app.py          主入口
    models/         数据模型
    graph_db/       图数据库层
    evaluator/      质量评价系统
    generator/      生成流水线
    knowledge/      写作技巧知识库
    api/            REST API 路由
  frontend/         React + Vite + Tailwind CSS 前端
  doc/              写作技巧文档库（60+篇）
  research/         行业调研报告

## 核心功能

### 图数据库引擎
基于 NetworkX 的多维关系网络：
- 人物：性格、动机、成长弧线、关系
- 地点：场景、历史、地理位置
- 场景：时间线、参与人物、情绪基调
- 事件：因果链、时间顺序
- 世界观：规则体系
- 一致性检测：自动发现冲突问题

### 质量评价体系
8个维度综合评价：情感共鸣(18%)、人物塑造(17%)、情节设计(15%)、文笔技巧(12%)、世界观(12%)、一致性(10%)、节奏控制(8%)、创新性(8%)
评价等级：S(90+) A(80+) B(70+) C(60+) D(40+) F(<40)

### 写作技巧知识引擎
整合 doc/ 下所有写作技巧，按创作阶段自动注入提示词：
- 大纲阶段：冲突设计、黄金开篇、悬念、伏笔
- 章节阶段：情感共鸣、人物弧光、对话、环境
- 修改阶段：去AI味、润色

### Web UI 控制台
作品管理、创作进度、人物/场景/时间线可视化、实时质量评估、知识库搜索

## 快速开始

### 安装
pip install -r backend/requirements.txt
cd frontend && pnpm install

### 运行
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
cd frontend && npx vite --host 0.0.0.0 --port 5173

访问 http://localhost:5173

## API 端点

GET  /api/system/status              系统状态
POST /api/novels                     创建作品
GET  /api/novels                     作品列表
GET  /api/novels/{id}                作品详情
POST /api/novels/{id}/generate       生成
POST /api/evaluate                   文本评估
GET  /api/evaluate/standards         评价标准
GET  /api/knowledge/categories       技巧分类
GET  /api/knowledge/search?q=        搜索技巧
GET  /api/graph/query                图查询
GET  /api/graph/consistency          一致性检查

## 技术栈

后端：Python 3.12 + FastAPI + NetworkX
前端：React 19 + Vite 6 + Tailwind CSS 3 + Recharts

## 创新点

1. 图数据库驱动的实体关系管理
2. 8维度评价体系 + 自优化迭代
3. 写作技巧系统化知识引擎
4. 长篇小说原生支持（500万字+）
5. 质量闭环：评估-分析-优化-再评估

## 调研参考

详见 research/github_top_projects.md

参考了以下项目：AI-Novel-Writing-Assistant(1976), Terminal Velocity(1108), Kimi Writer(576), Denova(472), Vela(454), 51mazi(394), NovelClaw(343), Show Me The Story(341), StoryForge(291), NeuroBook(266)

## 开发路线

[x] 项目架构设计与基础搭建
[x] 图数据库管理与关系查询
[x] 质量评价系统
[x] 写作技巧知识库
[x] 生成流水线
[x] Web UI 控制台
[ ] LLM API 集成
[ ] 实际章节生成
[ ] 长文本上下文管理
[ ] 回描/Foreshadowing 系统
[ ] 多 Agent 协作
[ ] 全书润色与去AI味
[ ] 导出功能

MIT License
