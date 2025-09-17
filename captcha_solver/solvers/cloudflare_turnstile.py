from playwright.async_api import Page, TimeoutError, Mouse, Frame
from ..human_mouse import HumanMouse
import time
from .solver_interface import SolverInterface

class CloudflareTurnstile(SolverInterface):
    def __init__(self, page: Page):
        self._page = page
        self._cursor = HumanMouse(self._page.mouse)

    def is_present(self, frame: Frame) -> bool:
        return frame and "challenges.cloudflare.com" in frame.url

    async def solve(self, frame: Frame) -> str | None:
        try:
            outer_div = self._page.locator("div#cf-turnstile[data-sitekey]")
            bounding_box = await outer_div.bounding_box()

            if bounding_box:
                center_x = bounding_box['x'] + bounding_box['width'] / 2
                center_y = bounding_box['y'] + bounding_box['height'] / 2

                print(f"Calculated center coordinates: ({center_x}, {center_y})")

                await self._page.mouse.click(center_x, center_y)

                print("Click event fired successfully.")
                await self._page.wait_for_timeout(3000)

                await self._page.keyboard.press('Tab')
                await self._page.wait_for_timeout(3000)

                await self._page.keyboard.press('Space')
                await self._page.wait_for_timeout(3000)
            else:
                print("Element with data-sitekey not found.")
        
            
        except Exception as e:
            print(f"Failed to solve captcha: {e}")
            return None
