import asyncio
from downloads import download_item, get_and_save_listurl
from q import DQ
from show import Show
from movie import Movie


                
async def main():
    q = DQ()
    while (item:=q.top()):
        if item.priority == -1:
            break
        success = False
        next = q.at(1)
        for i in range(4):
            try:
                await download_item(item, next)
                q.pop()
                success = True
                break
            except Exception as e:
                print(e, e.args)
        if not success:
            item.update(priority=-1)

async def scrape():
    q = DQ()
    for item in q:
        print('getting', item.use())
        for i in range(4):
            print('att', i)
            try:
                await get_and_save_listurl(item, overwrite=False)
                break
            except:
                pass
            if i==9:
                print("Error")


async def add(mvs):
    for sh, kw in mvs:
        await Show.a_add(sh, kw)
        print('added', sh)
            
async def add_to_q():
    q = DQ()
    # print()
    # lucifer = Show.load('Lucifer')
    # bcs = Show.load('better call saul')
    # got = Show.load('GOT')
    # lost = Show.load('Lost')
    # chernobyl = Show.load('Chernobyl')
    # mr = Show.load('Mr. Robot')
    # dexter = Show.load('Dexter')
    # friends = Show.load('Friends')
    
    # Movie.load('Monkey Man').add_to_queue(q, '1080p', 2)
    # Movie.load('mission impossible').add_to_queue(q, '1080p', 2)
    # Movie.load('dune').add_to_queue(q, '1080p', 2)
    # Movie.load('everything').add_to_queue(q, '1080p', 2)
    # Movie.load('The Revenant').add_to_queue(q, '1080p', 2)
    

    # friends.add_season_to_queue(q, 1, '1080p', 1)
    # dexter.add_season_to_queue(q, 4, '1080p', 2)
    # mr.add_season_to_queue(q, 1, '1080p', 2)
    # chernobyl.add_season_to_queue(q, 1, '1080p', 2)
    # lost.add_season_to_queue(q, 1, '1080p', 1)
    # got.add_season_to_queue(q, 1, '1080p', 1)
    # got.add_season_to_queue(q, 2, '1080p', 1)
    # got.add_season_to_queue(q, 3, '1080p', 1)
    # bcs.add_season_to_queue(q, 4, '1080p', 2)
    # bcs.add_season_to_queue(q, 5, '1080p', 2)
    # bcs.add_season_to_queue(q, 6, '1080p', 2)
    # lucifer.add_season_to_queue(q, 1, '1080p', 1)

if __name__ ==  '__main__':
    # asyncio.run(scrape())
    asyncio.run(main())
    # asyncio.run(add_to_q())
    # main()
    # asyncio.run(add([["lost-3xry", []], ['chernobyl-xjwjq', []],  ["mr-robot-ppmp4", []], ["dexter-kxxxw", []], ["friends-3rvj9", []]]))
    # ["mission-impossible-dead-reckoning-part-one-nky2l", ["mission impossible"]], ["monkey-man-jww83", []], ["dune-part-two-91jy0", ["dune"]], ["everything-everywhere-all-at-once-20vk2", ["everything"]], ["the-revenant-w8kk", []]