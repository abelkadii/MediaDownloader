import os
import json
from utils import *
from episode import Episode
from gather_information import get_info


SHOW_PATH = os.path.join(BASE_DIR, "content\\tv")


class Show:
    def __init__(self, name, code, country, release, seasons=[]):
        self.name = name
        self.code = code
        self.country = country
        self.release = release
        self.seasons = seasons
        self.path = os.path.join(SHOW_PATH, self.encoded_name()+".json")
    
    def encoded_name(self):
        return self._encoded(self.name)
    
    @classmethod
    def _encoded(self, name):
        return name.replace(" ", "-").replace(":", "-").replace("--", "-")
    
    @property
    def structure(self):
        return [len(s) for s in self.seasons]

    @classmethod
    def from_dict(self, show):
        obj = Show(show['name'], show['code'], show['country'], show['release'])
        obj.seasons = obj.load_seasons(show['seasons'])
        return obj

    def load_seasons(self, seasons):
        seasons = [[Episode.from_dict(self, e) for e in s] for s in seasons]
        return seasons
    
    def to_dict(self):
        return {
            "name": self.name,
            "code": self.code,
            "country": self.country,
            "release": self.release,
            "seasons": [[e.to_dict() for e in s] for s in self.seasons]
        }

    def save(self):
        json.dump(self.to_dict(), open(self.path, 'w'), indent=4)

    @classmethod
    def new(cls, show_name, informations):
        name = informations['title']
        country = informations.get("details").get("country")
        release = informations.get("details").get("release")
        show = cls(name, show_name, country, release, [])
        for sn, season in informations.get("seasons").items():
            show.seasons.append([])
            for en, episode in enumerate(season, 1):
                episode = Episode.new(show=show, season=int(sn), episode=en, data=episode)
                show.seasons[-1].append(episode)
        show.save()
        return show
    
    def episode(self, code=None, num=None, season=None, episode=None) -> Episode:
        if code:
            season , episode = episode_from_code(code)
        if num:
            s=0
            struct = self.structure
            while num>struct[s]:
                num -= struct[s]
                s+=1
            season, episode = s+1, num
        assert season <= len(self.seasons), f"Season {season} does not exist."
        assert episode <= len(self.seasons[season-1]), f"Episode {episode} does not exist."
        return self.seasons[season-1][episode-1]

    
    @classmethod
    def add(self, code, keywords):
        informations = asyncio.get_event_loop().run_until_complete(get_info(code))
        self.save_show(code, informations, keywords)
    
    @classmethod
    async def a_add(self, code, keywords):
        informations = await get_info(code)
        self.save_show(code, informations, keywords)

    @classmethod
    def save_show(self, code, informations, keywords):
        show = self.new(code, informations)
        if show.name not in keywords:
            keywords.append(show.name)
        with open(os.path.join(SHOW_PATH, "__all__.json"), "r") as file:
            data = json.load(file)
            data = [d for d in data if d["code"] != show.code]
            data.append({
                "name": show.name,
                "code": code,
                "structure": show.structure,
                "keywords": keywords,
                "added_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            })
        with open(os.path.join(SHOW_PATH, "__all__.json"), "w") as file:
            json.dump(data, file, indent=4)
        return show

    @classmethod
    def load(self, show_name):
        all_shows = json.load(open(os.path.join(SHOW_PATH, "__all__.json"), 'r'))
        for show in all_shows:
            if show_name in show['keywords']:
                return self.from_dict(json.load(open(os.path.join(SHOW_PATH, self._encoded(show['name'])+".json"), 'r')))
        
    def add_to_queue(self, q, quality=None, priority=0, overide=False):
        t = 0
        for season in self.seasons:
            for episode in season:
                episode.add_to_queue(q, quality, priority, overide)
                t += 1
        return t
    
    def add_season_to_queue(self, q, season, quality=None, priority=0, overide=False):
        t = 0
        for episode in self.seasons[season-1]:
            episode.add_to_queue(q, quality, priority, overide)
            t += 1
        return t


    @classmethod
    def get_all(self):
        shows = []
        for show in os.listdir(SHOW_PATH):
            shows.append(self.from_dict(json.load(open(os.path.join(SHOW_PATH, show), 'r'))))
        return shows