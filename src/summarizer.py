"""使用 Claude 生成中文每日 AI 热点总结"""
from __future__ import annotations

import logging
import os
from typing import Iterable

from anthropic import Anthropic

from .fetcher import NewsItem

logger = logging.getLogger(__name__)

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")

SYSTEM_PROMPT = """你是一名资深 AI 行业编辑,任务是把今天全球 AI 新闻整理成一段精炼的中文热点摘要。

要求:
1. 长度 250-400 个汉字,不用超出。
2. 用一段或两段连贯文字,不要列点、不要 markdown 标题。
3. 突出 3-5 个最重要的事件,每个事件简明交代主体、动作、影响。
4. 风格:专业、克制、有判断力,可以适度点评趋势,不要堆砌形容词。
5. 国内厂商和国际厂商各占一定篇幅,如果国内新闻较少,可以只一两句带过。
6. 直接输出正文,不要"以下是总结"之类的开场白。"""


def _format_items_for_prompt(items: Iterable[NewsItem]) -> str:
    lines = []
    for it in items:
        # 摘要截断 120 字以控制 token
        s = it.summary[:120] if it.summary else ""
        lines.append(f"- [{it.source}|{it.category}] {it.title}" + (f" — {s}" if s else ""))
    return "\n".join(lines)


def summarize(items: list[NewsItem], date_str: str) -> str | None:
    """
    生成中文每日总结。失败时返回 None,调用方应优雅降级 (邮件不带总结部分)。

    需要环境变量: ANTHROPIC_API_KEY
    可选环境变量: CLAUDE_MODEL (默认 claude-sonnet-4-20250514)
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("未设置 ANTHROPIC_API_KEY,跳过 AI 总结")
        return None

    if not items:
        logger.info("没有新闻条目,跳过总结")
        return None

    try:
        client = Anthropic(api_key=api_key)
        news_text = _format_items_for_prompt(items)
        user_msg = (
            f"以下是 {date_str} 全球 AI 行业的新闻列表 (共 {len(items)} 条),"
            f"请按要求输出中文热点摘要:\n\n{news_text}"
        )

        logger.info("调用 Claude (%s) 生成中文总结,新闻 %d 条", MODEL, len(items))
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )

        text_parts = []
        for block in resp.content:
            if getattr(block, "type", None) == "text":
                text_parts.append(block.text)
        summary = "".join(text_parts).strip()
        if not summary:
            logger.warning("Claude 返回空内容")
            return None

        logger.info("总结生成成功,长度 %d 字", len(summary))
        return summary

    except Exception as e:
        logger.exception("Claude 总结失败,将不带总结发送邮件: %s", e)
        return None
