from typing import Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CheckResult:
    url: str
    is_ok: bool
    reason: str = field(default='')


@dataclass(frozen=True)
class OutputData:
    details: Tuple[CheckResult]

    @property
    def is_all_ok(self):
        return all(item.is_ok for item in self.details)


class IOutputProcessor(ABC):
    @abstractmethod
    async def process(self, output: OutputData):
        pass

