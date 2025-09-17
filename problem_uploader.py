import asyncio
from playwright.async_api import async_playwright, TimeoutError
from captcha_solver.vnc_server import VNCServer
from captcha_solver.manual_fallback_handler import ManualFallbackHandler
from captcha_solver.process_runner import ProcessRunner
from captcha_solver.page_controller import PageController
from utils.notifier import Notifier


class LinkedInUploader:
    def __init__(self, linkedin_email: str, linkedin_password: str, notifier: Notifier):
        self._linkedin_email = linkedin_email
        self._linkedin_password = linkedin_password
        self._notifier = notifier
        self._browser = None
        self._page = None
        self._pr = None

    async def _setup(self, p) -> None:
        self._browser = await p.chromium.launch(
            headless = False,
            args = [
                "--start-maximized",
                "--kiosk",
                "--no-first-run",
                "--no-default-browser-check",
            ]
        )
        self._page = await self._browser.new_page(no_viewport = True)
        vnc_server = VNCServer()
        manual_fallback_handler = await ManualFallbackHandler.create(self._page, vnc_server, self._notifier)
        self._page_controller = PageController(self._page, manual_fallback_handler)
        self._pr = ProcessRunner(manual_fallback_handler)
    
    async def _login(self) -> None:
        try:
            print("Navigating to LinkedIn login page...")
            await self._pr.run_with_fallback(
                lambda: self._page.goto("https://www.linkedin.com/checkpoint/rm/sign-in-another-account")
            )

            print("Filling email...")
            await self._pr.run_with_fallback(
                lambda: self._page.get_by_label("Email or phone").fill(self._linkedin_email)
            )

            print("Filling password...")
            await self._pr.run_with_fallback(
                lambda: self._page.get_by_label("Password").fill(self._linkedin_password)
            )

            print("Clicking sign in and waiting for proceed event...")
            await self._pr.run_with_fallback(
                lambda: self._page.get_by_label("Sign in", exact = True).click()
            )

            print("Waiting for login to complete...")
            await self._pr.run_with_fallback(
                lambda: self._page.get_by_role("link", name = "Home", exact = True).wait_for(timeout = 15000)
            )

        except Exception:
            raise

        print("Login successful!")
        print("Starting a post...")

    async def _publish_post(self, post_content: str) -> None:
        try:

            await self._pr.run_with_fallback(
                lambda: self._page.get_by_role("button", name = "Start a post", exact = True).click(timeout = 10000)
            )

            await self._pr.run_with_fallback(
                lambda: self._page.get_by_label("Text editor for creating content").click(timeout = 10000)
            )
            
            await self._pr.run_with_fallback(
                lambda: self._page.keyboard.insert_text(post_content)
            )

            await self._pr.run_with_fallback(
                lambda: self._page.get_by_role("button", name = "Post", exact = True).click(timeout = 10000)
            )

        except Exception:
            raise

        print("Post published successfully.")
        await asyncio.sleep(3)

    async def upload(self, post_content: str) -> None:
        try:
            async with async_playwright() as p:
                await self._setup(p)
                await self._login()
                await self._publish_post(post_content)

        except TimeoutError:
            print("Timed out while waiting for an element.")
            raise

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise

        finally:
            if self._browser and self._browser.is_connected():
                await self._browser.close()
                self._browser = None
