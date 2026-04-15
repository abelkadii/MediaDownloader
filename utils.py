import os
import random
from termcolor import colored
import sys
import asyncio
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DOWNLOADS_PATH = os.path.join(BASE_DIR, "downloads/")
DOWNLOADS_PATH = "d:\\series"
TEMPORARY_PATH = os.path.join(BASE_DIR, ".tmp/")
CACHE_PATH = os.path.join(BASE_DIR, "cache/")
FMOVIES = "https://fmoviesz.to/{}/{}-{}"
MA_WINDOW = 8192
RESOLUTION_MAP = {
    "sd": 360,
    "fsd": 480,
    "hd": 720,
    "fhd": 1080,
    "qhd": 1440,
    "uhd": 2160,
    "360p": 360,
    "480p": 480,
    "720p": 720,
    "1080p": 1080,
    "1440p": 1440,
    "2160p": 2160,
    "2k": 1440,
    "4k": 2160,
}

def pad_left(string, length, char):
    return char*(length-len(string))+string

def pad_right(string, length, char):
    return string+char*(length-len(string))

def capitalize(string):
    return string[0].upper()+string[1:].lower()


def generate_random_name():
    name = ""
    BASE = "0123456789abcdef"
    for i in range(16):
        name += BASE[random.randint(0, len(BASE) - 1)]
    return name

def generate_name(path, ext):
    while True:
        name = generate_random_name()+ext
        if not os.path.exists(os.path.join(path, name)):
            return name

def create_dir_from_name(path, name):
    name_without_ext = ".".join(name.split(".")[:-1])
    dir_base_name = name_without_ext.replace(" ", "_")
    if not os.path.exists(os.path.join(path, dir_base_name)):
        os.mkdir(os.path.join(path, dir_base_name))
        return os.path.join(path, dir_base_name)
    i = 2
    while os.path.exists((pth:=os.path.join(path, dir_base_name+"_"+str(i)))):
        i+=1
    os.mkdir(pth)
    return pth

def split_array(arr, sp):
    parts = []
    cur = []
    for i in range(len(arr)):
        if arr[i] == sp:
            parts.append(cur)
            cur = []
        else:
            cur.append(arr[i])
    if cur: parts.append(cur)
    return parts

def sort_resolutions(resolutions):
    res = []
    for r in resolutions:
        key = int(r.split("x")[1])
        res.append((key, resolutions[r]))
    return sorted(res, key=lambda key: key[0])

def get_res_url(resolutions, res):
    for r, url in resolutions:
        if r==res:
            return url
    return None

def format_time(t_in_s):
    weeks = int(t_in_s/604800)
    days = int(t_in_s/86400)%7
    hours = int(t_in_s/3600)%24
    minutes = int((t_in_s/60))%60
    seconds = int(t_in_s%60)
    units = ["w", "d", "h", "m", "s"]
    values = [weeks, days, hours, minutes, seconds]
    output = ""
    for i in range(len(units)):
        if values[i]>0:
            output += pad_left(str(values[i]), 2, " ")+units[i]
            if i < len(units)-1:
                output += " " + pad_left(str(values[i+1]), 2, " ")+units[i+1]
            break
    return output or "0s"

def format_data(in_bytes):
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while in_bytes > 1000:
        in_bytes /= 1024
        i += 1
    string = str(in_bytes)
    len_int = len(string.split(".")[0])
    rounding = {3:0, 2:1, 1:2, 0:2}[len_int]
    if rounding == 0:
        size = int(in_bytes)
    else:
        size = round(in_bytes, rounding)
    return f"{size} {units[i]}"


