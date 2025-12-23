import os
import sys
import platform
import logging

from datasource import DataSource, SOURCE_NOISE, SOURCE_PIPE, SOURCE_HTTP
from peppymeter import Peppymeter

from configfileparser import *
from moode import moodeCurrentSong

import time
from threading import Lock, Thread
import traceback

import pygame
import requests
from io import BytesIO
from datetime import datetime
from functools import lru_cache
from PIL import Image, ImageOps
import base64
from itertools import cycle
import subprocess
import random

PEPPY_EXTENDED_CONF = "config.extend"

PEPPY_ALBUMART_POS = "albumart.pos"
PEPPY_ALBUMART_DIM = "albumart.dimension"
PEPPY_ALBUMART_MASK = "albumart.mask"
PEPPY_ALBUMBORDER = "albumart.border"

PEPPY_PLAYINFO_CENTER = "playinfo.center"
PEPPY_PLAYINFO_MAX_WIDTH = "playinfo.maxwidth"
PEPPY_PLAYINFO_TYPE_DIM = "playinfo.type.dimension"

PEPPY_PLAYINFO_TITLE = "playinfo.title"
PEPPY_PLAYINFO_TITLE_POS = "playinfo.title.pos"
PEPPY_PLAYINFO_TITLE_DIM = "playinfo.title.dimension"
PEPPY_PLAYINFO_TITLE_COLOR = "playinfo.title.color"
PEPPY_PLAYINFO_TITLE_MAX_WIDTH = "playinfo.title.maxwidth"

PEPPY_PLAYINFO_ARTIST = "playinfo.artist"
PEPPY_PLAYINFO_ARTIST_POS = "playinfo.artist.pos"
PEPPY_PLAYINFO_ARTIST_COLOR = "playinfo.artist.color"
PEPPY_PLAYINFO_ARTIST_MAX_WIDTH = "playinfo.artist.maxwidth"

PEPPY_PLAYINFO_ALBUM = "playinfo.album"
PEPPY_PLAYINFO_ALBUM_POS = "playinfo.album.pos"
PEPPY_PLAYINFO_ALBUM_COLOR = "playinfo.album.color"

PEPPY_PLAYINFO_FONT_DIGI = "font.size.digi"
PEPPY_PLAYINFO_FONT_LIGHT="font.size.light"
PEPPY_PLAYINFO_FONT_REGULAR="font.size.regular"
PEPPY_PLAYINFO_FONT_BOLD="font.size.bold"
PEPPY_PLAYINFO_FONT_COLOR="font.size.color"

PEPPY_PLAYINFO_DIM = 'playinfo.type.dimension'
PEPPY_PLAYINFO_COLOR = 'playinfo.type.color'

PEPPY_PLAYINFO_TIME = "time.remaining"
PEPPY_PLAYINFO_TIME_POS = "time.remaining.pos"
PEPPY_PLAYINFO_TIME_COLOR = "time.remaining.color"

PEPPY_PLAYINFO_SAMPLERATE = "playinfo.samplerate"
PEPPY_PLAYINFO_SAMPLERATE_POS = "playinfo.samplerate.pos"

