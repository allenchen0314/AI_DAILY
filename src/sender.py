"""通过 Resend 发送邮件"""
from __future__ import annotations

import logging
import os

import resend

logger = logging.getLogger(__name__)


def send_email(subject: str, html: str) -> str:
    """
    发送 HTML 邮件,返回 Resend 返回的邮件 id。

    需要环境变量:
      RESEND_API_KEY  - Resend API key
      MAIL_FROM       - 发件人,如 "AI Daily <onboarding@resend.dev>"
      MAIL_TO         - 收件人,多个用逗号分隔
    """
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        raise RuntimeError("环境变量 RESEND_API_KEY 未设置")

    mail_from = os.environ.get("MAIL_FROM", "AI Daily <onboarding@resend.dev>")
    mail_to_raw = os.environ.get("MAIL_TO")
    if not mail_to_raw:
        raise RuntimeError("环境变量 MAIL_TO 未设置")

    to_list = [s.strip() for s in mail_to_raw.split(",") if s.strip()]
    if not to_list:
        raise RuntimeError("环境变量 MAIL_TO 为空或格式不正确")

    resend.api_key = api_key
    params: resend.Emails.SendParams = {
        "from": mail_from,
        "to": to_list,
        "subject": subject,
        "html": html,
    }

    logger.info("发送邮件 from=%s to=%s subject=%s", mail_from, to_list, subject)
    result = resend.Emails.send(params)
    msg_id = result.get("id") if isinstance(result, dict) else getattr(result, "id", str(result))
    logger.info("邮件已发送,id=%s", msg_id)
    return str(msg_id)
