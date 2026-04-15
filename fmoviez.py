from utils import split_array
import asyncio
import pyppeteer
from pyppeteer_stealth import stealth
import logging
# async def get_iframe_url(page, url):
    
    # vurl = await page.evaluate("""() => { 
    #     let iframe = document.querySelector("#player").querySelector("iframe");
    #     return iframe.src;
    # }""")
    # return vurl+


def intercept_response(response, future):
    # print("intercepted", response.url)
    if not response.url.endswith(".m3u8"):
        return
    # print("intercepted .m3u8 file", response.url)
    splited = response.url.split("/")
    parts = split_array(splited, "h")
    if parts[1][0].split(";")[0]=="list":
        future.set_result(response.url)
    

# async def intercept_response(response):
#     print("intercepted", request.url)


async def go_to_fmoviez(url):
    # print("launching browser")
    browser = await pyppeteer.launch({"executablePath": "C:\Program Files\Google\Chrome\Application\chrome.exe", "headless": False})
    page = await browser.newPage()  
    await stealth(page)
    # await page.setRequestInterception(True)
    try:
        # print("going to "+url)
        await page.goto(url)
        future = asyncio.Future()
        # https://dzdxx.mv29nz9ho.online/_v2p-lrld/12a3c523f8105800ed8c394685aeeb0bc62ea85c02b0bef403187baea93ece832257df1a4b6125fcfa38c35da05dee86aad28d46d73fc4e9d4e5a33d5072f3d534c114e30918b4081286a3b967107c122631822f4d436ec3d1c6fb0fc3fe6091204eb9160c69bb09ba/h/cdfaaafec3/cce;15a3873cfa10585daa846515d1b0ea069138af455cb8a8ee490165a0a7.m3u8
        # print("intercepting response with .m3u8 files")
        page.on('response', lambda res: intercept_response(res, future))
        await page.evaluate("""() => { 
            let element = document.querySelector("#player").querySelector("i");
            element.click();
        }""")
        list_url = await asyncio.wait_for(future, timeout=60)
        # print("intercepted resolution list file")
        # print("closing the browser")
        await browser.close()
        return list_url

    except Exception as e:
        # print("closing the browser")
        await browser.close()
        raise e
