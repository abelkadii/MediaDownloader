import os
import json
from utils import *
from gather_information import get_info


MOVIE_PATH = os.path.join(BASE_DIR, "content\\movie")


class Movie:
    def __init__(self, name, code, country, release, id):
        self.name = name
        self.code = code
        self.country = country
        self.release = release
        self.id = id
        self.path = os.path.join(MOVIE_PATH, self.encoded_name()+".json")
    
    def encoded_name(self):
        return self._encoded(self.name)
    
    @classmethod
    def _encoded(self, name):
        return name.replace(" ", "-").replace(":", "-").replace("--", "-")
    

    @classmethod
    def from_dict(self, movie):
        obj = self(movie['name'], movie['code'], movie['country'], movie['release'], movie['id'])
        return obj

    
    def to_dict(self):
        return {
            "name": self.name,
            "code": self.code,
            "country": self.country,
            "release": self.release,
            "id": self.id,
        }

    def save(self):
        json.dump(self.to_dict(), open(self.path, 'w'), indent=4)

    @classmethod
    def new(cls, movie_name, informations):
        name = informations['title']
        country = informations.get("details").get("country")
        release = informations.get("details").get("release")
        movie = cls(name, movie_name, country, release, informations.get("id"))
        movie.save()
        return movie
    
    @classmethod
    def add(self, code, keywords):
        informations = asyncio.get_event_loop().run_until_complete(get_info(code, "movie"))
        self.save_movie(code, informations, keywords)
    
    @classmethod
    async def a_add(self, code, keywords):
        informations = await get_info(code, "movie")
        self.save_movie(code, informations, keywords)

    @classmethod
    def save_movie(self, code, informations, keywords):
        movie = self.new(code, informations)
        if movie.name not in keywords:
            keywords.append(movie.name)
        with open(os.path.join(MOVIE_PATH, "__all__.json"), "r") as file:
            data = json.load(file)
            data = [d for d in data if d["code"] != movie.code]
            data.append({
                "name": movie.name,
                "code": code,
                "keywords": keywords,
                "added_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            })

        with open(os.path.join(MOVIE_PATH, "__all__.json"), "w") as file:
            json.dump(data, file, indent=4)
        return movie



    @classmethod
    def load(self, movie_name):
        all_movies = json.load(open(os.path.join(MOVIE_PATH, "__all__.json"), 'r'))
        for movie in all_movies:
            if movie_name in movie['keywords']:
                return self.from_dict(json.load(open(os.path.join(MOVIE_PATH, self._encoded(movie['name'])+".json"), 'r')))
        
    def add_to_queue(self, q, quality=None, priority=0, overide=False):
        q.add_movie(self.name, self.code, quality, priority, overide)


    @classmethod
    def get_all(self):
        shows = []
        for movie in os.listdir(MOVIE_PATH):
            shows.append(self.from_dict(json.load(open(os.path.join(MOVIE_PATH, movie), 'r'))))
        return shows