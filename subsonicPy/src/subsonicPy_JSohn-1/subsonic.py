import requests
import html
import xml.etree.ElementTree as ET

class subsonic:
    def __init__(self, username, password, url):
        self.username = html.escape(username)
        self.password = html.escape(password)
        self.url = url
    
    def request(self, req, params):
        req = "http://" + self.url + "/rest/" + req + "?u=" + self.username + "&p=" + self.password + "&v=1.12.0&c=myapp"

        for p in params:
            for n in p["content"]:
                if isinstance(n, str):
                    req = req + "&" + p["head"] + "=" + n

        return req

    def request2(self, req):
        return("http://" + self.url + "/rest/" + req + ".view?u=" + self.username + "&p=" + self.password + "&v=1.12.0&c=myapp")

    def ping(self):
        return requests.get(self.request2("ping"))

    def getId(self, name):
        #name = name.replace("’", "\'")
        nme = name
        result = requests.get(self.request("search2", [{"head": "query", "content": [name]}])).text
        result = result.replace("â", "’")
        result = result.replace("Ã«", "ë")

        result = ET.fromstring(result)
        n = name
        for type in result.findall("searchResult2/song"):
            if type.get("title") == n:
                return(type.get("id"))

        for type in result.findall("searchResult2/album"):
            if type.get("title") == n:
                return(type.get("id"))
        
        n = html.escape(n)

        for type in result.findall("searchResult2/song"):
            if type.get("title") == n:
                return(type.get("id"))

        for type in result.findall("searchResult2/album"):
            if type.get("title") == n:
                return(type.get("id"))

        n = n.replace("\'", "&quot;")

        for type in result.findall("searchResult2/song"):
            if type.get("title") == n:
                return(type.get("id"))

        for type in result.findall("searchResult2/album"):
            if type.get("title") == n:
                return(type.get("id"))

        name = name.replace("\'", "\"")

        result = requests.get(self.request("search2", [{"head": "query", "content": [name]}])).text
        #result.encode('latin1').decode('unicode_escape').encode('latin1').decode('utf8')
        result = result.replace("â", "’")
        result = result.replace("Ã«", "ë")
        result = ET.fromstring(result)

        n = name
        for type in result.findall("searchResult2/song"):
            if type.get("title") == n:
                return(type.get("id"))

        for type in result.findall("searchResult2/album"):
            if type.get("title") == n:
                return(type.get("id"))
        
        n = html.escape(n)

        for type in result.findall("searchResult2/song"):
            if type.get("title") == n:
                return(type.get("id"))

        for type in result.findall("searchResult2/album"):
            if type.get("title") == n:
                return(type.get("id"))

        n = n.replace("&#x27;", "&quot;")

        for type in result.findall("searchResult2/song"):
            if type.get("title") == n:
                return(type.get("id"))

        for type in result.findall("searchResult2/album"):
            if type.get("title") == n:
                return(type.get("id"))
            
        print(nme)
        print(n)
        print(name)
        print("------")


    def createPlaylist(self, name):
        return requests.post(self.request("createPlaylist", [{"head": "name", "content": [name]}]))

    def getPId(self, name):
        result = requests.get(self.request("getPlaylists", [{"head": "query", "content": [name]}]))
        result = ET.fromstring(result.text)
        for type in result.findall("playlists/playlist"):

            if type.get("name") == name:
                return(type.get("id"))


    def addToPlaylist(self, id, sid):
        print(id)
        return requests.post(self.request("updatePlaylist", [{"head": "playlistId", "content": [id]}, {"head": "songIdToAdd", "content": sid}]))

    def scan(self):
        return requests.get(self.request2("startScan"))

    def getScanStatus(self):
        result = requests.get(self.request2("getScanStatus"))
        result = ET.fromstring(result.text)
        for type in result.findall("scanStatus"):
            return(type.get("scanning") == "true")
                