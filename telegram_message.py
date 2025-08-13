import os
import json
import requests
import logging

logger = logging.getLogger(__name__)

class TelegramMessager:
    """Handles sending messages to Telegram."""

    def __init__(self, bot_token=None, chat_id=None):
        """Initialize with bot token and chat ID, optionally from env vars."""
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def log(self, message):
        """Send a message to Telegram."""
        headers = {'Content-Type': 'application/json'}
        data = {'chat_id': self.chat_id, 'text': message}
        print(data)
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send message to Telegram: {e}")
