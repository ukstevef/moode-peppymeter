# moode-peppymeter
## Peppymeter integration for moOde audio

Copy **moode.py** and **moodepeppymeter.py** to **/opt/peppymeter**

To activate, edit the file ```~/.xinitrc``` and change the python method to call moodepeppymeter.py
```python
elif [ $PEPPY_SHOW = "1" ]; then
        if [ $PEPPY_TYPE = 'meter' ]; then
                cd /opt/peppymeter && python3 moodepeppymeter.py
        else
                cd /opt/peppyspectrum && python3 spectrum.py
        fi
fi
```

Extended properties can be added to the meter.txt for you chosen screen dimensions.

e.g. **black-white** in the 1280x400-moode folder
```javascript
# --- moode optional entries -------
config.extend = True
albumart.pos = 580,264
albumart.dimension = 130,130
albumart.border = 1
playinfo.title.pos = 10,300,regular
playinfo.title.color = 70,80,90
playinfo.artist.pos = 10,326,regular
playinfo.artist.color = 70,80,90
playinfo.center = True
playinfo.maxwidth = 200
playinfo.type.pos = 1120,40  
playinfo.type.color = 70,80,90
playinfo.type.dimension = 60,60
playinfo.samplerate.pos = 10,360,light
playinfo.samplerate.color = 70,80,90
time.remaining.pos = 580,216
time.remaining.color = 70,80,90
font.size.digi = 28
font.size.light = 16
font.size.regular = 20
font.size.bold = 22
font.color = 70,80,90
```
