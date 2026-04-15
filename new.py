from q import DQ
import asyncio
from fmoviez import go_to_fmoviez
from downloads import FMOVIES, get_res_from_list, sort_resolutions
from aiohttp import ClientSession

async def main():
    q = DQ()
    t = q.top()
    print(t)
    show, season, episode, quality, code = t.use()
    url = FMOVIES.format(code, season, episode)
    res_url = await go_to_fmoviez(url)
    print(res_url)
    async with ClientSession() as session:
        resolution = await get_res_from_list(session, res_url)
        res = sort_resolutions(resolution)
    


if __name__ == '__main__':
    asyncio.run(main())


