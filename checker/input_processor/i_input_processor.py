from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass(frozen=True)
class PreparedInputData:
    user_id: str
    delay: float

    get_all_user_messages_url: str
    send_message_url: str
    get_message_detail_url: str
    delete_message_url: str

    get_all_user_messages_resp_req_args: tuple
    send_message_resp_req_args: tuple
    get_message_detail_resp_req_args: tuple

    log_file: Path


class IInputProcessor(ABC):
    @abstractmethod
    async def process(self) -> PreparedInputData:
        pass



