import os
os.environ['PYPPETEER_CHROMIUM_REVISION'] = '1263111'
import asyncio
from pyppeteer import launch

async def log_request(response):
    print(response.url)

async def main():
    browser = await launch({"headless": True})
    page = await browser.newPage()

    # Enable request interception
    # await page.setRequestInterception(True)
    page.on('response', lambda res: asyncio.ensure_future(log_request(res)))
    # Navigate to a page
    await page.goto('https://google.com')

    # Close the browser
    await browser.close()


asyncio.get_event_loop().run_until_complete(main())