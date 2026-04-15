from tqdm import tqdm
import os
from utils import *
import asyncio
import logging
import aiohttp
import sys
from termcolor import colored
from fmoviez import go_to_fmoviez



async def get_playlist(session, url):
    async with session.get(url) as res:
        text = await res.text()
        playlist_lines = text.split("\n")
        items = []
        start_index = 0
        total_duration = 0
        while playlist_lines[start_index].split(":")[0] != "#EXTINF":
            start_index += 1
        for i in range(start_index, len(playlist_lines), 2):
            if playlist_lines[i] == "#EXT-X-ENDLIST":
                break
            duration = float(playlist_lines[i].split(":")[1].split(",")[0])
            total_duration += duration
            url = playlist_lines[i+1]
            items.append([url, duration])
        return items, total_duration

async def download_playlist(session, playlist, path, bar, log, MAX_CONCURRENT_DOWNLOADS):
    downloads = []
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
    for url, duration in playlist:
        name = url.split("/")[-1]
        downloads.append(asyncio.ensure_future(semaphore_download(semaphore, session, url, os.path.join(path, name), bar=bar, log=log)))
    await asyncio.gather(*downloads)
    


async def semaphore_download(semaphore, *args, **kwargs):
    async with semaphore:
        await download_file(*args, **kwargs)

async def download_file(session, url: str, fname: str, chunk_size=8192, bar=None, log=None, att=0):
    try:
        async with session.get(url) as resp:
            total = int(resp.headers.get('content-length', 0))
            downloaded = 0
            totalSize = 0
            with open(fname, 'wb') as file:
                while True:
                    chunk = await resp.content.read(chunk_size)
                    if not chunk:
                        if total==0 and downloaded<1 and bar:
                            bar.update(1-downloaded)
                        break
                    size = file.write(chunk)
                    totalSize += size
                    if bar:
                        if total>0:
                            amount = size / total
                        else:
                            amount = min((200*1024/chunk_size), 1-downloaded)
                            downloaded= min(downloaded + (200*1024/chunk_size), 1)
                        bar.progress += size
                        update_bar(bar, amount)
            log("Downloaded %s %s"%(fname.split("\\")[-1], totalSize))
        return fname
    except Exception as e:
        if att==10:
            raise e
        await asyncio.sleep(1)
        return await download_file(session, url, fname, chunk_size, bar, log, att+1)


def verify_resume(path, downloaded):
    found = os.listdir(path)
    for file in downloaded:
        if file not in found:
            return False
    return True
        

def verify_download(path, playlist):
    # return True
    with open(playlist, 'r') as pls:
        playlist_items = [i.split(' - ')[0] for i in pls.read().split('\n')[1:]]
    for item in os.listdir(path):
        if item == "_log.txt" or item == "_playlist.m3u8":
                continue
        if item not in playlist_items:
            return False
    return True






def join_playlist(playlist, path, bar):
    assert verify_download(playlist, os.path.join(playlist, '_playlist.m3u8')), "error with downloaded files"
    with open(path, 'wb') as file:
        for item in os.listdir(playlist):
            if item == "_log.txt" or item == "_playlist.m3u8":
                continue
            with open(os.path.join(playlist, item),  'rb') as itemFile:
                size = file.write(itemFile.read())
                bar.progress += size
                update_bar(bar, 1)
        file.close()



