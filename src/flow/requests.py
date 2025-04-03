import aiofiles
import aiohttp

from src.config import settings
from src.flow import REQUEST_URL


async def get_video_from_flow(start_time: int, end_time: int) -> str:
    dur = end_time - start_time
    ENDPOINT = REQUEST_URL + f'/archive-{start_time}-{end_time - start_time}.ts?token={settings.TOKEN}'
    save_path = f"{start_time}-{dur}.ts"

    async with aiohttp.ClientSession() as session:
        async with session.get(ENDPOINT) as response:
            response.raise_for_status()
            async with aiofiles.open(save_path, "wb") as f:
                while chunk := await response.content.read(1024 * 1024):
                    await f.write(chunk)

    return save_path
