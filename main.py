#!/usr/bin/env python
import sys
import spiff
import os
from PyQt4 import QtCore, QtGui
import spaceapi
import optparse

from ui import KioskUI
from pages import *

class EventFilter(QtGui.QApplication):
    def __init__(self, argv):
        super(EventFilter, self).__init__(argv)

        parser = optparse.OptionParser()
        parser.add_option('-a', '--spaceapi', help="URL to spaceapi, if one cannot be automatically discovered", default=None)

        (options, args) = parser.parse_args()

        if options.spaceapi:
            spaceAPI = spaceapi.API(options.spaceapi, verify=False)
        else:
            try:
                spaceAPI = spaceapi.Browser().defaultAPI()
            except spaceapi.DiscoveryError:
                spaceAPI = None
        api = None

        if spaceAPI:
            print "Found SpaceAPI:", spaceAPI.apiurl
        else:
            print "No SpaceAPI found."

        self.__ui = KioskUI()

        self.__ui.addPage(NamebadgePage())

        if spaceAPI:
            self.__ui.addPage(WebPage(spaceAPI.name, spaceAPI._data['url']))
            if 'x-spiff-url' in spaceAPI._data:
                print "Found a spiff installation at", spaceAPI._data['x-spiff-url']
                api = spiff.API(spaceAPI._data['x-spiff-url'], verify=False)
                self.__ui.addPage(WebPage('Spiff', spaceAPI._data['x-spiff-url']))
                if 'x-spiff-open-sensor' in spaceAPI._data:
                  self.__ui.addPage(OpenClosePage(api.sensor(spaceAPI._data['x-spiff-open-sensor'])))
            if 'contact' in spaceAPI._data:
                if 'twitter' in spaceAPI._data['contact']:
                    self.__ui.addPage(WebPage('Twitter', 'http://twitter.com/%s'%(spaceAPI._data['contact']['twitter'])))
                
            if 'cam' in spaceAPI._data:
                for webcam in spaceAPI._data['cam']:
                    self.__ui.addPage(WebPage('Webcam', webcam))

        self.__ui.showFullScreen()

    def notify(self, object, event):
        if event.type() == QtCore.QEvent.KeyPress or event.type() == QtCore.QEvent.MouseButtonPress:
            self.__ui.resetTimeout()
        return super(EventFilter, self).notify(object, event)

app = EventFilter(sys.argv)
sys.exit(app.exec_())
