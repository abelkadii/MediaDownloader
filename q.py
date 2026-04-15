import os
import json
from show import Show
from utils import *
from episode import Episode
from data import Data

PATH = os.path.join(BASE_DIR, "Queue.log")
QUEUE_STATUS = ["PENDING", "STARTED", "DOWNLOADED", "REBUILT", "FINISHED"]


class QItem:
    def __init__(self, show, code, season, episode, quality, status, priority, time_added, q):
        self.q = q
        self.show = show
        self.code = code
        self.season = season
        self.episode = episode
        self.quality = quality
        self.status = status
        self.priority = priority
        self.time_added = time_added

    @classmethod
    def new(self, show, code, season, episode, quality, priority, q):
        return QItem(show, code, season, episode, quality, QUEUE_STATUS[0], priority, dt_now(), q)

    def use(self):
        return self.show, self.season, self.episode, self.quality, self.code

    def update(self, **updates):
        for key, value in updates.items():
            setattr(self, key, value)
        self.q.sort()
        self.save()

    def encode(self):
        return f"{dot_string(strip(printable(self.show)))}.S{pad_left(str(self.season), 2, '0')}E{pad_left(str(self.episode), 2, '0')}.{self.quality} {self.code} {self.status} {self.priority} {dt_to_string(self.time_added)}"
    
    def save(self):
        self.q.save()

    def __str__(self):
        return self.encode()

    def __repr__(self):
        return self.encode()

    def __eq__(self, other):
        return self.show == (other.show.name if isinstance(other, Episode) else other.show) and self.season == other.season and self.episode == other.episode
    
    def __gt__(self, other):
        if self==other:return False
        if self.priority > other.priority:return True
        if self.priority < other.priority:return False
        if self.show!=other.show:
            return self.time_added < other.time_added
        else:
            if self.season < other.season:return True
            if self.season > other.season:return False
            if self.episode < other.episode:return True
            if self.episode > other.episode:return False
            raise Exception("Two items with the same season, episode")
    
    def __lt__(self, other):return self != other and not self > other
    def __ge__(self, other):return self > other or self == other
    def __le__(self, other):return self < other or self == other


    @classmethod
    def decode(cls, string, q):
        parts = string.split(" ")
        show = " ".join(parts[0].split(".")[:-2])
        season, episode = episode_from_code(parts[0].split(".")[-2])
        quality = parts[0].split(".")[-1]
        code = parts[1]
        status = parts[2]
        priority = int(parts[3])
        time_added = dt_from_string(parts[4])
        return cls(show, code, season, episode, quality, status, priority, time_added, q)
    
    def remove(self):
        self.q.remove(self)
    
class DQ:
    def __init__(self):
        self.queue = []
        self.load()
    
    def load(self):
        with open(PATH, "r") as file:
            data = file.read()
        lines = data.split("\n")
        for line in lines:
            if line:
                self.queue.append(QItem.decode(line, self))
        self.sort()

    def sort(self):
        self.queue = sorted(self.queue, reverse=True)

    def top(self) -> QItem:
        if not self.queue:
            return None
        return self.queue[0]
    def at(self, ind) -> QItem:
        if not self.queue:
            return None
        assert len(self.queue) > ind
        return self.queue[ind]
    
    def pop(self):
        self.queue.pop(0)
        self.save()
    

    def get(self, episode):
        for item in self.queue:
            if item == episode:
                return item
    
    def __getitem__(self, index):
        return self.queue[index]


    def add(self, episode, quality, priority=0, overide=False):
        if episode in self:
            if overide:
                qitem = self.get(episode)
                qitem.priority = priority
                qitem.time_added = dt_now()
                qitem.quality = quality
                self.sort()
                self.save()
                return 
            else:
                raise Exception("Item already in queue.")
        self.queue.append(QItem.new(episode.show.name, "tv/"+episode.show.code, episode.season, episode.episode, quality, priority, self))
        self.sort()
        self.save()
    
    def add_movie(self, name, code, quality, priority=0, overide=False):
        for item in self.queue:
            if item.show == name and item.code == code:
                if overide:
                    item.priority = priority
                    item.time_added = dt_now()
                    item.quality = quality
                    self.sort()
                    self.save()
                    return 
                else:
                    raise Exception("Item already in queue.")
        self.queue.append(QItem.new(name, "movie/"+code, 1, 1, quality, priority, self))
        self.sort()
        self.save()

    def remove(self, episode):
        self.queue = [item for item in self.queue if item != episode]
        self.save()
    
    def remove_movie(self, name, code):
        for item in self.queue:
            if item.show == name and item.code == code:
                self.queue.remove(item)
                self.save()
                return

    def save(self):
        with open(PATH, "w") as file:
            for item in self.queue:
                file.write(str(item)+"\n")
            file.close()

    def __contains__(self, item):
        return self.get(item) is not None
    
    def update(self, filters, updates):
        data = Data(self.queue).filter(**filters)
        data.update(**updates)
        self.save()

    def remove(self, filters):
        self.queue = Data(self.queue).filter(**filters).data
        self.save()
    
    def filter(self, **filters):
        return Data(self.queue).filter(**filters)

    
    def get_all(self):
        return self.queue
    
    # def display(self, a=None, b=None):
    #     shows = {}
    #     sc=0
    #     for item in self.queue:
    #         if item.show not in shows:
    #             shows[item.show] = []
    #             sc+=1
    #         shows[item.show].append(item)

    #     all_intervals = {}
    #     for show in shows:
    #         all_intervals[show] = []
    #         e_show = shows[show][0].show
    #         shows[show].sort(key=lambda x: x.num)
    #         intervals = get_intervals([x.num for x in show])
    #         for a, b in intervals:
    #             if a!=b:
    #                 all_intervals[show].append(e_show.episode(num=a).code+"-"+e_show.episode(num=b).code)
    #             else:
    #                 all_intervals[show].append(e_show.episode(num=a).code)
    #     return all_intervals