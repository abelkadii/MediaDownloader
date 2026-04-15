from utils import split_array
import asyncio
import pyppeteer
from pyppeteer_stealth import stealth
import logging




async def get_info(code, content_type="tv"):
    url = "https://fmoviesz.to/"+content_type+"/"+code
    print("launching browser")
    browser = await pyppeteer.launch({"executablePath": "C:\Program Files\Google\Chrome\Application\chrome.exe", "headless": True})
    page = await browser.newPage()  
    await stealth(page)
    # await page.setRequestInterception(True)
    try:
        print("going to "+url)
        await page.goto(url)
        print('gathering info')
        seasons = await page.evaluate("""()=>{
            let seasons = {};
            let episodes = document.querySelector("#episodes").querySelector("div.body").children;
            for (let i = 0; i < episodes.length; i++) {
                    let season = []
                    let seasonNum = episodes[i].getAttribute("data-season");
                for (let j = 0; j < episodes[i].children.length; j++) {
                    let episodeElement = episodes[i].children[j];
                    let episode = {}
                    let time = episodeElement.querySelector("a").getAttribute("data-original-title");
                    episode["time"] = time;
                    episode["url"] = "https://fmoviesz.to"+episodeElement.querySelector("a").getAttribute("href");
                    episode["id"] = episodeElement.querySelector("a").getAttribute("data-id");
                    episode["num"] = episodeElement.querySelectorAll("span")[0].innerText;
                    episode["title"] = Array.from(episodeElement.querySelectorAll("span")).at(-1).innerText;
                    season.push(episode);
                }
                seasons[seasonNum] = season;
            }                            
            return seasons;
        }""")

        information = await page.evaluate("""()=>{
            let infoSection = document.getElementById("w-info");
            let posterURL = infoSection.querySelector("div.poster").querySelector("img").src;
            let title = infoSection.querySelector("div.info").querySelector("h1.name").innerText;
            let description = infoSection.querySelector("div.info").querySelector("div.description.cts-wrapper").innerText;
            let detailsDiv = infoSection.querySelector("div.info").querySelector("div.detail");
            let details = [];
            for (let i = 0; i < detailsDiv.children.length; i++) {
                try{details.push([detailsDiv.children[i].children[0].innerText, detailsDiv.children[i].children[1].innerText]);}
                catch(e){continue;}
            }
            return {posterURL, title, description, details};
                                          
        }""")
        details = {}
        for k, v in information["details"]:
            details[k.split(":")[0].lower()] = v
        information["details"] = details
        if content_type=="tv":
            information["seasons"] = seasons
        else:
            information["id"] = seasons["1"][0]['id']
        await browser.close()
        return information

    except Exception as e:
        # print("closing the browser")
        await browser.close()
        raise e


# if __name__ == "__main__":
#     # asyncio.run(get_info_tv("the-walking-dead"))
#     info = asyncio.run(get_info("the-batman-j2lx4", "movie"))
#     print(info)
