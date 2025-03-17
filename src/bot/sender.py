from src.bot import bot
from src.database.repositories import ChannelRepository


# this func will send the message to channels
# TODO add the message to send as an argument
async def send():
    channels = await ChannelRepository.get_channels()

    for channel in channels:
        await bot.send_message(channel.channel_id, "Hello, world!")
