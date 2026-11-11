import os

from dotenv import load_dotenv, set_key
import logging
import sys
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("telegram_listener")

class Settings:
    def __init__(self):
        self.TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
        self.TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
        self.TELEGRAM_SESSION = os.getenv("TELEGRAM_SESSION")
        # self.TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if chat_id and chat_id.lstrip("-").isdigit():
            self.TELEGRAM_CHAT_ID = int(chat_id)
        else:
            self.TELEGRAM_CHAT_ID = chat_id

        self.WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
        self.WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.WHATSAPP_RECIPIENT = os.getenv("WHATSAPP_RECIPIENT")

    def update_telegram_session(self, session: str) -> bool:
        try:
            set_key(str(ENV_FILE), "TELEGRAM_SESSION", session)

            self.TELEGRAM_SESSION = session
            os.environ["TELEGRAM_SESSION"] = session

            logger.info("Telegram session updated successfully")
            return True

        except Exception as error:
            logger.exception(f"Failed to update Telegram session: {error}")
            return False

settings = Settings()