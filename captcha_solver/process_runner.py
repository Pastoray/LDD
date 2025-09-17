import asyncio
from .manual_fallback_handler import ManualFallbackHandler

class ProcessRunner:
    def __init__(self, manual_fallback_handler: ManualFallbackHandler):
        self._manual_fallback_handler = manual_fallback_handler

    # func is a lambda wrapping the actual function call
    # so we no longer need to pass *args, **kwargs explicitely
    async def run_with_fallback(self, func) -> any:
        try:
            res = await func()
            return res

        except Exception as e:
            print(f"Selector timed out or another error occurred: {e}")
            print("Falling back to manual solution...")
            try:
                await self._manual_fallback_handler.handle_fallback()
                res = await func()
                return res

            except Exception as e:
                print(f"Manual fallback failed with error: {e}, giving up...")
                raise

        # Unreachable
