from .i_output_processor import *


class PrintOutputProcessor(IOutputProcessor):
    async def process(self, output: OutputData):
        print(self, output)

