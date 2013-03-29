from PyQt4 import QtCore, QtGui
import spiff
import os
import spaceapi
import optparse
from ui import KioskUI
from pages import *
from ConfigParser import ConfigParser
from yapsy.PluginManager import PluginManager
import logging

class App(QtGui.QApplication):
    def __init__(self, argv):
        super(App, self).__init__(argv)
        parser = optparse.OptionParser()
        parser.add_option('-c', '--config', help='Path to a configuration', default='/etc/bonehead.cfg')
        (options, args) = parser.parse_args()

        logging.basicConfig(level=logging.DEBUG)

        self._conf = ConfigParser()
        self._conf.read(options.config)

        self._plugins = PluginManager()
        self._plugins.setPluginPlaces([
            '/usr/lib/bonehead/pages',
            './pages/'
        ])

        self._plugins.collectPlugins()

        for plugin in self._plugins.getAllPlugins():
            self._plugins.activatePluginByName(plugin.name)

        self.__ui = KioskUI()

        pages = self._conf.get('general', 'pages', []).split(',')
        for pageName in pages:
            pageConfig = {}
            for k,v in self._conf.items("page:%s"%(pageName)):
                pageConfig[k] = v
            pagePlugin = self._plugins.getPluginByName(pageConfig['plugin'])
            page = pagePlugin.plugin_object.newPage(pageName, pageConfig, self.__ui)
            self.__ui.addPage(page)

        self.__ui.showFullScreen()

    def notify(self, object, event):
        if event.type() == QtCore.QEvent.KeyPress or event.type() == QtCore.QEvent.MouseButtonPress:
            self.__ui.resetTimeout()
        return super(App, self).notify(object, event)

