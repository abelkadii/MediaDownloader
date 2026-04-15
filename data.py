


class Data:
    def __init__(self, data=[]):
        self.data = data
    
    def f_filter(self, func):
        return self.__class__([x for x in self.data if func(x)])
    
    def filter(self, **filters):
        return self.f_filter(lambda x: all([x[k]==v for k,v in filters.items()]))

    def update(self, **items):
        for k, v in items.items():
            for i in self.data:
                i[k] = v
        return self

    def get(self, **filters):
        fl[0] if (fl:=self.filter(**filters)) else None
    
    def __iter__(self):
        return iter(self.data)
    
    def __getitem__(self, index):
        return self.data[index]