class moodePeppyConfig(ConfigFileParser):

    def __init__(self, section=None):
        super().__init__()

        c = ConfigParser()

        config_path = "."
        
        config_file_path = os.path.join(config_path, FILE_CONFIG)
        c.read(config_file_path)

        folder = self.meter_config[SCREEN_INFO][METER_FOLDER]

        config_path = "."
        config_file_path = os.path.join(folder, FILE_METER_CONFIG)
    
        m = ConfigParser()
        m.read(config_file_path)

        try:
            self.meter_config[section][PEPPY_EXTENDED_CONF] = m.get(section, PEPPY_EXTENDED_CONF).capitalize()
        except:
            self.meter_config[section][PEPPY_EXTENDED_CONF] = "False"

        try:
            self.meter_config[section][PEPPY_ALBUMART_POS] = m.get(section, PEPPY_ALBUMART_POS)
        except:
            self.meter_config[section][PEPPY_ALBUMART_POS] = None

        try:
            self.meter_config[section][PEPPY_ALBUMART_DIM] = m.get(section, PEPPY_ALBUMART_DIM)
        except:
            self.meter_config[section][PEPPY_ALBUMART_DIM] = None

        try:
            self.meter_config[section][PEPPY_ALBUMBORDER] = m.get(section, PEPPY_ALBUMBORDER)
        except:
            self.meter_config[section][PEPPY_ALBUMBORDER] = None

        try:
            self.meter_config[section][PEPPY_ALBUMART_MASK] = m.get(section, PEPPY_ALBUMART_MASK)
        except:
            self.meter_config[section][PEPPY_ALBUMART_MASK] = None

        try:
            self.meter_config[section][PEPPY_PLAYINFO_ALBUM_POS] = m.get(section, PEPPY_PLAYINFO_ALBUM_POS)
        except:
            self.meter_config[section][PEPPY_PLAYINFO_ALBUM_POS] = None

        try:
            self.meter_config[section][PEPPY_PLAYINFO_ALBUM_COLOR] = m.get(section, PEPPY_PLAYINFO_ALBUM_COLOR)
        except:
            self.meter_config[section][PEPPY_PLAYINFO_ALBUM_COLOR] = (0,0,0)
            
        try:
            self.meter_config[section][PEPPY_PLAYINFO_FONT_BOLD] = m.get(section, PEPPY_PLAYINFO_FONT_BOLD)
        except:
            self.meter_config[section][PEPPY_PLAYINFO_FONT_BOLD] = None
            
        try:
            self.meter_config[section][PEPPY_PLAYINFO_FONT_DIGI] = m.get(section, PEPPY_PLAYINFO_FONT_DIGI)
        except:
            self.meter_config[section][PEPPY_PLAYINFO_FONT_DIGI] = None
            
        try:
            self.meter_config[section][PEPPY_PLAYINFO_FONT_LIGHT] = m.get(section, PEPPY_PLAYINFO_FONT_LIGHT)
        except:
            self.meter_config[section][PEPPY_PLAYINFO_FONT_LIGHT] = None

        try:
            self.meter_config[section][PEPPY_PLAYINFO_FONT_REGULAR] = m.get(section, PEPPY_PLAYINFO_FONT_REGULAR)
        except:
            self.meter_config[section][PEPPY_PLAYINFO_FONT_REGULAR] = None

        try:
            self.meter_config[section][PEPPY_PLAYINFO_FONT_COLOR] = m.get(section, PEPPY_PLAYINFO_FONT_COLOR)
        except:
            self.meter_config[section][PEPPY_PLAYINFO_FONT_COLOR] = None

        try:
            self.meter_config[section][PEPPY_PLAYINFO_TITLE_POS] = m.get(section, PEPPY_PLAYINFO_TITLE_POS)
        except:
            self.meter_config[section][PEPPY_PLAYINFO_TITLE_POS] = None

        try:
            self.meter_config[section][PEPPY_PLAYINFO_TITLE_COLOR] = m.get(section, PEPPY_PLAYINFO_TITLE_COLOR)
        except:
            self.meter_config[section][PEPPY_PLAYINFO_TITLE_COLOR] = (0,0,0)

        try:
            self.meter_config[section][PEPPY_PLAYINFO_TITLE_MAX_WIDTH] = int(m.get(section, PEPPY_PLAYINFO_TITLE_MAX_WIDTH))
        except:
            self.meter_config[section][PEPPY_PLAYINFO_TITLE_MAX_WIDTH] = None

        try:
            self.meter_config[section][PEPPY_PLAYINFO_ARTIST_POS] = m.get(section, PEPPY_PLAYINFO_ARTIST_POS)
        except:
            self.meter_config[section][PEPPY_PLAYINFO_ARTIST_POS] = None

        try:
            self.meter_config[section][PEPPY_PLAYINFO_ARTIST_COLOR] = m.get(section, PEPPY_PLAYINFO_ARTIST_COLOR)
        except:
            self.meter_config[section][PEPPY_PLAYINFO_ARTIST_COLOR] = (0,0,0)

        try:
            self.meter_config[section][PEPPY_PLAYINFO_ARTIST_MAX_WIDTH] = int(m.get(section, PEPPY_PLAYINFO_ARTIST_MAX_WIDTH))
        except:
            self.meter_config[section][PEPPY_PLAYINFO_ARTIST_MAX_WIDTH] = None

        try:
            self.meter_config[section][PEPPY_PLAYINFO_CENTER] = m.get(section, PEPPY_PLAYINFO_CENTER).capitalize()=="True"
        except:
            self.meter_config[section][PEPPY_PLAYINFO_CENTER] = False

        try:
            self.meter_config[section][PEPPY_PLAYINFO_MAX_WIDTH] = int(m.get(section, PEPPY_PLAYINFO_MAX_WIDTH))
        except:
            self.meter_config[section][PEPPY_PLAYINFO_MAX_WIDTH] = None

        try:
            self.meter_config[section][PEPPY_PLAYINFO_DIM] = m.get(section, PEPPY_PLAYINFO_DIM)
        except:
            self.meter_config[section][PEPPY_PLAYINFO_DIM] = None

        try:
            self.meter_config[section][PEPPY_PLAYINFO_TIME_POS] = m.get(section, PEPPY_PLAYINFO_TIME_POS)
        except:
            self.meter_config[section][PEPPY_PLAYINFO_TIME_POS] = None

        try:
            self.meter_config[section][PEPPY_PLAYINFO_COLOR] = m.get(section, PEPPY_PLAYINFO_COLOR)
        except:
            self.meter_config[section][PEPPY_PLAYINFO_COLOR] = None

        try:
            self.meter_config[section][PEPPY_PLAYINFO_TIME_COLOR] = m.get(section, PEPPY_PLAYINFO_TIME_COLOR)
        except:
            self.meter_config[section][PEPPY_PLAYINFO_TIME_COLOR] = None

        try:
            self.meter_config[section][PEPPY_PLAYINFO_SAMPLERATE_POS] = m.get(section, PEPPY_PLAYINFO_SAMPLERATE_POS)
        except:
            self.meter_config[section][PEPPY_PLAYINFO_SAMPLERATE_POS] = None

