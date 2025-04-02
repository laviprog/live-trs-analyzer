from datetime import timezone, datetime

from aiogram.types import BufferedInputFile

from src.database.repositories import ChannelRepository
from src.flow.requests import get_video_from_flow


async def send(result: dict[str, str], keyword: str):
    from src.bot import bot
    from src.bot import logger

    def to_seconds(s: str) -> int:
        start_of_today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_since_epoch = int(start_of_today.timestamp())
        times = s.split(':')
        return int(times[0]) * 3600 + int(times[1]) * 60 + int(times[2]) + seconds_since_epoch

    start_time, end_time = map(to_seconds, result['time_range'].split('–'))

    # video = await get_video_from_flow(start_time, end_time, f"{start_time}-{end_time}.mp4")

    message = (f"#{keyword}\n\n"
               f"{result['summary']}\n\n"
               f"Tone: {result['tone']}")

    channels = await ChannelRepository.get_channels()
    logger.info(channels)

    for channel in channels:
        await bot.send_message(channel, message)

    # with open(video, 'rb') as v:
    #     video_data = v.read()
    #     for channel in channels:
    #         await bot.send_video(
    #             chat_id=channel.channel_id,
    #             caption=message,
    #             video=BufferedInputFile(video_data, filename=video)
    #         )
