import hashlib
import random
import string
import requests
import xmltodict
import html
import urllib.parse
import taglib
import os

class subsonic:
    def __init__(self, base_url, username, password, use_salt=True):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.use_salt = use_salt

    def _make_request(self, url, params={}, method="GET"):
        params["u"] = self.username

        if self.use_salt:
            salt = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            params["t"] = self._get_hashed_password(salt)
            params['s'] = salt


        else:
            params["p"] = self.password

        params["v"] = "1.16.1"
        params["c"] = "subsonicPy"

        encoded_params = {}
        for key, value in params.items():
            encoded_params[key] = urllib.parse.quote(str(value), safe='')

        # Make the HTTP request to the Subsonic API server
        if method == "GET":
            response = requests.get(self.base_url + url, params=params)
        elif method == "POST":
            response = requests.post(self.base_url + url, params=params)

        #print(encoded_params)

        response.raise_for_status()

        data = xmltodict.parse(response.text)
        self._decode_html(data)

        """
        if "subsonic-response" in data and "error" in data["subsonic-response"]:
            raise Exception("API request failed with error: {}".format(data["subsonic-response"]["code"]["@message"]))
        """
        #print(data)
        return data

    def _get_hashed_password(self, salt):
        hash = hashlib.md5((self.password + salt).encode('utf-8'))
        return hash.hexdigest()

    def _decode_html(self, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = html.unescape(value)
                else:
                    self._decode_html(value)
        elif isinstance(data, list):
            for item in data:
                self._decode_html(item)

    def ping(self):
        data = self._make_request("ping")
        if "error" in data:
            return False
        return True

    def getSong(self, id):
        """
        Get details for a song.
        """
        params = {"id": id}
        data = self.make_request("getSong", params)
        if "error" in data:
            raise Exception(f"{data['code']}: {data['@message']}")
        return data["song"]

    def getAlbum(self, id):
        """
        Get details for an album.
        """
        params = {"id": id}
        data = self.make_request("getAlbum", params)
        if "error" in data:
            raise Exception(f"{data['code']}: {data['@message']}")
        return data["album"]

    def getArtist(self, id):
        params = {"id": id}
        data = self.make_request("getArtist", params)
        if "error" in data:
            raise Exception(f"{data['code']}: {data['@message']}")
        return data["artist"]

    def search(self, query, artist_count=None, artist_offset=None, album_count=None, album_offset=None, song_count=None, song_offset=None):
        """
        Search for music.
        """
        params = {"query": query}

        if artist_count is not None:
            params["artistCount"] = artist_count
        if artist_offset is not None:
            params["artistOffset"] = artist_offset
        if album_count is not None:
            params["albumCount"] = album_count
        if album_offset is not None:
            params["albumOffset"] = album_offset
        if song_count is not None:
            params["songCount"] = song_count
        if song_offset is not None:
            params["songOffset"] = song_offset

        data = self._make_request("search2", params)

        if "error" in data:
            raise Exception(f"{data['code']}: {data['@message']}")

        data = data["subsonic-response"]["searchResult2"]

        if not "song" in data.keys():
            data["song"] = []
        if not "album" in data.keys():
            data["album"] = []
        if not "artist" in data.keys():
            data["artist"] = []

        if isinstance(data["song"], dict):
            data["song"] = [data["song"]]
        if isinstance(data["album"], dict):
            data["album"] = [data["album"]]
        if isinstance(data["artist"], dict):
            data["artist"] = [data["artist"]]

        return data

    def createPlaylist(self, name, song_ids=None):
        params = {'name': name}
        if song_ids is not None:
            params['songId'] = song_ids
        data = self._make_request('createPlaylist', params, method='POST')
        if 'error' in data:
            raise Exception(f"{data['code']}: {data['@message']}")
        return True

    def addToPlaylist(self, playlist_id, song_id):
        """
        Add a list of songs to a playlist.
        """
        params = {"playlistId": playlist_id}
        """
        for i, song_id in enumerate(song_ids):
            params[f"songId_{i+1}"] = song_id
        """
        params["songIdToAdd"] = song_id

        data = self._make_request("updatePlaylist", params, method="POST")
        if "error" in data:
            raise Exception(f"{data['code']}: {data['@message']}")
        return True

    def deletePlaylist(self, playlist_id):
        """
        Delete an existing playlist.
        """
        params = {"id": playlist_id}
        data = self._make_request("deletePlaylist", params, method="POST")
        if "error" in data:
            raise Exception(f"{data['code']}: {data['@message']}")
        return True

    def getPlaylist(self, id):
        params = {"id": id}
        data = self.make_request("getPlaylist", params)
        if "error" in data:
            raise Exception(f"{data['code']}: {data['@message']}")
        return data["playlist"]

    def startScan(self):
        """
        Start a new scan for new and changed media files.
        """
        data = self._make_request("startScan", method="POST")
        if "error" in data:
            raise Exception(f"{data['code']}: {data['@message']}")
        return True

    def getScanStatus(self):
        """
        Returns the status of the current scan, or `None` if no scan is in progress.
        """
        data = self._make_request("getScanStatus")
        if "error" in data:
            raise Exception(f"{data['code']}: {data['@message']}")
        if "scanStatus" in data and data["scanStatus"] == "true":
            return True
        return False

    def getUser(self, username):
        """
        Returns a dictionary of the user's details.
        """
        params = {"username": username}
        data = self._make_request("getUser", params)
        if "error" in data:
            raise Exception(f"{data['code']}: {data['@message']}")
        return data["user"]


    def getLyrics(self, song_id):
        # Set the API method and parameters
        method = "getLyrics"
        params = {"id": song_id}

        # Make the API request and parse the response
        response = self.make_request(method, params)
        data = xmltodict.parse(response)

        # Extract the lyrics from the response
        lyrics = data["subsonic-response"]["lyrics"]["lyric"]

        return lyrics

    def getPlaylists(self, username=None):
        params = {}
        if username:
            params['username'] = username
        data = self._make_request('getPlaylists', params, method="POST")

        if data['subsonic-response']['playlists'] == None:
            return []
        elif isinstance(data['subsonic-response']['playlists']["playlist"], dict):
            return [data['subsonic-response']['playlists']["playlist"]]
        else:
            return data['subsonic-response']['playlists']["playlist"] 


        """
        try:
            return data['subsonic-response']['playlists']["playlist"]
        except Exception:
            result = []
            return data['subsonic-response']
        """

    #Unofficial methods


    def findSongId(self, song_name):
        offset = 0
        while True:
            results = self.search(song_name, song_offset=offset)['song']
            
            for song in results:
                if song['@title'] == song_name:
                    return song['@id']

            offset += 20
            if len(results['song']) < 20:
                break
        raise Exception(f"Song '{song_name}' not found")

    def findAlbumId(self, album_name):
        """Searches for an album by name and returns its ID.
        
        Args:
            album_name (str): The name of the album to search for.
            
        Returns:
            str: The ID of the album.
            
        Raises:
            Exception: If the album is not found or if there is an error making the request.
        """
        offset = 0
        while True:
            results = self.search(album_name, album_offset=offset)['album']
            
            for album in results:
                if album['@title'] == album_name:
                    return album['@id']

            offset += 20
            if len(results['album']) < 20:
                break
        raise Exception(f"Album '{album_name}' not found")

    def findArtistId(self, artist_name):
        offset = 0
        while True:
            results = self.search(artist_name, artist_offset=offset)['artist']
            
            for artist in results:
                if artist['@name'] == artist_name:
                    return artist['@id']

            offset += 20
            if len(results['artist']) < 20:
                break
        raise Exception(f"Artist '{artist_name}' not found")

    def findPlaylistId(self, playlist_name, username=None, own=True):
        playlists = self.getPlaylists(username=username)

        for playlist in playlists:
            if playlist['@name'] == playlist_name:
                if (own and playlist["@owner"] == self.username) or not own:
                    return playlist['@id']

        raise Exception("Playlist not found")

    def isSongIdValid(self, songId):
        """
        Returns `True` if the given song ID is valid, `False` otherwise.
        """
        try:
            self.getSong(songId)
            return True
        except Exception:
            return False

    def isAlbumIdValid(self, albumId):
        """
        Returns `True` if the given album ID is valid, `False` otherwise.
        """
        try:
            self.getAlbum(albumId)
            return True
        except Exception:
            return False
        
    def isArtistIdValid(self, artistId):
        try:
            self.getArtist(artistId)
            return True
        except Exception:
            return False

    def isPlaylistIdValid(self, playlistId, username=None):
        """
        Returns `True` if the given playlist ID is valid, `False` otherwise.
        """
        try:
            self.getPlaylist(playlistId, username)
            return True
        except Exception:
            return False

    def isAdmin(self, username):
        """
        Returns `True` if the given user is an admin, `False` otherwise.
        """
        params = {"username": username}
        data = self._make_request("getUser", params)            
#        print(data)
        return data["subsonic-response"]["user"]["@adminRole"]

    def playlist_exists(self, playlist_name, username=None):
        data = self.getPlaylists(username)

        for playlist in data:
            if playlist["@name"] == playlist_name:
                return True

        return False

    def createPlaylistFromM3U(self, m3u_file, replace=False, playlist_name=None, own=True):
        """
        Reads a M3U file and creates a playlist on the server using the taglib
        package to find the title of the song files. If `playlist_name` is not
        provided, the name of the playlist will be the name of the M3U file. If
        `replace` is True and a playlist with the same name already exists, it
        will be replaced with the new playlist. If `replace` is False and a
        playlist with the same name already exists, a new playlist with a unique
        name will be created.
        """
        if playlist_name is None:
            playlist_name = os.path.basename(m3u_file)

        # Check if a playlist with the same name already exists

        if own:
            username = self.username
        else:
            username = None

        if replace and self.playlist_exists(playlist_name, username):
            self.deletePlaylist(playlist_name)
        elif not replace and self.playlist_exists(playlist_name, username):
            playlist_names = self.getPlaylists(username)
            i = 1
            while True:
                new_name = f"{playlist_name} ({i})"
                if new_name not in playlist_names:
                    playlist_name = new_name
                    break
                i += 1

        # Create the new playlist on the server
        self.createPlaylist(playlist_name)
        playlist_id = self.findPlaylistId(playlist_name, username)

        # Read the M3U file and add the songs to the playlist
        with open(m3u_file, "r") as f:
            #print("found")
            for line in f:
                """
                # Skip lines that don't contain song file paths
                if not line.startswith("/"):
                    continue
                """
                # Open the song file and retrieve the title tag
                try:
                    song_file = taglib.File(line.strip())
                    title = song_file.tags["TITLE"][0]

                    # Search for the song by title and add it to the playlist using its ID
                    id = self.findSongId(title)
                    self.addToPlaylist(playlist_id, id)
                except Exception:
                    continue

        return playlist_id