def update_bar(bar, amount):
    total = bar.format_dict.get("total")
    downloaded = bar.format_dict.get("n")
    bar.update(min(amount, total-downloaded))
    rate = bar.format_dict.get("rate")
    downloaded = bar.format_dict.get("n")
    elapsed = int(bar.format_dict.get("elapsed"))
    
    if rate: bar.moving_average.append(rate)
    if len(bar.moving_average) > MA_WINDOW:
        bar.moving_average.pop(0)

    MA = sum(bar.moving_average) / len(bar.moving_average) if rate else "NAN"
    # WMA = (sum(rate * weight for rate, weight in zip(bar.moving_average, range(1, len(bar.moving_average) + 1))) / (len(bar.moving_average)*(len(bar.moving_average)+1)/2)) if rate else "NAN"
    URATE = MA

    dara_rate = URATE*bar.progress/downloaded if rate else "NAN"
    remaining = format_time((total - downloaded)/URATE) if rate else "TBD"
    for i, (cb, tm) in enumerate(getattr(bar, 'timed_calls', [])):
        if rate and tm>downloaded/total*100:
            setattr(bar, 'timed_calls', [[cb, tm] for j, (cb, tm) in enumerate(getattr(bar, 'timed_calls')) if i!=j])
            asyncio.create_task(cb())
    
    percentage = str(round(downloaded/total*100, 1)) + "%"
    formated_dara_rate = pad_left(format_data(dara_rate) if rate else "NAN", 7, " ")
    downloaded_size = pad_left(format_data(bar.progress), 7, " ")
    formated_elapsed = format_time(elapsed)

    bar.set_description(f"{formated_elapsed} ETA {remaining}")
    bar.set_postfix_str(f"{percentage} {downloaded_size} [{formated_dara_rate}/s]")


def log(output):
    sys.stdout.write("\r"+output+" "*5)
    sys.stdout.flush()
    

async def hold(future, message, success="done", fail="failed"):
    maximum = max(len(message), len(success), len(fail))+10
    i=0
    while not future.done():
        i+=1
        states = ["\\", "|", "/", "-"]
        log(pad_right(message+" "+colored(states[i%4], "grey"), maximum, " "))
        await asyncio.sleep(.01)
    state = future.result()
    if state:
        log(pad_right(success+" "+colored("✓", "green"), maximum, " "))
    else:
        log(pad_right(fail+" "+colored("✗", "red"), maximum, " "))
    print()


def create_pending_task(message, success="done", fail="failed"):
    future = asyncio.Future()
    asyncio.ensure_future(hold(future, message, success, fail))
    async def end():
        future.set_result(True)
        await asyncio.sleep(.01)
    return end


def dt_from_string(string):
    return datetime.strptime(string, "%y%m%d%H%M%S")

def dt_to_string(dt):
    return dt.strftime("%y%m%d%H%M%S")

dt_now = datetime.now

def dash_name(name):
    return name.replace(" ", "-").lower()

def capitalize_name(name):
    return " ".join([capitalize(n) for n in name.split(" ")])

def episode_from_code(code):
    season = int(code[1:-3])
    episode = int(code[-2:])
    return season, episode

def dot_string(name):
    return name.replace(" ", ".").replace("-", ".")

def get_intervals(array):
    intervals = []
    cur=0
    for i in range(1, len(array)):
        if array[i]-array[i-1]!=1:
            intervals.append((array[cur], array[i-1]))
            cur = i
    if cur!=len(array)-1:
        intervals.append((array[cur], array[-1]))
    return intervals
    

def episode_code(show, season, episode, quality):
    return f"{dot_string(path_safe(show))}.S{pad_left(str(season), 2, '0')}E{pad_left(str(episode), 2, '0')}.{quality}"

def clear_dir(path):
    for item in os.listdir(path):
        if os.path.isdir(os.path.join(path, item)):
            clear_dir(os.path.join(path, item))
        else:
            os.remove(os.path.join(path, item))
    os.rmdir(path)
    
def path_safe(name):
    return "".join([c for c in name if c.isalnum() or c in " .-"]).strip()

import re

def printable(string):
    # Define the regular expression pattern for valid characters in a Windows directory name
    pattern = r"[^\\/:*?\"<>|\r\n]+"
    
    # Use the re.findall function to find all matching substrings
    valid_chars = re.findall(pattern, string)
    
    # Concatenate the valid characters to form the directory name
    valid_dir_name = ''.join(valid_chars)
    
    return valid_dir_name

def strip(string):
    return ' '.join([i for i in string.split(' ') if i])
