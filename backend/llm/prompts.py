# -*- coding: utf-8 -*-
"""Soultext 小说创作 LLM 提示词模板

从 doc/ 文件夹的所有写作技巧中提炼核心原则，
确保每一次生成都融入高质量写作方法论。
"""

from typing import Dict, List, Optional

SYSTEM_TEMPLATE = """你是「Soultext」—— 世界顶级的华语小说创作 AI。你兼具文学大师的审美、资深编辑的洞察力和网文作者的叙事掌控力。

你的使命是写出直击灵魂、感人至深、引人入胜的小说作品。

## 核心创作原则
1. 情感为本：故事情节必须服务于情感共鸣，让读者笑、哭、愤怒、感动、遗憾。
2. 人物驱动：角色必须有真实的人性弱点、欲望、矛盾和成长弧光。
3. 展现而非讲述：通过对话、动作、环境、感官细节展现情节，避免直接概括。
4. 冲突多层次：同时构建人际冲突、内心冲突、环境/社会冲突三层结构。
5. 悬念与节奏：每章结尾留钩子，控制张弛节奏，大高潮前有小高潮铺垫。
6. 伏笔与呼应：重要情节转折前至少埋设 2-3 处伏笔，回收时具有情感冲击力。
7. 细节质感：用具体、独特的细节代替通用描写，让场景和人物有真实感。
8. 去AI味：避免工整的长排比、固定句式开头、过度解释，保持自然语言节奏。
9. 五感描写：每次场景描写至少调动视觉、听觉、触觉、嗅觉、味觉中的三种。
10. 对话差异化：每个角色的语言风格迥异，对话有潜台词，不做信息搬运。"""


def build_outline_prompt(idea: str, genre: str, settings: Optional[Dict] = None) -> List[Dict]:
    s = settings or {}
    style_guide = s.get("writing_style", "")
    tone = s.get("tone", "")
    custom = s.get("custom_instructions", "")
    style_str = f"\n文风要求：{style_guide}" if style_guide else ""
    tone_str = f"\n基调要求：{tone}" if tone else ""
    custom_str = f"\n额外要求：{custom}" if custom else ""

    user_prompt = f"""你是一位顶尖的小说架构师。请为一部【{genre}】类型的小说设计完整的大纲。

核心创意：{idea}

请以如下结构输出大纲：

1. 【核心主题】：这部小说想表达什么？它如何触及人性深处？
2. 【人物群像】：每个主要角色的姓名、年龄、性格关键词、核心欲望与恐惧、初始缺陷、成长弧线。
3. 【世界观设定】：故事发生的世界/时代背景、独特规则、社会结构、核心矛盾。
4. 【主线剧情】：分 3-5 幕，每幕 2-4 个关键情节节点，构成完整的起承转合结构。
5. 【爽点与虐点分布】：在什么位置让读者爽，什么位置让读者虐，规划情绪曲线。
6. 【伏笔系统】：重要的伏笔埋设在哪些章节，预计在哪些章节回收。
7. 【章节规划】：总章节规划，每章核心作用和预期字数。

{style_str}{tone_str}{custom_str}

要求：大纲至少 2000 字，人物弧光必须有说服力，情节冲突必须层层递进。"""

    return [
        {"role": "system", "content": SYSTEM_TEMPLATE},
        {"role": "user", "content": user_prompt},
    ]


def build_chapter_prompt(novel_title: str, chapter_num: int, outline_summary: str,
                         previous_chapters: List[str], character_context: str,
                         scene_context: str, world_context: str,
                         settings: Optional[Dict] = None) -> List[Dict]:
    s = settings or {}
    style_guide = s.get("writing_style", "")
    custom = s.get("custom_instructions", "")
    pov = s.get("pov", "")
    pace = s.get("pace", "")
    style_str = f"\n文风：{style_guide}" if style_guide else ""
    custom_str = f"\n额外要求：{custom}" if custom else ""
    pov_str = f"\n视角：{pov}" if pov else ""
    pace_str = f"\n节奏：{pace}" if pace else ""

    prev_text = ""
    if previous_chapters:
        prev_text = "\n\n".join([f"--- 前文回顾 ---\n{ch[-500:]}" for ch in previous_chapters[-3:]])

    user_prompt = f"""请为《{novel_title}》撰写第 {chapter_num} 章正文。

全书大纲参考：
{outline_summary[:1500]}

角色当前状态：
{character_context[:500]}

当前场景：
{scene_context[:500]}

世界观上下文：
{world_context[:500]}{pov_str}{pace_str}{style_str}{custom_str}

前文回顾（最近章节尾段）：
{prev_text}

写作要求：
1. 本章字数 3000-8000 字（长篇按需）
2. 开篇用有冲击力的细节或对话抓住读者
3. 用五感描写营造氛围，让读者身临其境
4. 通过角色言行展现性格，避免平铺直叙
5. 章尾留下悬念钩子，让读者欲罢不能
6. 注意与全文节奏和情绪曲线的协调统一
7. 自然融入已有伏笔或埋设新伏笔
8. 如果有前文，保持角色性格和剧情逻辑一致性

开始创作，请直接输出正文："""

    return [
        {"role": "system", "content": SYSTEM_TEMPLATE},
        {"role": "user", "content": user_prompt},
    ]


def build_revision_prompt(content: str, feedback: str, settings: Optional[Dict] = None) -> List[Dict]:
    s = settings or {}
    custom = s.get("custom_instructions", "")

    user_prompt = f"""请根据以下反馈修改小说内容。

## 需要修改的内容
{content}

## 修改意见
{feedback}

{custom}

修改要求：
1. 保留原文精华，只针对反馈中提到的问题修改
2. 避免 AI 感过重的表达方式（如不必要的解释、工整的排比）
3. 增强情感冲击力和代入感
4. 修改后与其他章节保持一致的风格和节奏
5. 确保修改后的文字读起来自然流畅，像人类作家的手笔

请直接输出修改后的完整内容："""

    return [
        {"role": "system", "content": SYSTEM_TEMPLATE},
        {"role": "user", "content": user_prompt},
    ]


def build_polish_prompt(content: str, settings: Optional[Dict] = None) -> List[Dict]:
    s = settings or {}
    style_guide = s.get("writing_style", "")
    style_str = f"\n文风偏好：{style_guide}" if style_guide else ""

    user_prompt = f"""请对以下小说内容进行润色优化，提升文学质感，消除 AI 写作痕迹。

{content}{style_str}

润色要求：
1. 消除 AI 感：删除"值得注意的是""可以想象""让我们看看"等 AI 套路开头
2. 增强画面感：补充恰到好处的感官细节，让场景活起来
3. 优化句子节奏：长句拆分、短句连接，读起来有呼吸感和韵律
4. 强化情感：在关键处增加情感渲染，让读者有代入感
5. 丰富对话张力：让潜台词更丰富，语言更符合人物性格
6. 注意不要过度修改，保留原文风格和叙事节奏

请输出润色后的完整内容："""

    return [
        {"role": "system", "content": SYSTEM_TEMPLATE},
        {"role": "user", "content": user_prompt},
    ]