async def download_video(session, url, name, code, MAX_CONCURRENT_DOWNLOADS=16, callbacks=[]):
    log = lambda *args: f"{dt_to_string(dt_now())}: " + " ".join([str(a) for a in args]) + "\n"
    tmp = os.path.join(TEMPORARY_PATH, code)
    if not os.path.exists(tmp):
        os.mkdir(tmp)
    resuming = os.path.exists(os.path.join(TEMPORARY_PATH, code, "_log.txt"))
    logg = open(os.path.join(tmp, "_log.txt"), "r").read() if resuming else ""
    end_pending = create_pending_task("getting playlist", "got playlist")
    playlist, total_duration = await get_playlist(session, url)
    downloaded = []
    downloaded_size = 0
    if not os.path.exists(os.path.join(TEMPORARY_PATH, code, "_playlist.m3u8")):
        with open(os.path.join(TEMPORARY_PATH, code, "_playlist.m3u8"), "w") as file:
            file.write(f"{name} - {total_duration}\n")
            for url, duration in playlist:
                file.write(f"{url.split('/')[-1]} - {duration}\n")
    else:
        for line in logg.split("\n"):
            if ":" not in line: continue
            if (msg:=line.split(": ")[1]).split(" ")[0] == "Downloaded":
                downloaded.append(msg.split(" ")[1])
                downloaded_size += int(msg.split(" ")[2])
    await end_pending()
    assert verify_resume(tmp, downloaded), "resuming not verified"
    # print("found %s files in playlist"%len(playlist))
    # print("starting download ...")
    print(colored("downloading %s duration = %s"%(name.split(".")[0], format_time(total_duration)), "blue"))
    originalLen = len(playlist)
    playlist = [[i, j] for i, j in playlist if i.split("/")[-1] not in downloaded]
    already_downloaded = originalLen-len(playlist)
    if already_downloaded: print(f"found {already_downloaded} files already downloaded")
    download_bar = tqdm(total=originalLen, unit="files", unit_scale=True, bar_format="{desc} |{bar}| {postfix}", colour="blue", dynamic_ncols=True, initial=already_downloaded)
    download_bar.__setattr__("progress", downloaded_size)
    download_bar.__setattr__("moving_average", [])
    download_bar.__setattr__("timed_calls", callbacks)
    def log_download(*msg):
        with open(os.path.join(tmp, "_log.txt"), "a") as file:
            file.write(log(*msg))
    if resuming:
        log_download("# Resuming download of", name, "from", url)
    else:
        log_download("# Starting download of", name, "from", url)
    # try: 
    await download_playlist(session, playlist, tmp, download_bar, log_download, MAX_CONCURRENT_DOWNLOADS)
    # except Exception as e:
        # file.write(log("failed to download", e))
        # file.close()
        # download_bar.close()
        # raise e
    size = download_bar.progress - downloaded_size
    elapsed = download_bar.format_dict['elapsed']
    rate = size/elapsed if elapsed else 0
    download_bar.close()
    sys.stdout.write("\r")
    print("took %s to download %s [%s/s]"%(format_time(elapsed), format_data(size), format_data(rate)))
    print("rebuilding ...")
    joinning_bar = tqdm(total=originalLen, unit="files", unit_scale=True, bar_format="{desc} |{bar}| {postfix}", colour="green", dynamic_ncols=True)
    joinning_bar.__setattr__("progress", 0)
    joinning_bar.__setattr__("moving_average", [])
    join_playlist(tmp, os.path.join(BASE_DIR, DOWNLOADS_PATH, name+".ts"), joinning_bar)
    size = joinning_bar.progress
    elapsed = joinning_bar.format_dict['elapsed']
    rate = size/elapsed
    joinning_bar.close()
    print("took %s to rebuild %s [%s/s]"%(format_time(elapsed), format_data(size), format_data(rate)))
    end_pending = create_pending_task("cleaning up", "cleaned up")
    clear_dir(tmp)
    await end_pending()
    await asyncio.sleep(1)
    print(f"successfully downloaded {name} to {os.path.join(BASE_DIR, DOWNLOADS_PATH)}")


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

async def get_and_save_listurl(item, overwrite=True):
    show, season, episode, _, code = item.use()
    cache = episode_code(show, season, episode, "txt") if code.startswith("tv") else dot_string(show)+".txt"    
    if os.path.exists(os.path.join(CACHE_PATH, cache)) and not overwrite:
        return
    url = FMOVIES.format(code, season, episode)
    list_url = await go_to_fmoviez(url)
    with open(os.path.join(CACHE_PATH, cache), 'w') as f:
        f.write(list_url)
        f.close()
    return list_url


async def download_item(item, next=None):
    show, season, episode, quality, code = item.use()
    url = FMOVIES.format(code, season, episode)
    if code.startswith("tv"):
        episodeName = f"{show} Season {season} Episode {episode}"
    else:
        episodeName = show
    print(colored("#"*10+" downloading "+ episodeName, "green"))
    end_pending = create_pending_task("getting download url from fmoviez ...", "got download url from fmoviez")
    # if not 
    cache = episode_code(show, season, episode, "txt") if code.startswith("tv") else dot_string(show)+".txt"    
    async with aiohttp.ClientSession() as session:
        if not os.path.exists(os.path.join(CACHE_PATH, cache)):
            list_url = await get_and_save_listurl(item)
        else:
            with open(os.path.join(CACHE_PATH, cache), 'r') as f:
                list_url = f.read()
        try:
            resolutions = await get_res_from_list(session, list_url)
        except:
            list_url = await get_and_save_listurl(item)
            resolutions = await get_res_from_list(session, list_url)
            
        sorted_resolutions = sort_resolutions(resolutions)
        download_url = None
        if quality.lower() in RESOLUTION_MAP:
            resolution = RESOLUTION_MAP.get(quality.lower())
            download_url = get_res_url(sorted_resolutions, resolution)
        # elif quality.lower() in ["min", "max"]:
        if not download_url:
            # quality = str(sorted_resolutions[-1][0] if quality.lower()=="max" else sorted_resolutions[0][0])+"p"
            # download_url = sorted_resolutions[-1][1] if quality.lower()=="max" else sorted_resolutions[0][1]
            quality = str(sorted_resolutions[-1][0])+"p"
            download_url = sorted_resolutions[-1][1]
        # else:
        #     raise Exception("Invalid quality", quality)
        # if not download_url:
        #     raise Exception("No download url found for", quality, "available resolutions are", " ".join([str(i[0])+"p" for i in sorted_resolutions]))
        code = episode_code(show, season, episode, quality) if code.startswith("tv") else dot_string(show)+"."+quality
        await end_pending()
        async def callback(att=0):
            if not next:
                return
            try:
                await get_and_save_listurl(next,  overwrite=False)
            except:
                if att==5:
                    return
                await asyncio.sleep(.2)
                await callback(att+1)

        await download_video(session, download_url, episodeName, code, MAX_CONCURRENT_DOWNLOADS=16, callbacks=[(callback, 70)])



