import json
import aiohttp
import asyncio
from typing import Tuple, Optional

from ..input_processor import PreparedInputData
from ..output_processor import OutputData, IOutputProcessor, CheckResult


class Worker:
    def __init__(self, input_data: PreparedInputData, output_processor: IOutputProcessor, delay: float):
        self._input_data = input_data
        self._output_processor = output_processor
        self._delay = delay

    async def process(self):
        while True:
            result = await self._work()
            await self._output_processor.process(result)
            await asyncio.sleep(self._delay)

    async def _work(self) -> OutputData:
        async with aiohttp.ClientSession() as session:
            get_all_messages_result = await self._check_get_all_user_messages(session)
            message_id, send_message_result = await self._check_send_message(session)
            if message_id:
                get_message_result = await self._check_get_message(session, message_id)
            else:
                get_message_result = CheckResult(self._input_data.get_message_detail_url, False, 'Не запускалась')

        results = get_all_messages_result, send_message_result, get_message_result
        return OutputData(details=results)

    async def _check_get_all_user_messages(self, session: aiohttp.ClientSession) -> CheckResult:
        async with session.get(self._input_data.get_all_user_messages_url,
                               params={'userExtId': self._input_data.user_id}) as response:
            if response.status == 200:
                return CheckResult(url=self._input_data.get_all_user_messages_url, is_ok=True, reason='')
            else:
                return CheckResult(url=self._input_data.get_all_user_messages_url,
                                   is_ok=False,
                                   reason=await response.text())

    async def _check_send_message(self, session: aiohttp.ClientSession) -> Tuple[Optional[str], CheckResult]:
        request = {
            "foreignData": {
                "subject": 'Test subject',
                "content": 'Test message',
                "submissionMethod": "VIS",
                "userInfo": {
                    'fio': 'Test fio',
                    'email': 'Test email',
                    'externalId': self._input_data.user_id
                }
            }
        }
        async with session.post(self._input_data.send_message_url, json=request, headers={'charset': 'UTF-8'}) as resp:
            if resp.status == 200:
                answer = await resp.text()
                created_message_id = '1'  # TODO:  answer['id']
                return created_message_id, CheckResult(url=self._input_data.send_message_url, is_ok=True, reason='')
            else:
                return None, CheckResult(url=self._input_data.send_message_url,
                                         is_ok=False,
                                         reason=await resp.text())

    async def _check_get_message(self, session: aiohttp.ClientSession, message_id: str) -> CheckResult:
        async with session.get(self._input_data.get_message_detail_url, params={'number': message_id}) as resp:
            if resp.status == 200:
                return CheckResult(url=self._input_data.get_message_detail_url, is_ok=True, reason='')
            else:
                return CheckResult(url=self._input_data.get_message_detail_url,
                                   is_ok=False,
                                   reason=await resp.text())