class infoItem():

    screen_bgr = None

    def __init__(self, value, pos, font=None, color=(random.randint(1,255), random.randint(1,255), random.randint(1,255)), bgColor=None):
        self.__pos=pos
        self.__value=value
        self.__color=color
        self.__offset = 0
        self.__pause = 0
        self.__font = font if font else pygame.font.SysFont(None,32)
        self.__charWidth = self.getImageText('w', False, self.__color).get_width()
        self.__imgText = self.getImageText(self.__value, True, self.__color, bgColor)
        self.__imgWidth = self.__imgText.get_width()
        self.__imgHeight = self.__imgText.get_height()
        self.__width = 200
        self.__centred = False

    def setWidth(self, width) -> int:
        self.__width=width

    def setCentred(self, value) -> bool:
        self.__centred=value

    def setBackground(self, img):
        infoItem.screen_bgr=img

    def getValue(self):
        return self.__value
    
    def setText(self, value):
        self.__value=value
        self.__imgText = self.__font.render(self.__value, True, self.__color)
        self.__imgWidth = self.__imgText.get_width()
        self.__imgHeight = self.__imgText.get_height()

    @lru_cache(maxsize=100, typed=True)
    def getImageText(self, value, aa, color, bgColor=None):
        self.__imgText = self.__font.render(value, aa, color, bgColor)
        return self.__imgText

    def setTime(self):
        # self.setText(f"{datetime.today().strftime('%H:%M:%S.%f')[:-3]}")
        self.setText(f"{datetime.today().strftime('%H:%M:%S')}")
        self.draw()

    def draw(self):

        __screen = pygame.display.get_surface()
        
        @lru_cache(maxsize=10)
        def imageClip(surface, x, y, w, h):
            if surface:
                clipSurface = surface.copy()
                clipSurface.set_clip(pygame.Rect(x,y,w,h))
                clipImage = surface.subsurface(clipSurface.get_clip())
                return clipImage.copy()

        def repaintBackground():
            # Get clipped background to erase text at that position
            cached_image=infoItem.screen_bgr
            background = imageClip(cached_image, self.__pos[0],self.__pos[1], self.__width, self.__imgHeight)
            if background:
                __screen.blit(background,self.__pos)

        # Pause scroll, then reset scroll position
        if self.__pause:
            self.__pause -= 1
            if self.__pause==1:
                self.__offset=0
                repaintBackground()
            return None
        else:
            repaintBackground()

        # Check if need to scroll value
        if self.__imgWidth > self.__width:
            if self.__offset > self.__imgWidth - self.__width: 
                self.__offset= self.__imgWidth - self.__width
                self.__pause= 6

        # copy the part of the screen
        rect = pygame.Rect(self.__offset, 0, self.__imgWidth-self.__offset if self.__imgWidth-self.__offset < self.__width else self.__width, self.__imgHeight)
        sub = self.__imgText.subsurface(rect)
        
        if self.__centred:                
            w = self.__width if self.__width and self.__width > 0 else sub.get_width()
            xPos= (self.__pos[0] + int((w - sub.get_width())/2), self.__pos[1])
            __screen.blit(sub, xPos)
        else:
            __screen.blit(sub, self.__pos)

        # advance scroll position by one character
        if self.__imgWidth > self.__width:
            self.__offset += self.__charWidth

