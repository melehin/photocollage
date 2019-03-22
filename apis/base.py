class APIException(Exception):
    pass

class BaseAPI(object):
    def __init__(self, user, max_imgs=1):
        self.user = user
        self.max_imgs = max_imgs
        self.cur = 0
    
    def __next__(self, a):
        if self.cur >= self.max_imgs:
            raise StopIteration()
        
        self.cur += 1
        
        return self.cur
    
    def __iter__(self):
        return self