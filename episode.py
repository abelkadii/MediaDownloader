from utils import pad_left

class Episode:
    def __init__(self, show, season, episode, title, release, url, _id, downloaded=False, available_qualities=[], quality=None, duration=None, size=None, available_subtitles=[], downloaded_subtitles=[]):
        self.show = show
        self.season = season
        self.episode = episode
        self.title = title
        self.release = release
        self.url = url
        self.id = _id
        self.downloaded = downloaded
        self.available_qualities = available_qualities
        self.quality = quality
        self.duration = duration
        self.size = size
        self.available_subtitles = available_subtitles
        self.downloaded_subtitles = downloaded_subtitles

    @classmethod
    def new(self, show, season, episode, data):
        return Episode(show, season, episode, data['title'], data['time'], data['url'], data['id'])

    def add_to_queue(self, q, quality=None, priority=0, overide=False):
        return q.add(self, quality, priority, overide)

    @property
    def num(self):
        return sum(self.show.structure[:self.season-1])+self.episode
    
    def __str__(self):
        return f"{self.show.code}.{self.season}.{self.episode}.{self.quality}"
    
    @property
    def code(self):
        return f"S{pad_left(str(self.season), 2, '0')}E{pad_left(str(self.episode), 2, '0')}"


    @classmethod
    def from_dict(self, show, episode):
        return Episode(
            show=show,
            season = episode.get("season"),
            episode = episode.get("episode"),
            title = episode.get("title"),
            release = episode.get("release"),
            url = episode.get("url"),
            _id = episode.get("id"),
            downloaded = episode.get("downloaded"),
            available_qualities = episode.get("available_qualities"),
            quality = episode.get("quality", "0p"),
            duration = episode.get("duration"),
            size = episode.get("size"),
            available_subtitles = episode.get("available_subtitles"),
            downloaded_subtitles = episode.get("downloaded_subtitles"),
        )

    def to_dict(self):
        return {
            "show": self.show.name,
            "season": self.season,
            "episode": self.episode,
            "title": self.title,
            'release': self.release,
            "url": self.url,
            "id": self.id,
            "downloaded": self.downloaded,
            "available_qualities": self.available_qualities,
            "quality": self.quality,
            "duration": self.duration,
            "size": self.size,
            "available_subtitles": self.available_subtitles,
            "downloaded_subtitles": self.downloaded_subtitles,
        }
    
    def save(self):
        self.show.save()
    
    