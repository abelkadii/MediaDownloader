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

all_logs = []


def intercept_response(response):
    all_logs.append(response.url)
    # if not response.url.endswith(".m3u8"):
    #     return
    # splited = response.url.split("/")
    # parts = split_array(splited, "h")
    # if parts[1][0].split(";")[0]=="list":
    #     future.set_result(response.url)
    

# async def intercept_response(response):
#     print("intercepted", request.url)


async def go_to_fmoviez(url):
    print("launching browser")
    browser = await pyppeteer.launch({"executablePath": "C:\Program Files\Google\Chrome\Application\chrome.exe", "headless": True})
    page = await browser.newPage()  
    await stealth(page)
    # await page.setRequestInterception(True)
    try:
        print("going to "+url)
        page.on('response', lambda res: intercept_response(res))
        await page.goto(url)
        print("intercepting all responses")
        await page.evaluate("""() => { 
            let element = document.querySelector("#player").querySelector("i");
            element.click();
        }""")
        await asyncio.sleep(10)
        # print("intercepted resolution list file")
        print("closing the browser")
        await browser.close()

    except Exception as e:
        # print("closing the browser")
        await browser.close()
        raise e
def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(go_to_fmoviez("https://fmoviesz.to/tv/friends-3rvj9"))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
    with open("logs.txt", "w") as file:
        file.write("\n".join(all_logs))
    print(len(all_logs))

if __name__ ==  '__main__':
    main()