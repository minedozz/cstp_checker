from typing import Tuple, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, unique


@dataclass(frozen=True)
class ArgCheckResult:
    arg_name: str
    is_exist: bool


@unique
class Status(Enum):
    UNREACHABLE = 0
    REACHABLE = 1
    NOT_CALLED = 2
    RESPONSE_DECODE_ERROR = 3


@dataclass(frozen=True)
class ApiMethodCheckResult:
    url: str
    status: Status

    response_code: int = -1
    args_checks: Tuple[ArgCheckResult] = tuple()
    error_message: str = field(default='')

    @property
    def is_all_ok(self):
        return (self.status == Status.REACHABLE
                and self.response_code == 200
                and all(check.is_exist for check in self.args_checks))


@dataclass(frozen=True)
class OutputData:
    status: Status
    details: Tuple[ApiMethodCheckResult]

    @property
    def is_all_ok(self):
        return self.status == Status.REACHABLE and all(item.is_all_ok for item in self.details)


class IOutputProcessor(ABC):
    @abstractmethod
    async def process(self, output: OutputData):
        pass

