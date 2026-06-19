"""RSS 抓取模块 - 抓取所有源,过滤出"前一天"发布的条目"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, time
from typing import Iterable
from zoneinfo import ZoneInfo

import feedparser
from dateutil import parser as date_parser

from .feeds import FEEDS, AI_KEYWORDS

logger = logging.getLogger(__name__)

# feedparser 默认 UA 经常被反爬,换成普通浏览器 UA
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
feedparser.USER_AGENT = USER_AGENT

# 预编译关键词正则,大小写不敏感,使用边界避免匹配 "Air" → "AI"
# 中文无需边界,英文用 \b
_AI_PATTERNS: list[re.Pattern[str]] = []
for kw in AI_KEYWORDS:
    if re.search(r"[\u4e00-\u9fff]", kw):  # 含中文
        _AI_PATTERNS.append(re.compile(re.escape(kw), re.IGNORECASE))
    else:
        # 英文加单词边界,但 GPT-4 之类带连字符的也要兼容
        _AI_PATTERNS.append(re.compile(r"(?<![A-Za-z])" + re.escape(kw) + r"(?![A-Za-z])", re.IGNORECASE))


@dataclass
class NewsItem:
    source: str
    category: str
    title: str
    link: str
    summary: str
    published: datetime  # 已转为目标时区的 aware datetime


def _parse_published(entry) -> datetime | None:
    """从 entry 解析发布时间,返回 UTC aware datetime。"""
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        st = entry.get(key)
        if st:
            try:
                return datetime(*st[:6], tzinfo=ZoneInfo("UTC"))
            except Exception:
                pass
    for key in ("published", "updated", "created"):
        s = entry.get(key)
        if s:
            try:
                dt = date_parser.parse(s)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=ZoneInfo("UTC"))
                return dt
            except Exception:
                pass
    return None


def _clean_summary(raw: str, max_len: int = 280) -> str:
    """去 HTML 标签,折叠空白,截断长度。"""
    if not raw:
        return ""
    text = re.sub(r"<[^>]+>", "", raw)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_len:
        text = text[: max_len - 1].rstrip() + "…"
    return text


def _is_ai_related(title: str, summary: str) -> bool:
    """检查标题或摘要是否命中任意 AI 关键词。"""
    text = f"{title}\n{summary}"
    return any(p.search(text) for p in _AI_PATTERNS)


def fetch_all(target_date: datetime, tz: ZoneInfo) -> list[NewsItem]:
    """
    抓取所有 RSS 源,只保留发布日期 == target_date 当天 (按 tz 时区) 的条目。
    对 ai_only=True 的源额外过滤:必须命中 AI 关键词。
    """
    day_start = datetime.combine(target_date.date(), time.min, tzinfo=tz)
    day_end = day_start + timedelta(days=1)
    logger.info(
        "抓取 %d 个 RSS 源,过滤窗口 [%s, %s)",
        len(FEEDS), day_start.isoformat(), day_end.isoformat(),
    )

    items: list[NewsItem] = []
    for entry_tuple in FEEDS:
        # 兼容旧 3 元组写法
        if len(entry_tuple) == 3:
            name, url, category = entry_tuple
            ai_only = False
        else:
            name, url, category, ai_only = entry_tuple

        try:
            parsed = feedparser.parse(url, request_headers={"User-Agent": USER_AGENT})
        except Exception as e:
            logger.warning("[%s] 抓取异常: %s", name, e)
            continue

        if parsed.bozo and not parsed.entries:
            logger.warning("[%s] 解析失败: %s", name, parsed.bozo_exception)
            continue

        kept = 0
        skipped_keyword = 0
        for entry in parsed.entries:
            pub = _parse_published(entry)
            if pub is None:
                continue
            pub_local = pub.astimezone(tz)
            if not (day_start <= pub_local < day_end):
                continue

            title = (entry.get("title") or "").strip()
            link = (entry.get("link") or "").strip()
            if not title or not link:
                continue

            summary = _clean_summary(entry.get("summary") or entry.get("description") or "")

            # AI 关键词过滤
            if ai_only and not _is_ai_related(title, summary):
                skipped_keyword += 1
                continue

            items.append(NewsItem(
                source=name,
                category=category,
                title=title,
                link=link,
                summary=summary,
                published=pub_local,
            ))
            kept += 1

        if ai_only:
            logger.info(
                "[%s] 共 %d 条,匹配日期 %d 条 (AI 过滤后保留),按关键词剔除 %d 条",
                name, len(parsed.entries), kept, skipped_keyword,
            )
        else:
            logger.info("[%s] 共 %d 条,匹配 %d 条", name, len(parsed.entries), kept)

    # 同标题去重
    seen: set[str] = set()
    deduped: list[NewsItem] = []
    for it in items:
        key = re.sub(r"\W+", "", it.title.lower())[:80]
        if key in seen:
            continue
        seen.add(key)
        deduped.append(it)

    deduped.sort(key=lambda x: x.published, reverse=True)
    logger.info("去重后总计 %d 条", len(deduped))
    return deduped


def group_by_category(items: Iterable[NewsItem]) -> dict[str, list[NewsItem]]:
    """按 category 分组,保持原顺序。"""
    groups: dict[str, list[NewsItem]] = {}
    for it in items:
        groups.setdefault(it.category, []).append(it)
    return groups
