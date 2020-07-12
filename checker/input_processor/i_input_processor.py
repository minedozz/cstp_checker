from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass(frozen=True)
class PreparedInputData:
    user_id: str

    get_all_user_messages_url: str
    send_message_url: str
    get_message_detail_url: str


class IInputProcessor(ABC):
    @abstractmethod
    async def process(self) -> PreparedInputData:
        pass



