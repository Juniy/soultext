# GitHub Top AI 写小说项目调研分析

> 调研时间：2026-07-14
> 数据来源：GitHub API
> 筛选标准：按 Star 数排序，聚焦 AI 辅助长篇小说创作领域

---

## 目录

1. [AI-Novel-Writing-Assistant ★1976](#1-ai-novel-writing-assistant--1976)
2. [Terminal Velocity ★1108](#2-terminal-velocity--1108)
3. [Kimi Writer ★576](#3-kimi-writer--576)
4. [Denova ★472](#4-denova--472)
5. [Vela ★454](#5-vela--454)
6. [51mazi ★394](#6-51mazi--394)
7. [NovelClaw ★343](#7-novelclaw--343)
8. [Show Me The Story ★341](#8-show-me-the-story--341)
9. [StoryForge ★291](#9-storyforge--291)
10. [NeuroBook ★266](#10-neurobook--266)

---

## 1. AI-Novel-Writing-Assistant ★1976

**链接**: https://github.com/ExplosiveCoderflome/AI-Novel-Writing-Assistant
**语言**: TypeScript | **技术栈**: React + Vite, Express + Prisma, LangChain, LangGraph

### 项目架构
- **Monorepo 架构**：pnpm workspace 管理前后端
- **Creative Hub**：创意中心，从一句话灵感出发
- **自动导演开书**：AI 作为导演自动规划全书
- **本书世界上下文**：维护整本书的世界观上下文
- **整本生产主链**：端到端的章节生产流水线
- **写法引擎**：可插拔的写作风格引擎

### 核心优势
- Agent 驱动工作流：使用 LangGraph 构建 Agent 工作流
- RAG 知识库：支持检索增强生成，保持前后一致
- 长篇小说原生支持：专门面向长篇小说设计，处理超长上下文
- 整本生产流水线：从灵感→大纲→章节→润色的完整流程
- 写法引擎：可配置的写作风格和方法论

### 可借鉴点
- Agent 工作流架构
- 世界观上下文管理机制
- 可插拔写法引擎设计

---

## 2. Terminal Velocity ★1108

**链接**: https://github.com/mind-protocol/terminal-velocity
**语言**: Python

### 项目架构
- **10 AI Agents 协作系统**：10 个 AI Agent 组成团队，各自扮演不同角色
- **角色分工**：构思、写作、编辑、校对等职责分离
- **自主创作流程**：Agent 团队自主完成 10 万字小说创作
- **已出版小说**：在 Amazon 出版了纸质书和 Kindle 版本

### 核心优势
- 多 Agent 协作可以产出高质量长篇作品
- 角色分工明确，各司其职
- 从构思到出版完全自动化
- 实际出版验证了 AI 创作长篇小说的可行性

### 可借鉴点
- 多 Agent 角色分工协作模式
- Agent 团队的组织架构
- 端到端的自动化流水线

---

## 3. Kimi Writer ★576

**链接**: https://github.com/Doriandarko/kimi-writer
**语言**: Python | **模型**: kimi-k2-thinking

### 项目架构
- **独立写作 Agent**：基于单个强大模型的自主写作 Agent
- **实时流式输出**：实时展示 AI 的推理和写作过程
- **智能上下文管理**：自动压缩上下文以支持长文本
- **多格式支持**：小说、书籍、短篇故事集

### 核心优势
- 利用模型的深度推理能力规划故事
- 上下文压缩解决长文本创作的上下文窗口限制
- Agent 自主制定写作计划并执行

### 可借鉴点
- 上下文压缩和管理策略
- 实时流式显示写作过程

---

## 4. Denova ★472

**链接**: https://github.com/alfredxw/denova
**语言**: Go | **技术栈**: Go 后端 + Web 前端

### 项目架构
- **AI 创作平台**：面向小说创作与 AI 角色扮演游戏
- **Agent 系统**：内置 AI Agents、Skills、Subagent Workflows
- **自动化引擎**：自动化和工作流引擎
- **图像生成**：内置图像自动生成
- **版本控制**：项目版本管理
- **插件系统**：Skills 可扩展架构

### 核心优势
- Go 语言后端，性能优秀
- 插件化架构，Skills 系统支持功能扩展
- 支持项目的版本管理
- 同时支持文本和图像生成

### 可借鉴点
- 插件化/Skills 架构设计
- 版本控制与项目管理
- AI Agent + 工作流自动化

---

## 5. Vela ★454

**链接**: https://github.com/heider-x/vela
**语言**: TypeScript | **技术栈**: React + Electron + TypeScript

### 项目架构
- **桌面 IDE**：Electron 桌面应用
- **本地 LLM**：支持本地大语言模型运行
- **RAG 引擎**：内置检索增强生成
- **隐私优先**：数据本地处理，隐私安全
- **BYOK**：自带密钥，灵活接入各种 LLM

### 核心优势
- 隐私优先设计，适合对隐私敏感的作者
- 本地 LLM 支持，不依赖云服务
- 全功能小说写作 IDE
- RAG 增强保持故事一致性

### 可借鉴点
- 隐私优先的设计理念
- 本地 LLM + RAG 的架构
- 小说写作 IDE 的交互设计

---

## 6. 51mazi ★394

**链接**: https://github.com/xiaoshengxianjun/51mazi
**语言**: Vue | **技术栈**: Electron + Vue 3 + Tailwind CSS

### 项目架构
- **桌面软件**：基于 Electron + Vue 3 的桌面应用
- **创作辅助工具集**：随机取名、小说地图、关系图谱、人物档案、时间线、词条字典
- **AI 功能集成**：AI 写作、AI 封面生成、AI 人物图、AI 场景图
- **网文下载工具**：支持网文小说下载

### 核心优势
- 功能全面，集成了各种创作辅助工具
- 关系图谱、地图设计等可视化工具
- 多书籍管理系统
- AI 多模态（文本 + 图像）生成

### 可借鉴点
- 人物档案、关系图谱、时间线的可视化设计
- 多类型 AI 辅助功能的集成方式
- 小说创作辅助工具的 UX 设计

---

## 7. NovelClaw ★343

**链接**: https://github.com/iLearn-Lab/NovelClaw
**语言**: Python | **技术栈**: FastAPI + Python

### 项目架构
- **动态记忆优先**：动态记忆优先的协作 AI 框架
- **多 Agent 协作**：多个 AI Agent 协同工作
- **章节规划**：自动规划章节结构
- **RAG 增强**：检索增强生成
- **长篇小说原生**：专注于长篇故事生成

### 核心优势
- 动态记忆架构，不同于简单的上下文窗口
- 协作框架让多个 AI Agent 协同工作
- 在长文本中保持叙事一致性
- 基于 FastAPI，易于集成

### 可借鉴点
- 动态记忆管理策略
- 多 Agent 协作框架设计
- 长文本一致性保障方案

---

## 8. Show Me The Story ★341

**链接**: https://github.com/Nigh/show-me-the-story
**语言**: Go | **技术栈**: Go + Svelte + Web UI

### 项目架构
- **单二进制文件**：一个可执行文件包含所有功能
- **两阶段创作**：先大纲审核修订，再逐章写作
- **逐章审核机制**：每章生成后可确认和修改
- **自动确认模式**：可开关的自动连写模式
- **多项目管理**：每部小说一个独立项目
- **回描系统**：Foreshadowing 伏笔机制
- **事实检查**：自动事实一致性检查
- **全书润色**：整本书的润色功能

### 核心优势
- 零依赖部署，单文件运行无需数据库
- 两阶段创作流程，每一步都有人工参与
- 回描机制专门处理伏笔和前后呼应
- 事实检查保持故事一致性
- 中英文双语言支持

### 可借鉴点
- 两阶段创作流程（大纲→章节审核）
- 回描/foreshadowing 机制
- 逐章审核的人机协作模式
- 单文件部署的极简设计

---

## 9. StoryForge ★291

**链接**: https://github.com/yuanbw2025/storyforge
**语言**: TypeScript | **技术栈**: React 19 + TypeScript + Vite

### 项目架构
- **纯前端应用**：所有逻辑在浏览器中运行
- **本地优先**：数据存储在本地
- **提示词全透明**：所有提示词对用户可见
- **完整创作链路**：灵感→设定→大纲→正文→审校→导出

### 核心优势
- 纯前端，无需后端服务器，部署简单
- 透明可控，用户可查看和修改所有提示词
- 创作链路覆盖从灵感到底稿的全过程
- 本地优先保护用户隐私

### 可借鉴点
- 提示词透明的设计理念
- 纯前端的轻量架构
- 完整创作链路的流程设计

---

## 10. NeuroBook ★266

**链接**: https://github.com/notnotype/neuro-book
**语言**: TypeScript | **技术栈**: Bun + React

### 项目架构
- **多 Agent 写作 IDE**：把软件工程方法论引入写作
- **三大支柱**：软件工程方法论、写作方法论、AI Agent
- **IDE 化设计**：像开发软件一样开发小说

### 核心优势
- 工程化思维，将软件工程最佳实践引入写作
- 写作方法论系统化编码
- AI Agent 辅助创作全过程

### 可借鉴点
- 软件工程方法论在写作中的应用
- 写作理论的系统化编码
- IDE 化的交互设计

---

## 综合分析与项目启发

### 技术架构趋势

| 趋势 | 占比 | 代表项目 |
|------|------|----------|
| TypeScript/React | 50% | AI-Novel-Writing-Assistant, Vela, StoryForge, NeuroBook |
| Python + FastAPI | 30% | NovelClaw, Kimi Writer, Terminal Velocity |
| Go 语言 | 20% | Denova, Show Me The Story |
| Electron 桌面应用 | 30% | Vela, 51mazi |
| 纯前端应用 | 20% | StoryForge |
| 多 Agent 架构 | 40% | Terminal Velocity, NovelClaw, Denova |

### 核心功能分布

| 功能 | 覆盖率 | 说明 |
|------|--------|------|
| RAG/知识检索 | 60% | 保持故事一致性 |
| 图关系/角色管理 | 30% | 51mazi 最完善 |
| 世界观管理 | 40% | AI-Novel-Writing-Assistant 最突出 |
| 大纲生成 | 80% | 几乎全部支持 |
| 逐章写作 | 80% | 大部分支持 |
| 润色/校审 | 40% | Show Me The Story, StoryForge |
| 时间线管理 | 20% | 51mazi |
| 多 Agent 协作 | 40% | 高级项目标配 |
| 图像生成 | 20% | Denova, 51mazi |

### 对 soultext 项目的具体启发

1. **架构选型**：采用 FastAPI + Python 后端 + React 前端
2. **多 Agent 协作**：参考 Terminal Velocity 的 Agent 分工模式
3. **图数据库**：参考 51mazi 的关系图谱 + 时间线，用图数据库实现
4. **两阶段流程**：参考 Show Me The Story 的大纲→章节审核流程
5. **写法引擎**：参考 AI-Novel-Writing-Assistant 的可插拔写法引擎
6. **动态记忆**：参考 NovelClaw 的动态记忆管理
7. **提示词透明**：参考 StoryForge 的透明提示词设计
8. **工程化**：参考 NeuroBook 的软件工程方法论
9. **评价体系**：现有项目普遍缺失，这是 soultext 核心差异化优势
10. **自优化循环**：基于评价结果自动优化提示词和写作策略
