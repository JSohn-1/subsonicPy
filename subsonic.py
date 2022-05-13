import requests
import xml.etree.ElementTree as ET

class subsonic:
    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.url = url
    
    def request(self, req, params):
        req = "http://" + self.url + "/rest/" + req + ".view?u=" + self.username + "&p=" + self.password + "&v=1.12.0&c=myapp"

        for p in params:
            for n in p["content"]:
                req = req + "&" + p["head"] + "=" + n

        return req

    def request2(self, req):
        return("http://" + self.url + "/rest/" + req + ".view?u=" + self.username + "&p=" + self.password + "&v=1.12.0&c=myapp")

    def ping(self):
        return requests.get(self.request2("ping"))

    def getId(self, name):
        result = requests.get(self.request("search2", [{"head": "query", "content": [name]}]))
        result = ET.fromstring(result.text)
        for type in result.findall("searchResult2/song"):
            return(type.get("id"))

    def createPlaylist(self, name):
        return requests.post(self.request("createPlaylist", [{"head": "name", "content": [name]}]))

    def getPId(self, name):
        result = requests.get(self.request("getPlaylists", [{"head": "query", "content": [name]}]))
        result = ET.fromstring(result.text)
        for type in result.findall("playlists/playlist"):

            if type.get("name") == name:
                return(type.get("id"))

    def addToPlaylist(self, id, sid):
        return requests.post(self.request("updatePlaylist", [{"head": "playlistId", "content": [id]}, {"head": "songIdToAdd", "content": sid}]))


    def scan(self):

        return requests.get(self.request2("startScan"))

    def getScanStatus(self):
        result = requests.get(self.request2("getScanStatus"))
        result = ET.fromstring(result.text)
        for type in result.findall("scanStatus"):
            return(type.get("scanning") == "true")
                