from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import AuthKeyUnregisteredError
from .constants import settings, logger


class AuthClient:
    def __init__(self):
        self.settings = settings
        self.client = None

    def initialize_telegram_client(self):
        session_str = self.settings.TELEGRAM_SESSION or ""

        self.client = TelegramClient(
            session=StringSession(session_str),
            api_id=self.settings.TELEGRAM_API_ID,
            api_hash=self.settings.TELEGRAM_API_HASH,
            auto_reconnect=True
        )

        try:
            self.client.start()

        except AuthKeyUnregisteredError:
            logger.info("[!] Existing session was logged out, revoked, or expired. Re-authenticating...")
            self.client = TelegramClient(
                session=StringSession(""),
                api_id=self.settings.TELEGRAM_API_ID,
                api_hash=self.settings.TELEGRAM_API_HASH,
                auto_reconnect=True
            )
            self.client.start()

        current_session_string = self.client.session.save()
        if current_session_string != session_str:
            logger.info("\n" + "=" * 60)
            logger.info("[!] NEW OR UPDATED TELEGRAM SESSION GENERATED!")
            logger.info("Copy and update your TELEGRAM_SESSION environment variable with this string:")
            logger.info(current_session_string)
            logger.info("=" * 60 + "\n")

            if not self.settings.update_telegram_session(session=current_session_string):
                raise AuthKeyUnregisteredError
            logger.info("Update your TELEGRAM_SESSION environment variable")

        return self.client

auth_manager = AuthClient()
client = auth_manager.initialize_telegram_client()