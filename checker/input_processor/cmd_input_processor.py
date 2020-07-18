import argparse
from pathlib import Path

from .i_input_processor import *


class CmdInputProcessor(IInputProcessor):
    def __init__(self):

        self._user_id_arg_name = 'user_id'
        self._delay_arg_name = 'delay'

        self._get_all_user_messages_url_arg_name = 'get_messages_url'
        self._get_all_user_messages_req_args_arg_name = 'get_messages_resp_args'

        self._send_message_url_arg_name = 'send_message_url'
        self._send_message_resp_req_arg_names_arg_name = 'send_message_resp_args'

        self._get_message_detail_url_arg_name = 'get_message_detail_url'
        self._get_message_detail_resp_req_arg_names_arg_name = 'get_message_detail_resp_args'

        self._delete_message_url_arg_name = 'delete_message_url'

        self._log_file_arg_name = 'log_file_path'

    async def process(self) -> PreparedInputData:
        parser = argparse.ArgumentParser()
        parser.add_argument(self._arg_name_as_raw(self._user_id_arg_name),
                            help='Test user id', type=str, required=True)

        parser.add_argument(self._arg_name_as_raw(self._delay_arg_name),
                            help='Delay between queries in seconds', type=float, required=True)

        parser.add_argument(self._arg_name_as_raw(self._get_all_user_messages_url_arg_name),
                            help='Get all messages url', type=str, required=True)
        parser.add_argument(self._arg_name_as_raw(self._get_all_user_messages_req_args_arg_name),
                            help='Get all messages response req args', type=str, nargs='+', default=tuple())

        parser.add_argument(self._arg_name_as_raw(self._send_message_url_arg_name),
                            help='Send message url', type=str, required=True)
        parser.add_argument(self._arg_name_as_raw(self._send_message_resp_req_arg_names_arg_name),
                            help='Send message response req args', type=str, nargs='+', default=tuple())

        parser.add_argument(self._arg_name_as_raw(self._get_message_detail_url_arg_name),
                            help='Get message detail url', type=str, required=True)
        parser.add_argument(self._arg_name_as_raw(self._get_message_detail_resp_req_arg_names_arg_name),
                            help='Get message response req args', type=str, nargs='+', default=tuple())

        parser.add_argument(self._arg_name_as_raw(self._delete_message_url_arg_name),
                            help='Delete message url', type=str, required=True)

        parser.add_argument(self._arg_name_as_raw(self._log_file_arg_name),
                            help='Log file path', type=Path, required=True)

        args = parser.parse_args()

        get_all_user_messages_resp_req_args = tuple(getattr(args, self._get_all_user_messages_req_args_arg_name))
        send_message_resp_req_args = tuple(getattr(args, self._send_message_resp_req_arg_names_arg_name))
        get_message_detail_resp_req_args = tuple(getattr(args, self._get_message_detail_resp_req_arg_names_arg_name))

        result = PreparedInputData(user_id=getattr(args, self._user_id_arg_name),

                                   delay=getattr(args, self._delay_arg_name),

                                   get_all_user_messages_url=getattr(args, self._get_all_user_messages_url_arg_name),
                                   send_message_url=getattr(args, self._send_message_url_arg_name),
                                   get_message_detail_url=getattr(args, self._get_message_detail_url_arg_name),
                                   delete_message_url=getattr(args, self._delete_message_url_arg_name),

                                   get_all_user_messages_resp_req_args=get_all_user_messages_resp_req_args,
                                   send_message_resp_req_args=send_message_resp_req_args,
                                   get_message_detail_resp_req_args=get_message_detail_resp_req_args,

                                   log_file=getattr(args, self._log_file_arg_name))
        return result

    @staticmethod
    def _arg_name_as_raw(arg_name):
        return f'--{arg_name}'


