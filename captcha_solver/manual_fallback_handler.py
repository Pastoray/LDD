import asyncio
from playwright.async_api import Page
from .vnc_server import VNCServer
from utils.notifier import Notifier

class ManualFallbackHandler:
    def __init__(self, page: Page, vnc_server: VNCServer, notifier: Notifier):
        self._page = page
        self._vnc_server = vnc_server
        self._notifier = notifier
        self._proceed_event = asyncio.Event()
        self._proceed_event.set()

    @classmethod
    async def create(cls, page: Page, vnc_server: VNCServer, notifier: Notifier):
        self = cls(page, vnc_server, notifier)
        await self._page.expose_function("on_proceed_event", self._on_proceed_event)
        return self

    async def handle_fallback(self) -> None:
        self._proceed_event.clear()
        print("Starting manual fallback for human intervention...")
        await self._notifier.send_message(
            "Auto delivery service encountered a problem, human intervention is required"
        )
        
        await self._vnc_server.start()
        await self._inject_signal_button()

        try:
            print("Waiting for user to solve the captcha...")
            await asyncio.wait_for(self._proceed_event.wait(), timeout = 300)
            print("User has signaled that the captcha is solved.")

        except Exception:
            print("Manual fallback timed out. Stopping VNC server.")
            await self._notifier.send_message("Manual fallback timed out.")
            raise

        finally:
            self._vnc_server.stop()
            await self._remove_signal_button()

    async def _on_proceed_event(self) -> None:
        self._proceed_event.set()

    async def on_page_load(self) -> None:
        if not self._proceed_event.is_set():
            await self._inject_signal_button()

    async def _inject_signal_button(self) -> None:
        print("Injecting signal button...")
        script = """
            (function() {
                // Remove any existing signal button to prevent duplicates
                const existingButton = document.getElementById('proceed-signal-button');
                if (existingButton) {
                    existingButton.remove();
                }

                const button = document.createElement('div');
                button.id = 'proceed-signal-button';
                button.textContent = 'Proceed';
                Object.assign(button.style, {
                    position: 'fixed',
                    bottom: '20px',
                    right: '20px',
                    width: '120px',
                    height: '40px',
                    backgroundColor: '#4CAF50',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'grab',
                    zIndex: '99999',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '14px',
                    fontFamily: 'sans-serif',
                    boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
                    userSelect: 'none',
                    transition: 'background-color 0.2s, box-shadow 0.2s'
                });

                // Add hover effects
                button.onmouseover = () => button.style.boxShadow = '0 6px 12px rgba(0,0,0,0.3)';
                button.onmouseout = () => button.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';

                const DRAG_THRESHOLD = 2;

                let isDragging = false;
                let hasMoved = false;
                let currentX, currentY, initialX, initialY, xOffset = 0, yOffset = 0;

                button.addEventListener('mousedown', (e) => {
                    initialX = e.clientX - xOffset;
                    initialY = e.clientY - yOffset;
                    isDragging = true;
                    hasMoved = false;
                    e.preventDefault();
                });

                document.addEventListener('mouseup', () => {
                    isDragging = false;
                });

                document.addEventListener('mousemove', (e) => {
                    if (isDragging) {
                        e.preventDefault();
                        currentX = e.clientX - initialX;
                        currentY = e.clientY - initialY;

                        const dx = Math.abs(e.clientX - initialX);
                        const dy = Math.abs(e.clientY - initialY);

                        if (dx > DRAG_THRESHOLD || dy > DRAG_THRESHOLD) {
                            hasMoved = true;
                        }

                        xOffset = currentX;
                        yOffset = currentY;
                        button.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
                    }
                });

                button.addEventListener('click', (e) => {
                    if (hasMoved) {
                        e.preventDefault();
                        hasMoved = false;
                        return;
                    }

                    e.preventDefault();
                    console.log("Button clicked. Sending solved signal...");
                    window.on_proceed_event();
                    button.textContent = 'Sent!';
                    button.style.backgroundColor = '#4CAF50';
                    button.style.cursor = 'default';
                    setTimeout(() => button.style.display = 'none', 1000);
                }); //

                document.body.appendChild(button);
            })();
        """
        await self._page.evaluate(script)

    async def _remove_signal_button(self) -> None:
        print("Removing signal button...")
        script = """
            const button = document.getElementById('proceed-signal-button');
            if (button) {
                button.remove();
            }
        """
        await self._page.evaluate(script)

