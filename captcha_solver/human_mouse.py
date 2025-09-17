import math
import random
from playwright.sync_api import Mouse

class HumanMouse:
    def __init__(self, mouse: Mouse):
        self.cursor_last_position = [0, 0]
        self.mouse = mouse

    async def move_to(self, target_x: float, target_y: float) -> None:
        curr_x, curr_y = self.cursor_last_position
        
        steps = random.randint(15, 30)
        
        control_x = (curr_x + target_x) / 2 + random.randint(-50, 50)
        control_y = (curr_y + target_y) / 2 + random.randint(-50, 50)
        
        print(f"Moving from ({curr_x:.2f}, {curr_y:.2f}) "
             f"to ({target_x:.2f}, {target_y:.2f}) in {steps} steps.")

        for i in range(1, steps + 1):
            t = i / steps
            curr_x, curr_y = self.cursor_last_position

            # Use a quadratic Bezier curve formula to calculate each step
            # P(t) = (1 - t) ^ 2 * P0 + 2t(1 - t)P1 + t ^ 2 * P2
            x = (1 - t) ** 2 * curr_x + 2 * t * (1 - t) * control_x + t ** 2 * target_x
            y = (1 - t) ** 2 * curr_y + 2 * t * (1 - t) * control_y + t ** 2 * target_y

            jitter_x = random.uniform(-2.0, 2.0)
            jitter_y = random.uniform(-2.0, 2.0)

            if i == steps:
                await self.mouse.move(target_x, target_y)
                self.cursor_last_position = [target_x, target_y]

            else:
                await self.mouse.move(x + jitter_x, y + jitter_y)
                self.cursor_last_position = [x + jitter_x, y + jitter_y]

            await asyncio.sleep(0.01)

    async def click_at(self, target_x: float, target_y: float) -> None:
        await self.move_to(target_x, target_y)
        await self.mouse.click(target_x, target_y)

        print("Mouse clicked.")
