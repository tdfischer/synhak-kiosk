#!/usr/bin/env python
import sys
import spiff
import os
from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork
import tempfile
import cups
from mako.template import Template
import subprocess 
import spaceapi
import optparse

class AnonymousJar(QtNetwork.QNetworkCookieJar):
    def clear(self):
        self.setAllCookies([])

class Page(QtGui.QWidget):
    def __init__(self, name, parent=None):
        super(Page, self).__init__(parent)
        self.__name = name

    @property
    def name(self):
        return self.__name

    def reset(self):
        pass

class OpenClosePage(Page):
    def __init__(self, sensor, parent=None):
        super(OpenClosePage, self).__init__('Open/Close Space', parent)
        self.__sensor = sensor
        self.setStyleSheet("*{font-size:32pt}")
        self.layout = QtGui.QVBoxLayout(self)
        self.button = QtGui.QPushButton(self)
        self.text = QtGui.QLabel(self)
        self.text.setAlignment(QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.toggle)
        self.updateButton()

    def toggle(self):
        if self.__sensor.value == True:
            self.__sensor.setValue(False)
        else:
            self.__sensor.setValue(True)
        self.updateButton()

    def updateButton(self):
        if self.__sensor.value == True:
            self.button.setStyleSheet("*{background-color: #f00;}")
            self.button.setText("Close Space")
            self.text.setText("Space is OPEN")
        else:
            self.button.setStyleSheet("*{background-color: #0f0;}")
            self.button.setText("Open Space")
            self.text.setText("Space is CLOSED")

class NamebadgePage(Page):
    def __init__(self, parent=None):
        super(NamebadgePage, self).__init__('Namebadge', parent)
        self.setStyleSheet("*{font-size:32pt}")
        self.layout = QtGui.QVBoxLayout(self)
        self.form = QtGui.QWidget(self)
        self.formLayout = QtGui.QFormLayout(self.form)
        self.nameField = QtGui.QLineEdit(self.form)
        self.doField = QtGui.QLineEdit(self.form)
        self.formLayout.addRow("What is your name?", self.nameField)
        self.formLayout.addRow("What do you do?", self.doField)
        self.badgeCounter = QtGui.QLabel(self.form)
        self.formLayout.addRow("Badges Printed:", self.badgeCounter)
        self.printButton = QtGui.QPushButton("Print it!", self)
        self.printButton.clicked.connect(self.printBadge)
        self.layout.addWidget(self.form)
        self.layout.addWidget(self.printButton)
        self.updateCount()

    def printBadge(self):
        name = self.nameField.text()
        purpose = self.doField.text()
        print "Printing badge for %s, who does '%s'"%(name, purpose)
        self.updateCount(self.badgeCount+1)
        tempDir = tempfile.mkdtemp()
        tempOut = open("%s/out.latex"%(tempDir), 'w')
        template = Template(filename='name-badge.latex')
        tempOut.write(template.render(name=name, purpose=purpose))
        tempOut.close()

        args = ["pdflatex", "-halt-on-error", "%s/out.latex"%(tempDir)]

        subprocess.call(args, cwd=tempDir)

        print "Wrote out.pdf to", tempDir
        conn = cups.Connection()
        conn.printFile('QL-7000', "%s/out.pdf"%(tempDir), "Label for %s"%(name), {'PageSize':'29x90','BrMirror':'OFF', 'orientation-requested': '5'})
        subprocess.call(["flite", "-t", "Hello, %s. Welcome to %s!"%(name, spaceAPI.name)])
        self.reset()

    def updateCount(self, value=None):
        path = os.path.expanduser('~/.local/share/synhak-kiosk/')
        if not os.path.exists(path):
            os.makedirs(path)
        if value is None:
            if not os.path.exists(path+"/badge-count"):
                value = 0
            else:
                try:
                    value = int(open(path+'/badge-count', 'r').read())
                except ValueError:
                    value = 0
        else:
            open(path+'/badge-count', 'w').write(str(value))
        self.badgeCount = value
        self.badgeCounter.setText(str(self.badgeCount))

    def reset(self):
        self.updateCount()
        self.nameField.setText("")
        self.doField.setText("")

