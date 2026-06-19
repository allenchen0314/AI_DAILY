"""HTML 邮件渲染"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .fetcher import NewsItem, group_by_category

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def render_email(
    items: list[NewsItem],
    target_date: datetime,
    summary: str | None = None,
) -> tuple[str, str]:
    """
    返回 (subject, html_body)。
    summary 为 None 时邮件不渲染总结区块。
    """
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("email.html.j2")

    groups = group_by_category(items)
    order = ["国际", "厂商", "中文"]
    ordered_groups = [(c, groups[c]) for c in order if c in groups]
    for c, lst in groups.items():
        if c not in order:
            ordered_groups.append((c, lst))

    date_str = target_date.strftime("%Y-%m-%d")
    subject = f"[AI Daily] {date_str} · {len(items)} 条全球 AI 新闻"

    # summary 转 HTML 段落
    summary_paragraphs = None
    if summary:
        summary_paragraphs = [p.strip() for p in summary.split("\n\n") if p.strip()]
        if not summary_paragraphs:
            summary_paragraphs = [summary]

    html = template.render(
        date_str=date_str,
        total=len(items),
        groups=ordered_groups,
        summary_paragraphs=summary_paragraphs,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
    return subject, html
