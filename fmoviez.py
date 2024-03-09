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
    # return vurl   


def intercept_response(response, future):
    if not response.url.endswith(".m3u8"):
        return
    splited = response.url.split("/")
    parts = split_array(splited, "h")
    if parts[1][0].split(";")[0]=="list":
        future.set_result(response.url)
    

# async def intercept_response(response):
#     logging.log("intercepted", request.url)


async def go_to_fmoviez(url):
    logging.log("launching browser")
    browser = await pyppeteer.launch({"executablePath": "C:\Program Files\Google\Chrome\Application\chrome.exe", "headless": True})
    page = await browser.newPage()  
    await stealth(page)
    # await page.setRequestInterception(True)
    try:
        logging.log("going to "+url)
        await page.goto(url)
        future = asyncio.Future()
        logging.log("intercepting response with .m3u8 files")
        page.on('response', lambda res: intercept_response(res, future))
        await page.evaluate("""() => { 
            let element = document.querySelector("#player").querySelector("i");
            element.click();
        }""")
        list_url = await asyncio.wait_for(future, timeout=30)
        logging.log("intercepted resolution list file")
        logging.log("closing the browser")
        await browser.close()
        return list_url

    except Exception as e:
        logging.log("closing the browser")
        await browser.close()
        raise e
