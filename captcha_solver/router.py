import asyncio
from captcha_solver.solvers.cloudflare_turnstile import CloudflareTurnstile
from playwright.async_api import Page, Frame
from .manual_fallback_handler import ManualFallbackHandler

class Router:
    def __init__(self, page: Page, manual_fallback_handler: ManualFallbackHandler):
        self._page = page
        self._manual_fallback_handler = manual_fallback_handler
        self._solvers = [
            CloudflareTurnstile(self._page)
        ]
        self._cf_turnstile = CloudflareTurnstile(self._page)

    def is_captcha_present(self, frame: Frame) -> bool:
        is_present = False
        for solver in self._solvers:
            is_present = is_present or solver.is_present(frame)

        return is_present

    async def route_captcha(self, frame: Frame) -> None:
        if self.is_captcha_present(frame):
            try:
                if self._cf_turnstile.is_present(frame):
                    print("Found turnstile captcha, solving...")
                    await self._cf_turnstile.solve(frame)

                # Potential harmless frame
                else:
                    pass

            except Exception:
                print("Failed to solve captcha.")
                await self._manual_fallback_handler.handle_fallback()
