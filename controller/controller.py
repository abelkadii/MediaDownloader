import asyncio
import pyppeteer
from pyppeteer_stealth import stealth

MAX_CONCURRENT_DOWNLOADS = 1
async def intercept_response(request):
    response = await request.response()
    logging.log(f"Intercepted response from {request.url}: {response.status}")
async def goto_page_intercept(page, url):
    pass
    
     

# def add_to_download_queue(urls):
#     logging.log("adding to download queue", urls)
#     with open('downloads.txt', 'r') as f:
#         downloads = f.read().split('\n')
#     downloads = [d for d in downloads if d != '']
#     if type(urls) == str:
#         urls = [urls]
#     for url in urls:
#         downloads.append(url)
#     with open('downloads.txt', 'w') as f:
#         f.write('\n'.join(downloads))
#         f.close()

# async def get_urls(urls):
#     browser = await pyppeteer.launch({"executablePath": "C:\Program Files\Google\Chrome\Application\chrome.exe", "headless": True})
#     try:
#         for i in range(0, len(urls), MAX_CONCURRENT_DOWNLOADS):
#             bach = []
#             for url in urls[i:i+MAX_CONCURRENT_DOWNLOADS]:
#                 page = await browser.newPage()
#                 await stealth(page)
#                 bach.append(get_iframe_url(page, url))
#             await asyncio.gather(*bach)
            
#     except Exception as e:
#         logging.log("closing the browser")
#         await browser.close()
#         raise e
#     logging.log("closing the browser")
#     await browser.close()

if __name__ == "__main__":
    asyncio.run(goto_page_intercept('https://vidplay.online/e/D1YKDMQDLJNV?t=4xjQAPwlDFcJyw%3D%3D&sub.info=https%3A%2F%2Ffmoviesz.to%2Fajax%2Fepisode%2Fsubtitles%2F290467&autostart=true'))