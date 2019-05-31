from __future__ import absolute_import
from builtins import object
from apis.base import BaseAPI
from apis.flickr import FlickrPhotoAPI
from apis.instagram import InstagramPhotoAPI

class DataGen(object):
    def __init__(self, url_generator, w, h):
        self.url_generator = url_generator
        self.w = w
        self.h = h
    
    def __next__(self):
        return (next(self.url_generator), self.w, self.h)

    def __iter__(self):
        return self

def make(user, max_imgs, w, h):
    if user and '@' in user:
        return DataGen(InstagramPhotoAPI(user.replace('@', ''), max_imgs), w, h)
    else:
        return DataGen(FlickrPhotoAPI(user, max_imgs), w, h)
    
