import re
import json
import requests

from apis.base import BaseAPI, APIException

# Flickr API: https://www.flickr.com/services/api/
class FlickrPhotoAPI(BaseAPI):
    url_format = "https://farm{farm}.staticflickr.com/{server}/{id}_{secret}_m.jpg"
    per_page = 10

    def __init__(self, user, max_imgs):
        super(FlickrPhotoAPI, self).__init__(user, max_imgs)
        self.window_cur = 0
        self.get_api_key()
        self.load()
    
    def get_api_key(self):
        r = requests.get("https://flickr.com/photos/")
        if r.status_code == 200:
            m = re.search(b'root.YUI_config.flickr.api.site_key = "(.+?)";', r.content)
            if m:
                self.api_key = m.group(1)
                return
        
        raise APIException("Can't get API key from flickr")

    def load(self, page=1):
        r = requests.get("https://api.flickr.com/services/rest", params={
            "method": "flickr.photos.search" if self.user else "flickr.photos.getRecent",
            "format": "json",
            "user_id": self.user,
            "api_key": self.api_key,
            "per_page": self.per_page,
            "page": page
        })
        self.page = page
        
        if r.status_code != 200:
            self.max_imgs = 0
            raise StopIteration()
        else:
            content = r.content.replace(b"jsonFlickrApi(", b"").rstrip(b")")
            self.json = json.loads(content)
            if self.json['stat'] == 'ok':
                self.total = int(self.json['photos']['total'])
                self.items = self.json['photos']['photo']
                self.window_cur = 0
            else:
                raise APIException(self.json['message'])

    def __next__(self):
        if self.cur >= self.max_imgs or self.cur >= self.total:
            raise StopIteration()
        
        if self.window_cur >= len(self.items):
            self.load(self.page+1)
        
        item = self.items[self.window_cur]
        
        self.window_cur += 1
        self.cur += 1

        return self.url_format.format(**item)