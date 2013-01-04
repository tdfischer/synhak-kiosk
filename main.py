#!/usr/bin/env python
import sys
import spiff
import os
from PyQt4 import QtCore, QtGui, QtWebKit
import tempfile
import cups
from mako.template import Template
import subprocess 

api = spiff.API("https://synhak.org/auth/", verify=False)

class Page(QtGui.QWidget):
    def __init__(self, name, parent=None):
        super(Page, self).__init__(parent)
        self.__name = name

    @property
    def name(self):
        return self.__name

    def reset(self):
        pass

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
        self.printButton = QtGui.QPushButton(self)
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
        conn.printFile('QL-700', "%s/out.pdf"%(tempDir), "Label for %s"%(name), {'BrCutLabel':'0', 'PageSize':'29x90','BrMirror':'OFF', 'orientation-requested': '5'})
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
        self.view.loadProgress.connect(self.loadProgress)
        self.view.urlChanged.connect(self.urlChange)


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
        self.view.load(QtCore.QUrl(self.__url))

class EventFilter(QtGui.QApplication):
    def notify(self, object, event):
        if event.type() == QtCore.QEvent.KeyPress or event.type() == QtCore.QEvent.MouseButtonPress:
            resetTimeout()
        return super(EventFilter, self).notify(object, event)

app = EventFilter(sys.argv)

pages = (
    NamebadgePage(),
    WebPage('Wiki', 'http://synhak.org/'),
    WebPage('Spiff', 'https://synhak.org/auth/'),
)

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
