from bonehead import Plugin
from bonehead.ui import Page

from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork

class AnonymousJar(QtNetwork.QNetworkCookieJar):
    def clear(self):
        self.setAllCookies([])

class BrowserPlugin(Plugin):
    def newPage(self, name, args, ui):
        return WebPage(args['title'], args['url'], ui)
    
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
        self.resetTimeout()

    @property
    def url(self):
        return self.__url

    def reset(self):
        self.cookies.clear()
        self.view.load(QtCore.QUrl(self.__url))

