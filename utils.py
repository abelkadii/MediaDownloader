# import os
# import json

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# CONFIG = json.load(open(os.path.join(BASE_DIR, "config.json"), 'r'))

# for path in CONFIG.get('paths'):
#     CONFIG['paths'][path] = CONFIG['paths'][path].replace("@", BASE_DIR)

# class Base:
#     def __init__(self): return
#     def __str__(self) -> str: return self.obj.__str__()

# def to_data_class(obj):
#     base = Base()
#     base.obj = obj
#     for key, value in obj.items():
#         if isinstance(value, dict):
#            base.__setattr__(key, to_data_class(value))
#         else:
#            base.__setattr__(key, value)
#     return base

# CONFIG = to_data_class(CONFIG)

import os
import random

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