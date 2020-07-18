from pathlib import Path

from .i_output_processor import *

url: str
status: Status

response_code: int = -1
args_checks: Tuple[ArgCheckResult] = tuple()
error_message: str = field(default='')


class LogErrorsOnlyOutputProcessor(IOutputProcessor):
    def __init__(self, log_file: Path):
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.touch(exist_ok=True)

        self._log_file = log_file

    async def process(self, output: OutputData):
        if not output.is_all_ok:
            with self._log_file.open(encoding='utf-8') as stream:
                stream.write(f'General result {output.is_all_ok}')
                stream.write('Details:')

                for detail in output.details:
                    if not detail.is_all_ok:
                        message = [f'Check of {detail.url}',
                                   f'General result: {detail.is_all_ok}',
                                   f'Response code: {detail.response_code}',
                                   f'Error message: {detail.error_message}']
                        missing_args = '\n'.join(arg.arg_name for arg in detail.missing_args)
                        message.append(f'Missing args: {missing_args}')

                        message = '\n'.join(message)
                        stream.write(message)
                        stream.write('\n')