class moodePeppyMeter(Peppymeter):

    __version = "0.1"
    currentMeter=""
    loadedFonts={}

    item_Album=None
    item_Artist=None
    item_Title=None
    item_Time=None
    item_SampleRate=None

    def __init__(self, util=None, standalone=False, timer_controlled_random_meter=True, quit_pygame_on_stop=True):
        
        self.machine = platform.machine()
        self.song = moodeCurrentSong()
        
        super().__init__(util, standalone, timer_controlled_random_meter, quit_pygame_on_stop)

        self.screen = None

    def start_display_output(self):
        return super().start_display_output()

    def stop(self):
        return super().stop()
    
    def get_CurrentSong(self):

        lock.acquire()
        try:
            __x = moodeCurrentSong()

            if __x.file == r"AirPlay Active":
                self.song = __x
            elif __x.file == r"Squeezelite Active":
                self.song = __x
            elif __x != self.song:
                self.song = __x
            
            # self.print_moode()
        
            lock.release()

        except Exception as e:
            print(f"{e}")
            pass

    def get_activeMeter(self):
        return self.meter.meter

    def get_activeConfig(self):
        config=self.get_activeMeter().meter_config
        return config
    
    def get_meterName(self):    
        config=self.get_activeConfig()
        return config[METER]
   
    @lru_cache(maxsize=100)
    def config_rgb(self, value) -> tuple:
        try:
            rgb = value.split(",")
            rgb = ( int(rgb[0]), int(rgb[1]), int(rgb[2])  )
        except:
            rgb = ( 128,128,128 )
        return rgb

    @lru_cache(maxsize=100)
    def config_xyw(self, value) -> tuple:
        try:
            xyf = value.split(",")
            if len(xyf)==3:
                xyf = ( int(xyf[0]), int(xyf[1]), xyf[2] )
            elif len(xyf)==2:
                xyf = ( int(xyf[0]), int(xyf[1]) )
            else:
                xyf=None
        except:
            xyf = None

        return xyf
    
    def get_Background(self) -> pygame.surface:

        activeMeter=self.get_activeMeter()
        config=self.get_activeConfig()

        if activeMeter.meter_parameters[SCREEN_BGR]:
            fname = activeMeter.meter_parameters[SCREEN_BGR]
        elif activeMeter.meter_parameters[BGR_FILENAME]:
            fname = activeMeter.meter_parameters[BGR_FILENAME]
        else:
            fname=""
        
        if len(fname)>0:
            path = os.path.join(config[BASE_PATH], config[SCREEN_INFO][METER_FOLDER], fname)
            if path in activeMeter.util.image_cache:
                return activeMeter.util.image_cache[path]

    def print_text(self, meter_cfg, value, digital=False):

        # playinfo.center = False
        # playinfo.maxwidth = 290
        # playinfo.title.pos = 354,280,bold
        # font.size.digi = 40
        # font.size.light = 15
        # font.size.regular = 20
        # font.size.bold = 25
        # font.color = 238,234,202

        def setFont(fontname,fw):
            if (fontname,fw) in self.loadedFonts:
                font=self.loadedFonts[(fontname,fw)]
            else:
                font=pygame.font.SysFont(fontname,fw)
                self.loadedFonts[(fontname,fw)]=font
            return font

        # if not value in meter_cfg:
        #     return None
        
        # set default font size
        fw = 32 if digital else 12

        _x_, _y_ = None, None
            
        try:
            xyw = self.config_xyw(meter_cfg[f"{value}.pos"])
        except:
            xyw = None

        if xyw:
            _x_ , _y_ = int(xyw[0]), int(xyw[1])

            try:
                if digital:
                    fw = int(meter_cfg[PEPPY_PLAYINFO_FONT_DIGI])
                else:
                    if len(xyw) > 2:
                        fw = int(meter_cfg[f"font.size.{xyw[2]}" ])
            except:
                pass

        try:
            c = meter_cfg[PEPPY_PLAYINFO_CENTER] == True if PEPPY_PLAYINFO_CENTER in meter_cfg else False
        except:
            c = False

        try:
            rgb = self.config_rgb(meter_cfg[f"{value}.color"])
        # except:
        #     rgb = self.config_rgb(meter_cfg[PEPPY_PLAYINFO_COLOR])
        except:
            rgb = self.config_rgb(None)


        # Cache font creation
        if self.machine == 'aarch64':
            fontname = 'freemono' if digital else 'freesanserif'
        else:
            fontname = 'Digital-7' if digital else 'freesanserif'
        font = setFont(fontname,fw)

        activeMeter=self.get_activeMeter()
        bg = activeMeter.meter_parameters[PEPPY_PLAYINFO_FONT_COLOR] if PEPPY_PLAYINFO_FONT_COLOR in activeMeter.meter_parameters else (0,0,0)

        # PEPPY_PLAYINFO_TITLE_DIM
        try:
            dim = self.config_xyw(meter_cfg[PEPPY_PLAYINFO_TYPE_DIM])
        except:
            dim = None

        if dim and len(dim)>=2:
            _yDim = int(dim[1])
        else:
            _yDim = 0

        if _y_ and font.get_height() < _yDim:
            _y_ += int((_yDim-font.get_height())/2)

        if value == METER:
            str = self.get_meterName()
            self.item_Meter = infoItem(str, (0,0), font, (255,255,0), None if self.get_Background() else bg)
            self.item_Meter.setBackground(self.get_Background())
            self.item_Meter.draw()

        if xyw:
            if value == PEPPY_PLAYINFO_ALBUM:
                str=self.song.album
                if self.item_Album and str!=self.item_Album.getValue():
                   self.item_Album=None 
                if self.item_Album==None:
                    self.item_Album = infoItem(self.song.album, (_x_,_y_), font, rgb, None if self.get_Background() else bg)
                    self.item_Album.setBackground(self.get_Background())
                if self.item_Album:
                    self.item_Album.setWidth(meter_cfg[PEPPY_PLAYINFO_MAX_WIDTH])
                    self.item_Album.draw()

            elif value == PEPPY_PLAYINFO_ARTIST:
                str=self.song.artist
                if self.item_Artist and str!=self.item_Artist.getValue():
                   self.item_Artist=None 
                if self.item_Artist==None:
                    self.item_Artist = infoItem(self.song.artist, (_x_,_y_), font, rgb, None if self.get_Background() else bg)
                    self.item_Artist.setBackground(self.get_Background())
                if self.item_Artist:
                    self.item_Artist.setWidth(meter_cfg[PEPPY_PLAYINFO_MAX_WIDTH])
                    self.item_Artist.draw()

            elif value == PEPPY_PLAYINFO_TITLE:
                str=self.song.title
                if self.item_Title and str!=self.item_Title.getValue():
                   self.item_Title=None 
                if self.item_Title==None:
                    self.item_Title = infoItem(self.song.title, (_x_,_y_), font, rgb,None if self.get_Background() else bg)
                    self.item_Title.setBackground(self.get_Background())
                if self.item_Title:
                    self.item_Title.setWidth(meter_cfg[PEPPY_PLAYINFO_MAX_WIDTH])
                    self.item_Title.draw()

            elif value == PEPPY_PLAYINFO_SAMPLERATE:
                str=f"{self.song.encoded}"# "{self.song.bitrate}"
                if self.item_SampleRate==None:
                    self.item_SampleRate = infoItem(str, (_x_,_y_), font, rgb,None if self.get_Background() else bg)
                    self.item_SampleRate.setBackground(self.get_Background())
                if self.item_SampleRate:
                    self.item_SampleRate.setWidth(meter_cfg[PEPPY_PLAYINFO_MAX_WIDTH])
                    self.item_SampleRate.draw()

            elif value == PEPPY_PLAYINFO_TIME:

                if self.song.file == r"Squeezelite Active" and len(self.song.timeRemaining)>0:
                    str=self.song.timeRemaining
    
                elif self.machine == 'aarch64':
                    # Running on a Pi ? If so, ask MPD for time string
                    str=subprocess.run(["mpc status|head -2|tail -1|tr -s '[:space:]'|cut -d' ' -f 3"], capture_output=True, text=True, shell=True, executable="/bin/bash").stdout.rstrip('\r\n')
                    if str.rstrip('\n')=="off":
                        str=f"{datetime.now().strftime('%H:%M:%S')}"
                else:
                    str=f"{datetime.now().strftime('%H:%M:%S')}"

                scale = 1 if len(str)<=6 else (6.0/len(str)) 
                if scale != 1:
                    fw = int(int(activeMeter.meter_parameters[PEPPY_PLAYINFO_FONT_DIGI] if PEPPY_PLAYINFO_FONT_DIGI in activeMeter.meter_parameters else fw) * scale)
                    font = setFont(fontname,fw)

                self.item_Time = infoItem(str, (_x_,_y_), font, rgb, None if self.get_Background() else bg)
                self.item_Time.setBackground(self.get_Background())
                self.item_Time.setWidth(meter_cfg[PEPPY_PLAYINFO_MAX_WIDTH])
                self.item_Time.setCentred(False)
                self.item_Time.draw()

            else:
                str = f"{value}"

            
    @lru_cache(maxsize=10, typed=True)
    def get_album(self, url) -> pygame.Surface:

        response=None

        if url=="": url="images/default-album-cover.png" 

        if url.startswith("http"):
            uri=url
        else:
            # remove leading / in url string
            url = url.lstrip(r'/')

            if self.machine == 'aarch64':
                # Running on a Raspberry Pi
                uri=f"http://localhost/{url}"
            else:
                # Testing from my laptop
                uri=f"http://moode930.local/{url}"
        
        # print(uri)
        img=None

        try:
            response = requests.get(uri, timeout=3)
        except requests.ConnectionError as e:
            print(f"connect error {e}")
        except requests.ConnectTimeout as e:
            print(f"connect timeout {e}")
        finally:
            pass

        if response:
            img = pygame.image.load(BytesIO(response.content))
        elif self.machine != 'aarch64':
            img = pygame.image.load("../moode/build/develop/images/default-album-cover.png")
            
        return img #if response else None
    
    def draw_album(self, meter_cfg, url):

        if not self.screen:
            exit

        # Fetch album art size and position 
        #   
        # albumart.pos = 1203,33
        # albumart.dimension = 252,252
        # albumart.border = 1

        xyw = self.config_xyw(meter_cfg[PEPPY_ALBUMART_POS])
        dim = meter_cfg[PEPPY_ALBUMART_DIM]

        if xyw and dim:
            img = self.get_album(url)

            if img:
                wh = dim.split(",")
                if len(wh)>=2:
                    _w_ , _h_= int(wh[0]),int(wh[1])
                    resized_image = pygame.transform.smoothscale(img, (_w_, _h_ ))
                else:
                    resized_image = img#.copy()

                _x_ = int(xyw[0])
                _y_ = int(xyw[1])
                _r_ = pygame.rect.Rect(_x_, _y_, _w_, _h_)

                # mask image if png mask set
                try:
                    if PEPPY_ALBUMART_MASK in meter_cfg and meter_cfg[PEPPY_ALBUMART_MASK]:

                        mask_image=None
                        format = r'RGBA'

                        # Fetch mask from folder path
                        config = self.get_activeConfig()
                        mpath = os.path.join(config[BASE_PATH], config[SCREEN_INFO][METER_FOLDER], meter_cfg[PEPPY_ALBUMART_MASK])
                        mask_image = Image.open(mpath).convert('L')
                        # mask_image = pygame.image.load(mpath).convert_alpha()

                        def inverted(img):
                            inv = pygame.Surface(img.get_rect().size, pygame.SRCALPHA)
                            inv.fill((255,255,255,255))
                            inv.blit(img, (0,0), None, pygame.BLEND_RGB_SUB)
                            return inv

                        if mask_image:
                            imgSize = (_w_, _h_)

                            if mask_image.size != imgSize:
                                mask_image = mask_image.resize(imgSize)
                                                
                            # img5 = inverted(mask_image)
                            # img5 = pygame.transform.smoothscale(mask_image, imgSize)
                            
                            img2 = Image.frombuffer('L', imgSize, resized_image.get_buffer())
                            img2.putalpha(ImageOps.invert(mask_image))

                            img3=img2.convert(format)

                            raw_str = img3.tobytes(r'raw', format)
                            img4 = pygame.image.fromstring(raw_str, (_w_, _h_), format)

                            # img5 = pygame.transform.smoothscale(img4, imgSize)

                            self.screen.blit(img4 ,(_x_, _y_))
                            pygame.display.update(_r_)

                    else:
                        # Image - no Mask
                        self.screen.blit(resized_image, (_x_, _y_))

                        # Draw Border if required
                        albumBorder=meter_cfg[PEPPY_ALBUMBORDER] if PEPPY_ALBUMBORDER in meter_cfg else None 
                        if albumBorder:
                            try:
                                rgb = self.config_rgb(meter_cfg[PEPPY_PLAYINFO_COLOR])
                            except:
                                rgb = self.config_rgb(None)
    
                            pygame.draw.rect(self.screen, rgb, _r_, int(albumBorder))

                        pygame.display.update(_r_)

                except Exception as e:
                    print(f"{e}")
                    pass
               
    def every(self, delay, task):
        next_time = time.time() + delay
        while True:
            time.sleep(max(0, next_time - time.time()))

            try:
                task()
            except Exception:
                traceback.print_exc()

            next_time += (time.time() - next_time) // delay * delay + delay

    def keypress(self):

        bExit = False
        
        try:
            if self.machine == 'aarch64':
                if pygame.mouse.get_pressed(num_buttons=3)[0]: 
                    print("Mouse pressed")
                    bExit=True
            else:
                keys=pygame.key.get_pressed()

                if keys[pygame.K_q]:
                    print("Key Q pressed")
                    bExit=True

        except Exception as e:
            print(e)

        finally:
            pass

        if bExit:
            try:
                str=subprocess.run(["sudo moodeutl --setdisplay webui"], capture_output=True, text=True, shell=True, executable="/bin/bash")                
            finally:
                sys.exit()
        return
    
    def print_moode(self):
        try:
            global currentMeter

            activeMeter=self.get_activeMeter()
            config=self.get_activeConfig()
            meter_name = config[METER]

            if activeMeter:

                if currentMeter:

                    if currentMeter != meter_name:
                        # Meter change - draw background image
                        if activeMeter.meter_parameters[SCREEN_BGR]:

                            fname = activeMeter.meter_parameters[SCREEN_BGR]
                            if len(fname)>0:
                                path = os.path.join(config[BASE_PATH], config[SCREEN_INFO][METER_FOLDER], fname)
                                if path in activeMeter.util.image_cache:
                                    img=activeMeter.util.image_cache[path]
                                    self.screen.blit(img,(0,0))

                        if self.item_Album: 
                            del self.item_Album
                            self.item_Album=None
                        if self.item_Artist:
                            del self.item_Artist
                            self.item_Artist=None
                        if self.item_Title:
                            del self.item_Title
                            self.item_Title=None
                        if self.item_Time:
                            del self.item_Time
                            self.item_Time=None
                        if self.item_SampleRate:
                            del self.item_SampleRate
                            self.item_SampleRate=None

                        currentMeter = meter_name
                        exit

            if self.screen:
                
                # Debug
                pygame.display.set_caption(f"Meter - {meter_name}")

                cfg = moodePeppyConfig(meter_name)
                meter_cfg = cfg.meter_config[meter_name]

                if meter_cfg[PEPPY_EXTENDED_CONF]=="True":
                    
                    if self.get_meterName()==currentMeter: 
                        self.print_text(meter_cfg, PEPPY_PLAYINFO_TIME, True)
                        self.draw_album(meter_cfg, self.song.coverurl)
                        self.print_text(meter_cfg, PEPPY_PLAYINFO_ALBUM)
                        self.print_text(meter_cfg, PEPPY_PLAYINFO_ARTIST)
                        self.print_text(meter_cfg, PEPPY_PLAYINFO_TITLE)
                        self.print_text(meter_cfg, PEPPY_PLAYINFO_SAMPLERATE)

            currentMeter = meter_name            

        except Exception as e:
            print(f"{e}")
            pass

