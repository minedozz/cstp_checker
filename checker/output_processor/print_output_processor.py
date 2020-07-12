from .i_output_processor import *


class PrintOutputProcessor(IOutputProcessor):
    async def process(self, output: OutputData):
        print(output.status, output.is_all_ok)
        for item in output.details:
            print(item)
        print()

