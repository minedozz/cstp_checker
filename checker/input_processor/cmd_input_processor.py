import argparse

from .i_input_processor import *


class CmdInputProcessor(IInputProcessor):
    def __init__(self, user_id_arg_name: str, get_all_user_messages_url_arg_name: str,
                 send_message_url_arg_name: str, get_message_detail_url_arg_name):

        self._user_id_arg_name = user_id_arg_name
        self._get_all_user_messages_url_arg_name = get_all_user_messages_url_arg_name
        self._send_message_url_arg_name = send_message_url_arg_name
        self._get_message_detail_url_arg_name = get_message_detail_url_arg_name

    async def process(self) -> PreparedInputData:
        parser = argparse.ArgumentParser()
        parser.add_argument(self._arg_name_as_raw(self._user_id_arg_name),
                            help='Test user id', type=str)
        parser.add_argument(self._arg_name_as_raw(self._get_all_user_messages_url_arg_name),
                            help='Get all messages url', type=str)
        parser.add_argument(self._arg_name_as_raw(self._send_message_url_arg_name),
                            help='Send message url', type=str)
        parser.add_argument(self._arg_name_as_raw(self._get_message_detail_url_arg_name),
                            help='Get message detail url', type=str)
        args = parser.parse_args()

        result = PreparedInputData(user_id=getattr(args, self._user_id_arg_name),
                                   get_all_user_messages_url=getattr(args, self._get_all_user_messages_url_arg_name),
                                   send_message_url=getattr(args, self._send_message_url_arg_name),
                                   get_message_detail_url=getattr(args, self._get_message_detail_url_arg_name))
        return result

    @staticmethod
    def _arg_name_as_raw(arg_name):
        return f'--{arg_name}'


