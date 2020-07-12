import asyncio

from .input_processor import CmdInputProcessor
from .output_processor import PrintOutputProcessor
from .worker import Worker


async def main():
    input_processor = CmdInputProcessor(user_id_arg_name='user_id',
                                        get_all_user_messages_url_arg_name='get_messages_url',
                                        send_message_url_arg_name='send_message_url',
                                        get_message_detail_url_arg_name='get_message_detail_url')

    input_data = await input_processor.process()
    print(input_data)

    output_processor = PrintOutputProcessor()

    worker = Worker(input_data, output_processor, 5)
    process_task = asyncio.create_task(worker.process())
    await process_task

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
