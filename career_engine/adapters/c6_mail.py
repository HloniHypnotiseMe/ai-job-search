"""C6 Mail Services adapter.

Verified service contract:
POST /api/v1/mail/send
Header: X-C6-Mail-Key (when MAIL_API_KEY is configured)
Payload: to[], subject, text, optional html/reply_to.

No mail credentials or message bodies are persisted by this adapter.
"""
from __future__ import annotations

import json
import os
from urllib import request


class C6MailAdapter:
    def __init__(self, base_url: str | None = None, api_key: str | None = None, timeout: float = 20.0):
        self.base_url = (base_url or os.getenv("C6_MAIL_BASE_URL", "")).rstrip("/")
        self.api_key = api_key if api_key is not None else os.getenv("C6_MAIL_API_KEY", "")
        self.timeout = timeout

    def send(
        self,
        *,
        to: list[str],
        subject: str,
        text: str = "",
        html: str | None = None,
        reply_to: str | None = None,
    ) -> dict:
        if not self.base_url:
            raise ValueError("C6_MAIL_BASE_URL is required")
        if not to:
            raise ValueError("At least one recipient is required")
        payload = {"to": to, "subject": subject, "text": text}
        if html is not None:
            payload["html"] = html
        if reply_to is not None:
            payload["reply_to"] = reply_to
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-C6-Mail-Key"] = self.api_key
        req = request.Request(
            f"{self.base_url}/api/v1/mail/send",
            data=body,
            headers=headers,
            method="POST",
        )
        with request.urlopen(req, timeout=self.timeout) as response:
            raw = response.read().decode("utf-8")
        result = json.loads(raw)
        if result.get("status") != "sent":
            raise RuntimeError("C6 Mail Services did not confirm delivery")
        return result
