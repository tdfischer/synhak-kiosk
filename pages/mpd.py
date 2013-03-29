import mpd
from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork
from bonehead.ui import Page
from bonehead import Plugin

class MPDPlugin(Plugin):
    def newPage(self, name, args, ui):
        return MPDPage(args['host'], args['port'], args['title'], ui)

class MPDPage(Page):
    def __init__(self, host, port, name, kioskUI):
        super(MPDPage, self).__init__(name, kioskUI)
        self.__host = host
        self.__port = port
        self.__client = mpd.MPDClient()
        self.__client.connect(host, port)

        self.layout = QtGui.QVBoxLayout(self)
        self.__toggle = QtGui.QPushButton(self)
        self.__toggle.clicked.connect(self.toggle)
        self.__next = QtGui.QPushButton("Next", self)
        self.__next.clicked.connect(self.next)
        self.__prev = QtGui.QPushButton("Previous", self)
        self.__prev.clicked.connect(self.next)
        self.__text = QtGui.QLabel(self)
        self.__text.setAlignment(QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.__text)
        self.layout.addWidget(self.__toggle)
        self.layout.addWidget(self.__next)
        self.layout.addWidget(self.__prev)
        self.updateState()

    def next(self):
        self.__client.next()
        self.updateState()

    def prev(self):
        self.__client.prev()
        self.updateState()

    def toggle(self):
        if self.__client.status()['state'] == 'pause':
          self.__client.play()
        else:
          self.__client.pause()
        self.updateState()

    def updateState(self):
      status = self.__client.status()
      song = self.__client.currentsong()
      if status['state'] == 'pause':
        self.__toggle.setText("Play")
      else:
        self.__toggle.setText("Pause")
      if 'title' in song:
        self.__text.setText("%s by %s"%(song['title'], song['artist']))
      else:
        self.__text.setText("Nothing?")

