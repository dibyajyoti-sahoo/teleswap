import os
from telethon import events
from core import logger, client, settings, is_trade_alert, WhatsAppClient, parse_spreadsheet_to_catalogs

wa_client = WhatsAppClient()


@client.on(events.NewMessage(chats=settings.TELEGRAM_CHAT_ID))
async def handle_new_message(event):
    message = event.message
    text = message.text or ""

    sender = await message.get_sender()
    sender_name = getattr(sender, 'first_name', None) or getattr(sender, 'title', 'Unknown')

    logger.info(f"[{message.date}] New message from {sender_name}:")
    logger.info(f"Content:\n{text}\n" + "-" * 40)

    # if message.document and message.file and message.file.ext:
    #     ext = message.file.ext.lower()
    #     if ext in ['.csv', '.xlsx', '.xls']:
    #         logger.info(f"Spreadsheet attached: {message.file.name}. Downloading...")
    #         file_path = await message.download_media()
    #
    #         try:
    #             sections = parse_spreadsheet_to_catalogs(file_path, ext)
    #
    #             if sections:
    #                 logger.info("Dispatching spreadsheet catalog to WhatsApp...")
    #                 await wa_client.send_catalogs(
    #                     filename=message.file.name,
    #                     sections=sections
    #                 )
    #             else:
    #                 logger.info("Spreadsheet was empty or parsing failed. Nothing sent.")
    #
    #         except Exception as e:
    #             logger.error(f"Failed to parse spreadsheet: {e}")
    #         finally:
    #             if os.path.exists(file_path):
    #                 os.remove(file_path)
    #
    #         return

    if not text:
        return

    if is_trade_alert(text):
        logger.info("Alert emojis detected. Forwarding exact text to WhatsApp.")
        await wa_client.send_text(text)
    else:
        logger.info("Message did not contain alert emojis or spreadsheet. Skipped.")


def main():
    logger.info(f"Starting Telegram near real-time listener for chat: {settings.TELEGRAM_CHAT_ID}")
    client.run_until_disconnected()


if __name__ == "__main__":
    main()