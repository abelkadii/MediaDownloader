from tqdm import tqdm
import os
from utils import *
import asyncio
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_PATH = os.path.join(BASE_DIR, "downloads/")
TEMPORARY_PATH = os.path.join(BASE_DIR, ".tmp/")

async def get_playlist(session, url):
    async with session.get(url) as res:
    # res = requests.get(url)
        text = await res.text()
        playlist_lines = text.split("\n")
        items = []
        for line in playlist_lines:
            if line and line[0]!="#":
                items.append(line)
        return items

async def download_playlist(session, playlist, path, bar, MAX_CONCURRENT_DOWNLOADS):
    downloads = []
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
    for url in playlist:
        name = url.split("/")[-1]
        downloads.append(asyncio.ensure_future(semaphore_download(semaphore, session, url, os.path.join(path, name), bar=bar)))
    await asyncio.gather(*downloads)
    


async def semaphore_download(semaphore, *args, **kwargs):
    async with semaphore:
        await download_file(*args, **kwargs)

async def download_file(session, url: str, fname: str, chunk_size=1024, bar=None):
    async with session.get(url) as resp:
        total = int(resp.headers.get('content-length', 0))
        with open(fname, 'wb') as file:
            while True:
                chunk = await resp.content.read(chunk_size)
                if not chunk:
                    break
                size = file.write(chunk)
                if bar:
                    bar.update(size / total)
    return fname

def join_playlist(playlist, path, bar):
    with open(path, 'wb') as output:
        for item in os.listdir(playlist):
            with open(os.path.join(playlist, item),  'rb') as itemFile:
                output.write(itemFile.read())
                bar.update(1)
        output.close()

async def download_video(session, url, name, MAX_CONCURRENT_DOWNLOADS=16):
    if not os.path.exists(TEMPORARY_PATH):
        os.mkdir(TEMPORARY_PATH)
    tmp = create_dir_from_name(TEMPORARY_PATH, name)
    logging.log("getting playlist")
    playlist = await get_playlist(session, url)
    logging.log("found %s files in playlist"%len(playlist))
    logging.log("starting download ...")
    download_bar = tqdm(desc=f"downloading {name}", total=len(playlist),unit='files')
    await download_playlist(session, playlist, tmp, download_bar, MAX_CONCURRENT_DOWNLOADS)
    logging.log("downloaded %s files successfully"%len(playlist))
    description = f"joining {len(playlist)} files"
    joinning_bar = tqdm(desc=description, total=len(playlist),unit='files')
    join_playlist(tmp, os.path.join(BASE_DIR, DOWNLOADS_PATH, name), joinning_bar)
    logging.log("finalizing ...")
    await asyncio.sleep(1)
    logging.log(f"successfully downloaded {name} to {os.path.join(BASE_DIR, DOWNLOADS_PATH)}")


def getInfo(line):
    line = line.split(":")[1]
    line = line.split(",")
    res = {}
    for l in line:
        key, value = l.split("=")
        res[key] = value
    return res


async def get_res_from_list(session, url):
    async with session.get(url) as response:
        text = await response.text()
        playlist_lines = text.split("\n")
        if ":" not in playlist_lines[0]:
            playlist_lines = playlist_lines[1:]
        if playlist_lines[-1] == "":
            playlist_lines = playlist_lines[:-1]
        res = {}
        parts = split_array(url.split("/"), "h")
        base = '/'.join(parts[0]+["h", ""])
        for i in range(0, len(playlist_lines), 2):
            info = getInfo(playlist_lines[i])
            url = playlist_lines[i+1]
            res[info['RESOLUTION']] =base + url
        return res
