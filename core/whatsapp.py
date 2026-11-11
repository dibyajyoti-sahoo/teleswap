import re

import httpx
from .constants import settings, logger

class WhatsAppClient:
    def __init__(self):
        self.url = f"https://graph.facebook.com/v25.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        self.recipient = settings.WHATSAPP_RECIPIENT
        self.template_name = settings.WHATSAPP_TEMPLATE_NAME
        self.template_lang = settings.WHATSAPP_TEMPLATE_LANG

    # Template variables can't contain newlines/tabs or 4+ spaces in a row,
    # and the whole body must stay under 1024 chars.
    TEMPLATE_PARAM_MAX = 900

    @staticmethod
    def _clean_param(text: str) -> str:
        lines = [ln.strip() for ln in text.replace("\t", " ").splitlines()]
        text = " | ".join(ln for ln in lines if ln and not set(ln) <= {"-"})
        return re.sub(r" {2,}", " ", text).strip()

    @classmethod
    def _chunk(cls, text: str) -> list:
        limit = cls.TEMPLATE_PARAM_MAX
        chunks = []
        while len(text) > limit:
            cut = text.rfind(" | ", 0, limit)
            if cut <= 0:
                cut = text.rfind(" ", 0, limit)
            if cut <= 0:
                cut = limit
            chunks.append(text[:cut].strip())
            text = text[cut:].lstrip(" |")
        if text:
            chunks.append(text)
        return chunks

    async def send_alert(self, message: str) -> bool:
        """Sends an alert via the approved template if configured, else as free-form text."""
        if not self.template_name:
            return await self.send_text(message)
        chunks = self._chunk(self._clean_param(message)) or ["(empty message)"]
        ok = True
        for i, chunk in enumerate(chunks, 1):
            if len(chunks) > 1:
                chunk = f"({i}/{len(chunks)}) {chunk}"
            ok = await self.send_template(chunk) and ok
        return ok

    async def send_template(self, param: str) -> bool:
        """Sends the configured template with one body variable."""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.recipient,
            "type": "template",
            "template": {
                "name": self.template_name,
                "language": {"code": self.template_lang},
                "components": [
                    {"type": "body", "parameters": [{"type": "text", "text": param}]}
                ],
            },
        }
        return await self._post(payload, "template message")

    async def send_text(self, message: str) -> bool:
        """Sends a simple text message."""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.recipient,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        return await self._post(payload, "text message")

    async def send_catalogs(self, filename: str, sections: list) -> bool:
        """Sends tabular data as an interactive list with categories/sheets."""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.recipient,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": { "type": "text", "text": "Spreadsheet Data" },
                "body": { "text": f"Data extracted from {filename}" },
                "footer": { "text": "Click button below to view" },
                "action": {
                    "button": "View Table Items",
                    "sections": sections
                }
            }
        }
        return await self._post(payload, "interactive list")

    async def _post(self, payload: dict, msg_type: str) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.url, json=payload, headers=self.headers, timeout=10.0)
                if response.status_code in (200, 201):
                    msg_id = (response.json().get("messages") or [{}])[0].get("id")
                    logger.info(f"WhatsApp {msg_type} accepted by Meta (id={msg_id}). Delivery is confirmed only via webhook.")
                    return True
                else:
                    logger.error(f"Failed to send WhatsApp {msg_type}: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.exception(f"Exception occurred while calling WhatsApp API: {e}")
            return False
