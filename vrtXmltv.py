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
        self.inited = True

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
        programme.set("start", str(start).zfill(14) + " +0100")
        programme.set("stop", str(stop).zfill(14) + " +0100")
        programme.set("channel", channel)

        ET.SubElement(programme, "title", lang="nl").text = title

    def output(self):
        tree = ET.ElementTree(self.root)
        tree.write(sys.stdout.buffer)

if __name__ == '__main__':
    sys.stdout.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE tv SYSTEM \"xmltv.dtd\">\n\n")
    now = datetime.now()
    xmlDoc = Xml()
    nowSeconds = now.year*10000000000 + now.month*100000000 + now.day*1000000

    vrts = Vrtnu(now, 0), Vrtnu(now, 1), Vrtnu(now, 2), Vrtnu(now, 3), Vrtnu(now, 4), Vrtnu(now, 5), Vrtnu(now, 6)

    for channel in "xmltv.canvas", "xmltv.een", "xmltv.ketnet":
        for advance in 1, 2, 3, 4, 5, 6:
            if vrts[advance].inited == True:
                programDayAdder = advance * 1000000
                timeTable = vrts[advance].getListForChannel(channel)
                lastStartInDay = 0
                lastStop = 0
                startDayAdder = 0
                for program in timeTable:
                    stopDayAdder = 0
                    startInDay = int(program.get("start").replace(":",""))*100
                    stopInDay = int(program.get("end").replace(":",""))*100

                    if startInDay < lastStartInDay:
                        startDayAdder = 1000000

                    if stopInDay < startInDay:
                        stopDayAdder = 1000000

                    start = nowSeconds + programDayAdder + startInDay + startDayAdder
                    stop = nowSeconds + programDayAdder + stopInDay + startDayAdder + stopDayAdder
                    if start < lastStop:
                        start = lastStop
                    lastStop = stop

                    lastStartInDay = startInDay
                    xmlDoc.addProgramme(start,
                                        stop,
                                        channel,
                                        program.get("title"))

            else:
                if advance == 1:
                    exit(1)

    xmlDoc.output()
    sys.stdout.write("\n")
    exit(0)
