"""主入口:抓取前一天的 AI 新闻并通过邮件发送"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from .fetcher import fetch_all
from .renderer import render_email
from .sender import send_email
from .summarizer import summarize


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="每日 AI 新闻聚合邮件")
    p.add_argument(
        "--date",
        help="指定目标日期 (YYYY-MM-DD),默认为运行时区的'昨天'",
        default=None,
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="只生成 HTML 不发送邮件 (写入 output/preview.html)",
    )
    p.add_argument(
        "--no-summary",
        action="store_true",
        help="跳过 Claude 总结 (用于本地快速调试,省 API 费用)",
    )
    return p.parse_args()


def main() -> int:
    setup_logging()
    args = parse_args()
    logger = logging.getLogger("ai-daily")

    tz_name = os.environ.get("TIMEZONE", "Asia/Shanghai")
    tz = ZoneInfo(tz_name)

    if args.date:
        target_date = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=tz)
    else:
        now = datetime.now(tz)
        target_date = (now - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )

    date_str = target_date.strftime("%Y-%m-%d")
    logger.info("目标日期: %s (%s)", date_str, tz_name)

    items = fetch_all(target_date, tz)

    if not items:
        logger.warning("未抓到任何新闻,仍发送一封空邮件以便观察")

    summary: str | None = None
    if not args.no_summary:
        summary = summarize(items, date_str)

    subject, html = render_email(items, target_date, summary)

    if args.dry_run:
        out_dir = "output"
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "preview.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info("Dry-run: 已写入 %s (subject=%s)", path, subject)
        return 0

    try:
        send_email(subject, html)
    except Exception as e:
        logger.exception("发送邮件失败: %s", e)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
