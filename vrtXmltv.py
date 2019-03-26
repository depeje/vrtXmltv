#!/usr/bin/python3

import requests
import sys
from datetime import datetime, timedelta
import xml.etree.cElementTree as ET

class Vrtnu:
    _vrt_base_address = "https://www.vrt.be/bin/epg/schedule."
    _vrt_channel_map =  {
                            'xmltv.canvas' : '1H',
                            'xmltv.een': 'O8',
                            'xmltv.ketnet': 'O9',
                        }

    def __init__(self, now, day_offset):
        requestDate = now + timedelta(days=day_offset)

        requestString = self._vrt_base_address\
                     + str(requestDate.year).zfill(4) + "-"\
                     + str(requestDate.month).zfill(2) + "-"\
                     + str(requestDate.day).zfill(2) + ".json"
        response = requests.get(requestString)

        if response.status_code != 200:
            self.inited = False
            return

        self.jsonString = response.json()
        if len(self.jsonString) > 0:
            self.inited = True
        else:
            self.inited = False

    def getListForChannel(self, channel):
        return self.jsonString.get(self._vrt_channel_map.get(channel))

class Xml:
    def __init__(self):
        root = ET.Element("tv")
        self.root = root

        root.set("generator-info-name", "vrt.be/vrtnu")

        channel = ET.SubElement(root, "channel", id="xmltv.een")
        ET.SubElement(channel, "display-name").text = "Een"
        ET.SubElement(channel, "icon", src="http://www.mythportal.be/sites/mythportal.be/files/icons/een.jpg")

        channel = ET.SubElement(root, "channel", id="xmltv.canvas")
        ET.SubElement(channel, "display-name").text = "Canvas"
        ET.SubElement(channel, "icon", src="http://www.mythportal.be/sites/mythportal.be/files/icons/canvas.jpg")

        channel = ET.SubElement(root, "channel", id="xmltv.ketnet")
        ET.SubElement(channel, "display-name").text = "Ketnet"
        ET.SubElement(channel, "icon", src="http://www.mythportal.be/sites/mythportal.be/files/icons/ketnet.jpg")

        channel = ET.SubElement(root, "channel", id="xmltv.sporza")
        ET.SubElement(channel, "display-name").text = "Sporza"
        ET.SubElement(channel, "icon", src="http://www.mythportal.be/sites/mythportal.be/files/icons/canvas.jpg")

    def addProgramme(self, start, stop, channel, title):
        programme = ET.SubElement(self.root, "programme")
        programme.set("start", start)
        programme.set("stop", stop)
        programme.set("channel", channel)

        ET.SubElement(programme, "title", lang="nl").text = title

    def output(self):
        tree = ET.ElementTree(self.root)
        tree.write(sys.stdout.buffer)

if __name__ == '__main__':
    print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE tv SYSTEM \"xmltv.dtd\">\n", flush=True)
    now = datetime.now()
    xmlDoc = Xml()

    advance = 1
    vrt = Vrtnu(now, advance)
    while vrt.inited == True:
        for channel in "xmltv.canvas", "xmltv.een", "xmltv.ketnet":
            timeTable = vrt.getListForChannel(channel)
            lastStop = 0
            for program in timeTable:
                startTime = datetime.strptime(program.get("startTime").replace(":",""), '%Y-%m-%dT%H%M%S%z')
                stopTime = datetime.strptime(program.get("endTime").replace(":",""), '%Y-%m-%dT%H%M%S%z')

                if (lastStop != 0 and startTime < lastStop):
                    startTime = lastStop
                lastStop = stopTime

                xmlDoc.addProgramme(startTime.strftime('%Y%m%d%H%M%S %z').replace(':',''),
                                    stopTime.strftime('%Y%m%d%H%M%S %z').replace(':',''),
                                    channel,
                                    program.get("title"))
        advance = advance + 1
        vrt = Vrtnu(now, advance)

    if advance == 1:
        exit(1)

    xmlDoc.output()
    sys.stdout.write("\n")
    exit(0)
