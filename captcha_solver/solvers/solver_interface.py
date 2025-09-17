from abc import ABC, abstractmethod
from playwright.async_api import Frame

# This is the new abstract base class (interface) for all solvers.
class SolverInterface(ABC):
    @abstractmethod
    async def is_present(self, frame: Frame) -> bool:
        """
        Checks if the specific captcha is present within the given frame.
        """
        pass

    @abstractmethod
    async def solve(self, frame: Frame) -> None:
        """
        Performs the actions necessary to solve the captcha.
        """
        pass
