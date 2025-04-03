import os
import subprocess
from datetime import timezone, datetime
from aiogram.types import FSInputFile

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

    video_path = await get_video_from_flow(start_time, end_time)
    new_video_path = ".".join(video_path.split('.')[:-1] + ['mp4'])

    command = [
        "ffmpeg",
        "-i", video_path,
        "-c:v", "libx264",
        "-c:a", "aac",
        new_video_path
    ]
    subprocess.run(command)

    message = (f"#{keyword}\n\n"
               f"{result['summary']}\n\n"
               f"Tone: {result['tone']}")

    channels = await ChannelRepository.get_channels()
    logger.info(channels)

    video = FSInputFile(path=new_video_path, filename=new_video_path.split('/')[-1])

    for channel in channels:
        logger.info(f"Send video to channel: {channel.title}. Message: {message}")
        await bot.send_video(
            chat_id=channel.channel_id,
            caption=message,
            video=video
        )

    if os.path.exists(video_path):
        os.remove(video_path)

    if os.path.exists(new_video_path):
        os.remove(new_video_path)
