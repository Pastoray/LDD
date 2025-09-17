import asyncio
import requests
import os

class Notifier:
    def __init__(self, platform: str, api_key: str, chat_id: str):
        self._platform = platform
        self._api_key = api_key
        self._chat_id = chat_id

    async def send_message(self, message: str) -> None:
        if self._platform.lower() == "telegram":
            await self._send_telegram_message(message)
        else:
            print(f"Unsupported notification platform: {self._platform}")

    async def _send_telegram_message(self, message: str) -> None:
        url = f"https://api.telegram.org/bot{self._api_key}/sendMessage"
        payload = {
            "chat_id": self._chat_id,
            "text": message
        }

        try:
            print("Attempting to send notification...")
            response = await asyncio.to_thread(requests.post, url, json = payload, timeout = 10)
            response.raise_for_status()
            print("Notification sent successfully.")

        except Exception as e:
            print(f"Failed to send Telegram notification: {e}")
