from __future__ import absolute_import
import re
import json
import hashlib
import requests

from apis.base import BaseAPI, APIException

class InstagramPhotoAPI(BaseAPI):
    base_url = "https://www.instagram.com"
    per_page = 12

    def __init__(self, user, max_imgs):
        super(InstagramPhotoAPI, self).__init__(user, max_imgs)
        self.window_cur = 0
        self.get_main_page_and_query_hash(user)
    
    def get_main_page_and_query_hash(self, user):
        self.session = requests.Session()
        self.session.headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/73.0.3683.86 Chrome/73.0.3683.86 Safari/537.36'
                }

        r = self.session.get("{}/{}/".format(self.base_url, user))

        if r.status_code != 200:
            raise APIException('User with this login not found')

        # Get rhx_gis for GIS signature
        m = re.search(b"rhx_gis\":\"(.+?)\"", r.content)
        if not m:
            raise APIException('Error extract rhx_gis from main page')
        
        self.rhx_gis = m.group(1)

        # Get shared data
        m = re.search(b">window._sharedData = (.+?);</script>", r.content)
        if not m:
            raise APIException('Error extract shared data from main page')

        shared_data = m.group(1)
        shared_data = json.loads(shared_data)

        user = shared_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]
        self.user_id = user["id"]

        self.items, self.end_cursor = self.get_sources_from_user(user)

        # Get query_hash
        m = re.search(b"\"/(.+?)ProfilePageContainer.js(.+?)\"", r.content)
        if not m:
            raise APIException('Error extract link to js file from main page')

        profile_js_href = m.group(0).decode().replace('"', '')
        r = self.session.get("{}{}".format(self.base_url, profile_js_href))

        if r.status_code != 200:
            raise APIException('Error receiving js file from server')

        m = re.search(b"void 0:s.pagination},queryId:\"(.+?)\"", r.content)
        self.query_hash = m.group(1).decode()

    def get_sources_from_user(self, user):
        edge_owner_to_timeline_media = user["edge_owner_to_timeline_media"]
        edges = edge_owner_to_timeline_media["edges"]

        page_info = edge_owner_to_timeline_media["page_info"]
        has_next_page = page_info["has_next_page"]
        end_cursor = page_info["end_cursor"]
        self.total = 500

        return [edge["node"]["thumbnail_resources"][0]["src"] for edge in edges], end_cursor if has_next_page else None

    def load(self, end_cursor=None):
        if not end_cursor:
            raise StopIteration()

        variables = json.dumps({"id": self.user_id, "first": self.per_page, "after": end_cursor}).replace(" ", "")
        s = "{}:{}".format(self.rhx_gis.decode(), variables).encode('utf-8')
        gis = hashlib.md5(s).hexdigest()


        r = self.session.get("https://www.instagram.com/graphql/query/", params={
            'query_hash': self.query_hash, 
            'variables': variables}, headers={'x-instagram-gis': gis})

        if r.status_code != 200:
            self.max_imgs = 0
            raise StopIteration()
        else:
            self.items, self.end_cursor = self.get_sources_from_user(r.json()["data"]["user"])
            self.window_cur = 0

    def __next__(self):
        if self.cur >= self.max_imgs or self.cur >= self.total:
            raise StopIteration()
        
        if self.window_cur >= len(self.items):
            self.load(self.end_cursor)
        
        item = self.items[self.window_cur]
        
        self.window_cur += 1
        self.cur += 1

        return item
