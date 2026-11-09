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
                    logger.info(f"WhatsApp {msg_type} sent successfully!")
                    return True
                else:
                    logger.error(f"Failed to send WhatsApp {msg_type}: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.exception(f"Exception occurred while calling WhatsApp API: {e}")
            return False
