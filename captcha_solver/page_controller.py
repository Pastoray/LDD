from playwright.async_api import Page, Frame
import time
from .router import Router
from .vnc_server import VNCServer
from .manual_fallback_handler import ManualFallbackHandler
import asyncio

class PageController:
    def __init__(self, page: Page, manual_fallback_handler: ManualFallbackHandler):
        self._page = page
        self._router = Router(page, manual_fallback_handler)
        self._init_listeners(manual_fallback_handler)

    def _init_listeners(self, manual_fallback_handler: ManualFallbackHandler) -> None:
        self._page.on("framenavigated", self._on_frame_navigated)
        self._page.on(
            "load",
            lambda: asyncio.create_task(manual_fallback_handler.on_page_load())
        )

    async def _on_frame_navigated(self, frame: Frame) -> None:
        if self._page.is_closed() or frame == self._page.main_frame:
            return

        else:
            await self._router.route_captcha(frame)
