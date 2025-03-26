from aiogram.enums import ParseMode

from src.database.repositories import ChannelRepository


async def send(message):
    from src.bot import bot
    from src.bot import logger

    channels = await ChannelRepository.get_channels()
    logger.info(channels)

    for channel in channels:
        await bot.send_message(channel.channel_id, message)