class WebPage(Page):
    def __init__(self, name, url, parent=None):
        super(WebPage, self).__init__(name, parent)
        self.__url = url
        self.layout = QtGui.QVBoxLayout(self)
        self.view = QtWebKit.QWebView(self)
        self.view.load(QtCore.QUrl(url))
        self.urlDisplay = QtGui.QLineEdit(self)
        self.urlDisplay.setEnabled(False)
        self.loaderBar = QtGui.QProgressBar(self)
        self.loaderBar.setTextVisible(True)
        self.layout.addWidget(self.urlDisplay)
        self.layout.addWidget(self.loaderBar)
        self.layout.addWidget(self.view)

        self.view.page().networkAccessManager().sslErrors.connect(self.sslErrors)
        self.cookies = AnonymousJar()
        self.view.page().networkAccessManager().setCookieJar(self.cookies)
        self.view.loadProgress.connect(self.loadProgress)
        self.view.urlChanged.connect(self.urlChange)
        self.view.settings().setAttribute(QtWebKit.QWebSettings.PrivateBrowsingEnabled, True)


    def loadProgress(self, progress):
        self.loaderBar.setValue(progress)

    def sslErrors(self, reply, errors):
        print "SSL Errors:", errors
        reply.ignoreSslErrors()

    def urlChange(self, url):
        self.urlDisplay.setText(url.toString())
        resetTimeout()

    @property
    def url(self):
        return self.__url

    def reset(self):
        self.cookies.clear()
        self.view.load(QtCore.QUrl(self.__url))

class EventFilter(QtGui.QApplication):
    def notify(self, object, event):
        if event.type() == QtCore.QEvent.KeyPress or event.type() == QtCore.QEvent.MouseButtonPress:
            resetTimeout()
        return super(EventFilter, self).notify(object, event)

parser = optparse.OptionParser()
parser.add_option('-a', '--spaceapi', help="URL to spaceapi, if one cannot be automatically discovered", default=None)

(options, args) = parser.parse_args()

app = EventFilter(sys.argv)

if options.spaceapi:
    spaceAPI = spaceapi.API(options.spaceapi)
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

pages = [
    NamebadgePage(),
]

if spaceAPI:
    pages.append(WebPage(spaceAPI.name, spaceAPI._data['url']))
    if 'x-spiff-url' in spaceAPI._data:
        print "Found a spiff installation at", spaceAPI._data['x-spiff-url']
        api = spiff.API(spaceAPI._data['x-spiff-url'], verify=False)
        pages.append(WebPage('Spiff', spaceAPI._data['x-spiff-url']))
        if 'x-spiff-open-sensor' in spaceAPI._data:
          pages.append(OpenClosePage(api.sensor(spaceAPI._data['x-spiff-open-sensor'])))
    if 'contact' in spaceAPI._data:
        if 'twitter' in spaceAPI._data['contact']:
            pages.append(WebPage('Twitter', 'http://twitter.com/%s'%(spaceAPI._data['contact']['twitter'])))
        
    if 'cam' in spaceAPI._data:
        for webcam in spaceAPI._data['cam']:
            pages.append(WebPage('Webcam', webcam))

def resetTimeout():
    timeout.stop()
    timeout.start()

def updateTimeout(value):
    timeoutBar.setValue(100-(value*100))

widget = QtGui.QWidget()

layout = QtGui.QVBoxLayout(widget)

tabs = QtGui.QTabWidget(widget)
timeout = QtCore.QTimeLine(1000*10)
timeout.valueChanged.connect(updateTimeout)
timeout.finished.connect(timeout.start)
timeout.setCurveShape(QtCore.QTimeLine.LinearCurve)
timeout.start()

for page in pages:
    tabs.addTab(page, page.name)
    timeout.finished.connect(page.reset)

timeoutBar = QtGui.QProgressBar(widget)
timeoutBar.setValue(100)
timeoutBar.setMinimum(0)
timeoutBar.setMaximum(100)
timeoutBar.setFormat("Time until reset")

layout.addWidget(tabs)
layout.addWidget(timeoutBar)

widget.showFullScreen()

sys.exit(app.exec_())
