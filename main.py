#!/usr/bin/env python
import sys
from PyQt4 import QtCore, QtGui, QtWebKit

class Page(QtGui.QWidget):
    def __init__(self, name, url, parent=None):
        super(Page, self).__init__(parent)
        self.__url = url
        self.__name = name
        self.layout = QtGui.QVBoxLayout(self)
        self.view = QtWebKit.QWebView(self)
        self.view.load(QtCore.QUrl(url))
        self.urlDisplay = QtGui.QLineEdit(self)
        self.urlDisplay.setReadOnly(True)
        self.layout.addWidget(self.urlDisplay)
        self.layout.addWidget(self.view)

        self.view.page().networkAccessManager().sslErrors.connect(self.sslErrors)
        self.view.urlChanged.connect(self.urlChange)

    def sslErrors(self, reply, errors):
        print "SSL Errors:", errors
        reply.ignoreSslErrors()

    def urlChange(self, url):
        self.urlDisplay.setText(url.toString())
        resetTimeout()

    @property
    def name(self):
        return self.__name

    @property
    def url(self):
        return self.__url

    def reset(self):
        self.view.load(QtCore.QUrl(self.__url))

app = QtGui.QApplication(sys.argv)

pages = (
    ('Wiki', 'http://synhak.org/'),
    ('Spiff', 'https://synhak.org/auth/'),
)

def resetTimeout():
    timeout.stop()
    timeout.start()

def updateTimeout(value):
    timeoutBar.setValue(100-(value*100))

widget = QtGui.QWidget()

layout = QtGui.QVBoxLayout(widget)

tabs = QtGui.QTabWidget(widget)
timeout = QtCore.QTimeLine(1000*10, widget)
timeout.valueChanged.connect(updateTimeout)
timeout.finished.connect(timeout.start)
timeout.setCurveShape(QtCore.QTimeLine.LinearCurve)
timeout.start()

for name,url in pages:
    view = Page(name, url, tabs)
    tabs.addTab(view, view.name)
    timeout.finished.connect(view.reset)

timeoutBar = QtGui.QProgressBar(widget)
timeoutBar.setValue(100)
timeoutBar.setMinimum(0)
timeoutBar.setMaximum(100)
timeoutBar.setFormat("Time until reset")

layout.addWidget(tabs)
layout.addWidget(timeoutBar)

widget.showFullScreen()

sys.exit(app.exec_())
