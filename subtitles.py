import asyncio
import aiohttp


SUBTITLE_URL = "https://fmoviesz.to/ajax/episode/subtitles/{}"


async def get_subtitles(session, id):
    async with session.get(SUBTITLE_URL.format(id)) as resp:
        return await resp.json()

async def download_subtitles(session, id, path, name, languages="*"):
    subtitles = await get_subtitles(session, id)
    langs = languages.split(" ") if languages != "*" else subtitles.keys()
    for language, url in subtitles.items():
        if  language not in langs:
            continue
        "Lucifer_S1E04_.vtt"
        async with session.get(url) as resp:
            with open(path+language+".vtt", "wb") as file:
                file.write(await resp.read())

        