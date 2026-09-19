import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class C6MailClient:
    """Small dependency-free adapter for C6-Mail-Services."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None, timeout: int = 20):
        self.base_url = (base_url or os.getenv("C6_MAIL_BASE_URL", "")).rstrip("/")
        self.api_key = api_key or os.getenv("C6_MAIL_API_KEY", "")
        self.timeout = timeout

    def send(self, to: list[str], subject: str, text: str, html: str | None = None, reply_to: str | None = None) -> dict:
        if not self.base_url:
            raise RuntimeError("C6_MAIL_BASE_URL is not configured")
        payload = {"to": to, "subject": subject, "text": text}
        if html:
            payload["html"] = html
        if reply_to:
            payload["reply_to"] = reply_to
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-C6-Mail-Key"] = self.api_key
        request = Request(f"{self.base_url}/api/v1/mail/send", data=body, headers=headers, method="POST")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError) as exc:
            raise RuntimeError(f"C6 mail service request failed: {exc}") from exc
