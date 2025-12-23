#moode utils
import os
import time
import configparser

import threading 
import time
import csv
import html

import requests
import json
import urllib.parse

class moodeCurrentSong:

    CURRENT_ARTIST="artist"
    CURRENT_ALBUM="album"
    CURRENT_TITLE="title"
    CURRENT_TRACK="track"
    CURRENT_COVERURL="coverurl"
    CURRENT_ENCODED="encoded"
    CURRENT_BITRATE="bitrate"
    CURRENT_STATE="state"
    CURRENT_FILE="file"
    CURRENT_OUTRATE="outrate"

    __filename__= r'/var/local/www/currentsong.txt'
    __airplay__= r'/var/local/www/aplmeta.txt'
    __section__ = r'MoOde'
    __last_file__ = None

    artist=""
    album=""
    title=""
    track=""
    coverurl=""
    encoded=""
    bitrate=""
    state=""
    timeRemaining=""

    @classmethod
    def __init__(self):

        mt = os.path.getmtime(self.__filename__)

        if self.__last_file__ != mt:
            __last_file = mt

        # print(f"File updated - {time.ctime(mt)}")
        self.update()

    @classmethod
    def get_FileName(self):
        return self.__filename__

    @classmethod
    def reset(self):
        self.artist=""
        self.album=""
        self.title=""
        self.track=""
        # self.coverurl=""
        self.encoded=""
        self.bitrate=""
        self.state=""
        self.timeRemaining=""

    @classmethod
    def update(self):

        with open(self.__filename__) as f:
            file_content = '['+self.__section__+']\n' + f.read()

        # Parse file using dummy section [MoOde]
        self.__config = configparser.ConfigParser(delimiters='=', interpolation=None)
        self.__config.read_string(file_content)
        self.tags=self.__config[self.__section__]

        try:
            self.file=self.tags[self.CURRENT_FILE]
            if self.file == r"AirPlay Active":
                self.parseAirPlay()
                return
            elif self.file == r"Squeezelite Active":
                try:
                    self.parseSqueezelite()
                except Exception as e:
                    print(f"{e}")
                finally:
                    pass
                return
        except:
            self.file=""

        self.reset()

        # remove html entities
        for item in self.tags:
            self.tags[item] = html.unescape(self.tags[item].rstrip("\n").rstrip("\r"))

            try:
                self.artist=self.tags[self.CURRENT_ARTIST]
            except:
                self.artist=""

            try:
                self.album=self.tags[self.CURRENT_ALBUM]
            except:
                self.album=""

            try:
                self.title=self.tags[self.CURRENT_TITLE]
            except:
                self.title=""

            try:
                self.track=self.tags[self.CURRENT_TRACK]
            except:
                self.track=""

            try:
                self.coverurl=self.tags[self.CURRENT_COVERURL]
            except:
                self.coverurl=""

            try:
                self.encoded=self.tags[self.CURRENT_ENCODED]
            except:
                self.encoded=""

            try:
                self.bitrate=self.tags[self.CURRENT_BITRATE]
            except:
                self.bitrate=""

            try:
                self.state=self.tags[self.CURRENT_STATE]
            except:
                self.state=""

    @classmethod
    def parseSqueezelite(self):

        LMS_HOST = 'truenas.local'
        LMS_PORT = 31101 #default port=9000

        LMS_JSONRPC_URL = f'http://{LMS_HOST}:{LMS_PORT}/jsonrpc.js' 

        # use requests to send json to LMS
        def json_request(player='-', command=''):
            params = command.split()
            cmd = [player, params]
            data = {'method': 'slim.request',
                    'params': cmd}
            r = requests.get(LMS_JSONRPC_URL, json=data, timeout=5)
            return r.json()['result']

        # self.album="Squeezelite Active"
        self.encoded = self.tags[self.CURRENT_OUTRATE] if self.CURRENT_OUTRATE in self.tags else ""

        result = json_request(command='player count ?')
        # print(f"Player Count={result}")

        for x in range(result['_count']):
            result = json_request(command=f"player name {x} ?")

            #moodeutl -q "select value from cfg_sl where param='PLAYERNAME'"
            if result['_name']=="Moode930":
                try:
                    result = json_request(command=f"player id {x} ?")
                    id=result['_id']

                    # https://lyrion.org/reference/cli/database/#songinfo
                    #   a       Artist Name
                    #   c       coverid to use when constructing an artwork URL, such as /music/$coverid/cover.jpg
                    #   K       A full URL to remote artwork. Only available for certain online music services.
                    #   d       Song duration in seconds.
                    #   j       1 if coverart is available for this song. Not listed otherwise.
                    #   J       Identifier of the album track used by the server to display the album's artwork. Not listed if artwork is not available for this album.
                    #   K       A full URL to remote artwork. Only available for certain online music services.
                    #   l       Album name. If known.
                    #   r       Song Bitrate
                    #   t       Track Number
                    #   T       Song sample rate (in KHz)

                    cmd = f"status - 1 tags:acdjJKlrtT"
                    playing = json_request(command=cmd, player=(id))
                    # {'time': 21.3550188865662, 'playlist_timestamp': 1766404251.31806, 'duration': 266.533, 'playlist shuffle': 0, 'randomplay': 0, 'signalstrength': 0, 'mode': 'play',

                    def durationHHMMSS(seconds):
                        return time.strftime("%-M:%S", time.gmtime(seconds))
                    
                    self.timeRemaining = f"{durationHHMMSS(playing['time'])}/{durationHHMMSS(playing['duration'])}"

                    songInfo = playing['playlist_loop'][0] if 'playlist_loop' in playing else None
                    # {'coverart': '1', 'playlist index': 6, 
                    #  'artist': 'Simple Minds', 'artwork_track_id': 'befefd9f', 
                    #  'album': 'Acoustic', 'id': 3129, 'bitrate': '904kbps VBR', 
                    #  'title': 'Waterfront', 'tracknum': '7', 'coverid': 'befefd9f', 
                    #  'duration': 315.866}
                    if songInfo:
                        self.title=songInfo['title']     if 'title'   in songInfo else ""
                        self.album=songInfo['album']     if 'album'   in songInfo else ""
                        self.artist=songInfo['artist']   if 'artist'  in songInfo else ""
                        self.bitrate=f"{songInfo['bitrate'] if 'bitrate' in songInfo else ""} {songInfo['samplerate'] if 'samplerate' in songInfo else ""}" 

                        if 'coverart' in songInfo and 'coverid' in songInfo:
                            self.coverurl=f"http://{LMS_HOST}:{LMS_PORT}/music/{songInfo['coverid']}/cover"    

                except Exception as e:
                    print(f"{e}")
                    pass

        return None
    
    @classmethod
    def parseAirPlay(self):

        with open(self.__airplay__, mode ='r') as f:

            csvFile = csv.reader(f, delimiter="¬")

            for lines in csvFile:

                """ 
                * File is single line, with columns seprated by ~~~
                * e.g.
                *
                It's the Most Wonderful Time of the Year (Album Version)~~~Andy Williams with Robert Mersey & His Orchestra~~~The Andy Williams Christmas Album~~~152570~~~imagesw/airplay-covers/cover-f9ae9fb280db7f25dd5549a5dce05f88.jpg~~~ALAC/AAC
                """
                res = lines[0].split('~~~')

                if len(res)>0:
                    self.title  = res[0] if len(res)>=1 else ""
                    self.artist = res[1] if len(res)>=2 else ""
                    self.album  = res[2] if len(res)>=3 else ""
                    self.coverurl=res[4] if len(res)>=5 else ""
                    self.encoded= res[5] if len(res)>=6 else ""
