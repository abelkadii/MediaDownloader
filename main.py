import asyncio
from fmoviez import go_to_fmoviez
from downloads import get_res_from_list, download_video
from utils import *
import aiohttp
from log import setup_logging
import logging
async def download_show(show, structure, resolution=None, resolution_available="max"):
    if resolution:
        resolution = RESOLUTION_MAP.get(resolution.lower())
    if not resolution and resolution_available.lower() not in ["max", "min"]:
        raise Exception("resolution not provided")
    show_url = "https://fmoviesz.to/tv/{}/{}-{}"
    for s, eps, epe in structure:
        for ep in range(eps, epe+1):
            url = show_url.format(show, s, ep)
            name = " ".join(show.split("-")[:-1])
            episode = f"{name} season {s} episode {ep}"
            logging.log("downloading "+episode)
            list_url = await go_to_fmoviez(url)
            logging.log("starting session")
            async with aiohttp.ClientSession() as session:
                logging.log("getting resolutions")
                resolutions = await get_res_from_list(session, list_url)
                sorted_resolutions = sort_resolutions(resolutions)
                logging.log("found: "+" ".join([str(i[0])+"p" for i in sorted_resolutions]))
                if resolution:
                    quality = str(resolution)+"p"
                    download_url = get_res_url(sorted_resolutions, resolution)
                else:
                    quality = str(sorted_resolutions[-1][0] if resolution_available.lower()=="max" else sorted_resolutions[0][0])+"p"
                    download_url = sorted_resolutions[-1][1] if resolution_available.lower()=="max" else sorted_resolutions[0][1]
                title = f"{name} season {s} episode {ep} {quality}.ts"
                await download_video(session, download_url, title)
                            

    

    # go_to_fmoviez

async def main():
    # setup_logging()
    await download_show("lucifer-82nyn", [[5, 10, 10]], "360p", resolution_available="min")


if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()