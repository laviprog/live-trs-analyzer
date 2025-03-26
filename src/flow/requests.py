import aiohttp

from src.flow import REQUEST_URL


async def get_video_from_flow(start_time: int, end_time: int, save_path: str):
    ENDPOINT = REQUEST_URL + f'?start_time={start_time}&end_time={end_time}'

    headers = {
        'Content-Type': 'multipart/form-data'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(ENDPOINT, headers=headers) as response:
            response.raise_for_status()
            with open(save_path, 'wb') as f:
                while chunk := await response.content.read(1024 * 1024):
                    f.write(chunk)

    return save_path