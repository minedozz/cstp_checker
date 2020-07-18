import asyncio

from .input_processor import CmdInputProcessor
from .output_processor import LogErrorsOnlyOutputProcessor
from .worker import Worker


async def main():
    input_processor = CmdInputProcessor()
    input_data = await input_processor.process()

    output_processor = LogErrorsOnlyOutputProcessor(input_data.log_file)

    worker = Worker(input_data, output_processor)
    process_task = asyncio.create_task(worker.process())
    await process_task

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
