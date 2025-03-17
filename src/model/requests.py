import aiohttp

from src.model import EMAIL_MODEL, PASSWORD_MODEL, MODEL_URL

TOKEN = None


async def get_token():
    global TOKEN
    ENDPOINT = MODEL_URL + '/api/v1/auths/signin'

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'email': EMAIL_MODEL,
        'password': PASSWORD_MODEL
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(ENDPOINT, headers=headers, json=data) as response:
            response.raise_for_status()
            TOKEN = (await response.json())['token']

    return TOKEN


async def get_models():
    global TOKEN
    ENDPOINT = MODEL_URL + '/api/models'

    if TOKEN is None:
        TOKEN = await get_token()

    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(ENDPOINT, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()

    return [model['name'] for model in data['data']]


async def chat_completions(model, content, role="user"):
    global TOKEN
    ENDPOINT = MODEL_URL + '/api/chat/completions'

    if TOKEN is None:
        TOKEN = await get_token()

    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }

    data = {
        "model": model,
        "messages": [
            {
                "role": role,
                "content": content
            }
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(ENDPOINT, headers=headers, json=data) as response:
            response.raise_for_status()
            result = await response.json()

    return result['choices'][0]['message']['content']
