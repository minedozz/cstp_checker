from pathlib import Path
from datetime import datetime

from .i_output_processor import *


class LogErrorsOnlyOutputProcessor(IOutputProcessor):
    def __init__(self, log_file: Path):
        log_file = log_file.parent / f'{log_file.name}_{datetime.now()}'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.touch(exist_ok=True)

        self._log_file = log_file

    async def process(self, output: OutputData):
        if not output.is_all_ok:
            with self._log_file.open('a', encoding='utf-8') as stream:
                stream.write(f'General result: {output.is_all_ok}\n')
                stream.write('Details: ')

                for detail in output.details:
                    if not detail.is_all_ok:
                        message = [f'\nCheck of {detail.url}',
                                   f'Status: {detail.status.name}',
                                   f'General result: {detail.is_all_ok}',
                                   f'Response code: {detail.response_code}',
                                   f'Error message: {detail.error_message}']
                        missing_args = ', '.join(arg.arg_name for arg in detail.missing_args)
                        message.append(f'Missing args: {missing_args}')

                        message = '\n\t'.join(message)
                        stream.write(f'\t{message}')
                        stream.write('\n\n')
