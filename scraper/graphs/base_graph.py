from abc import ABC, abstractmethod
from typing import Optional


class GraphInterface(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs) -> Optional[str]:
        pass
