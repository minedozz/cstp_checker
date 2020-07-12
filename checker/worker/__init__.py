import json
import aiohttp
import asyncio
from typing import Tuple, Optional, Union
from itertools import groupby
from operator import attrgetter

from ..input_processor import PreparedInputData
from ..output_processor import OutputData, IOutputProcessor, ApiMethodCheckResult, ArgCheckResult, Status


class Worker:
    def __init__(self, input_data: PreparedInputData, output_processor: IOutputProcessor):
        self._input_data = input_data
        self._output_processor = output_processor

        self._id_to_remove = None

    async def process(self):
        while True:
            result = await self._work()
            await self._output_processor.process(result)
            self._id_to_remove = None
            await asyncio.sleep(self._input_data.delay)

    async def _work(self) -> OutputData:
        async with aiohttp.ClientSession() as session:
            try:
                results = [await self._check_get_all_user_messages(session)]

                message_id, send_message_result = await self._check_send_message(session)
                results.append(send_message_result)
                if message_id:
                    results.append(await self._check_get_message(session, message_id))
                else:
                    results.append(ApiMethodCheckResult(self._input_data.get_message_detail_url,
                                                        status=Status.NOT_CALLED))
                if self._id_to_remove:
                    async with session.delete(f'{self._input_data.delete_message_url}/{self._id_to_remove}') as resp:
                        assert resp.status == 204 or resp.status == 200

            except aiohttp.ClientConnectionError:
                return OutputData(status=Status.UNREACHABLE, details=tuple())
            else:
                return OutputData(status=Status.REACHABLE, details=tuple(results))

    async def _check_get_all_user_messages(self, session: aiohttp.ClientSession) -> ApiMethodCheckResult:
        async with session.get(self._input_data.get_all_user_messages_url,
                               params={'userExtId': self._input_data.user_id}) as response:
            if response.status == 200:
                try:
                    resp = await response.json()
                except json.JSONDecodeError:
                    return ApiMethodCheckResult(url=self._input_data.get_all_user_messages_url,
                                                status=Status.RESPONSE_DECODE_ERROR)
                else:
                    args_check_results = _check_arg_existing(resp, self._input_data.get_all_user_messages_resp_req_args)
                    return ApiMethodCheckResult(url=self._input_data.get_all_user_messages_url,
                                                status=Status.REACHABLE,
                                                response_code=200,
                                                args_checks=args_check_results)
            else:
                return ApiMethodCheckResult(url=self._input_data.get_all_user_messages_url,
                                            status=Status.REACHABLE,
                                            response_code=response.status,
                                            args_checks=tuple(),
                                            error_message=await response.text())

    async def _check_send_message(self, session: aiohttp.ClientSession) -> Tuple[Optional[str], ApiMethodCheckResult]:
        request = {
            "foreignData": {
                "subject": 'TEST SUBJECT',
                "content": 'TEST CONTENT',
                "submissionMethod": "VIS",
                "userInfo": {
                    'fio': 'TEST_FIO',
                    'email': 'TEST_EMAIL@mail.ru',
                    'externalId': self._input_data.user_id
                }
            }
        }
        async with session.post(self._input_data.send_message_url, json=request, headers={'charset': 'UTF-8'}) as resp:
            if resp.status == 200:
                try:
                    resp = await resp.json()
                except json.JSONDecodeError:
                    result = ApiMethodCheckResult(url=self._input_data.get_all_user_messages_url,
                                                  status=Status.RESPONSE_DECODE_ERROR)
                    return None, result
                else:
                    args_check_results = _check_arg_existing(resp, self._input_data.send_message_resp_req_args)
                    if all((item.is_exist for item in args_check_results)):
                        new_message_id = resp['response']['data']['caseNumber']
                    else:
                        new_message_id = None
                    result = ApiMethodCheckResult(url=self._input_data.get_all_user_messages_url,
                                                  status=Status.REACHABLE,
                                                  response_code=200,
                                                  args_checks=args_check_results)
                    return new_message_id, result
            else:
                result = ApiMethodCheckResult(url=self._input_data.get_all_user_messages_url,
                                              status=Status.REACHABLE,
                                              response_code=resp.status,
                                              args_checks=tuple(),
                                              error_message=await resp.text())
                return None, result

    async def _check_get_message(self, session: aiohttp.ClientSession, message_id: str) -> ApiMethodCheckResult:
        async with session.get(self._input_data.get_message_detail_url, params={'number': message_id}) as resp:
            if resp.status == 200:
                try:
                    resp = await resp.json()
                except json.JSONDecodeError:
                    result = ApiMethodCheckResult(url=self._input_data.get_message_detail_url,
                                                  status=Status.RESPONSE_DECODE_ERROR)
                    return result
                else:
                    args_check_results = _check_arg_existing(resp, self._input_data.get_message_detail_resp_req_args)
                    result = ApiMethodCheckResult(url=self._input_data.get_message_detail_url,
                                                  status=Status.REACHABLE,
                                                  response_code=200,
                                                  args_checks=args_check_results)
                    self._id_to_remove = resp['id']
                    return result
            else:
                result = ApiMethodCheckResult(url=self._input_data.get_message_detail_url,
                                              status=Status.REACHABLE,
                                              response_code=resp.status,
                                              args_checks=tuple(),
                                              error_message=await resp.text())
                return result


def _check_arg_existing(resp, req_args):
    args_check_results = []
    for arg in req_args:
        args_check_results.extend(_is_arg_exists(resp, arg))

    merged_args_check_results = []
    for k, group in groupby(sorted(args_check_results, key=attrgetter('arg_name')), key=attrgetter('arg_name')):
        is_all_ok = all(item.is_exist for item in group)
        merged_args_check_results.append(ArgCheckResult(k, is_exist=is_all_ok))
    merged_args_check_results = tuple(merged_args_check_results)
    return merged_args_check_results


def _is_arg_exists(data: Union[dict, list], arg_name):
    yield from _rec(data, path=[], name_parts=arg_name.split('.'))


def _rec(data: Union[dict, list], path, name_parts):
    arg_name, name_parts = name_parts[0], name_parts[1:]
    full_name = '.'.join(path + [arg_name])
    current_path = path + [arg_name]

    if isinstance(data, dict):
        result = True if arg_name in data else False
        yield ArgCheckResult(full_name, result)
        if result and name_parts:
            yield from _rec(data[arg_name], current_path, name_parts)

    elif isinstance(data, list):
        result = all(arg_name in item for item in data)
        yield ArgCheckResult(full_name, result)
        if result and name_parts:
            for item in data:
                yield from _rec(item, current_path, name_parts)