if __name__ == "__main__":

    currentMeter = ""
    lock = Lock()

    pm = moodePeppyMeter(standalone=True)
    source = pm.util.meter_config[DATA_SOURCE][TYPE]

    if source == SOURCE_HTTP:
        try:
            f = open(os.devnull, 'w')
            sys.stdout = sys.stderr = f
            from webserver import WebServer
            web_server = WebServer(pm)
        except Exception as e:
            logging.debug(e)

    if source != SOURCE_PIPE:
        pm.data_source.start_data_source()
        
    # Show Meter
    pm.init_display()

    pm.screen = pm.util.PYGAME_SCREEN
    
    # info=pygame.display.Info()
    # print(pygame.font.get_fonts())
    # print(f"Platform={sys.platform}, Ver={sys.version}, uname={platform.node()}")

    # Show Moode Information
    if pm.util.meter_config[OUTPUT_DISPLAY]:

        rt1 = Thread(target=lambda: pm.every(0.333, pm.get_CurrentSong)).start()
        rt2 = Thread(target=lambda: pm.every(0.333, pm.print_moode)).start()
        rt3 = Thread(target=lambda: pm.every(0.250, pm.keypress)).start()

        try:
            pm.start_display_output()

        finally:
            # rt.stop()
            if rt1:
                rt1.join()
            if rt2:
                rt2.join()
            if rt3:
                rt3.join()
