from apis.base import BaseAPI
from apis.flickr import FlickrPhotoAPI

class DataGen:
    def __init__(self, url_generator, w, h):
        self.url_generator = url_generator
        self.w = w
        self.h = h
    
    def __next__(self):
        return (next(self.url_generator), self.w, self.h)

    def __iter__(self):
        return self

def make(user, max_imgs, w, h) -> BaseAPI:
    return DataGen(FlickrPhotoAPI(user, max_imgs), w, h)
    