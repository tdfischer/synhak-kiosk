from PyQt4 import QtGui, QtCore

class KioskUI(QtGui.QWidget):
    def __init__(self, parent=None):
        super(KioskUI, self).__init__(parent)
        self.__layout = QtGui.QVBoxLayout(self)
        self.__tabs = QtGui.QTabWidget(self)
        self.__tabs.setStyleSheet("*{font-size:16pt}")
        self.__timeout = QtCore.QTimeLine(1000*10)
        self.__timeout.valueChanged.connect(self.__updateTimeout)
        self.__timeout.finished.connect(self.__timeout.start)
        self.__timeout.setCurveShape(QtCore.QTimeLine.LinearCurve)
        self.__timeout.start()
        
        self.__timeoutBar = QtGui.QProgressBar(self)
        self.__timeoutBar.setValue(100)
        self.__timeoutBar.setMinimum(0)
        self.__timeoutBar.setMaximum(100)
        self.__timeoutBar.setFormat("Time until reset")

        self.__layout.addWidget(self.__tabs)
        self.__layout.addWidget(self.__timeoutBar)

    def __updateTimeout(self, value):
        self.__timeoutBar.setValue(100 - (value*100))

    def resetTimeout(self):
        self.__timeout.stop()
        self.__timeout.start()

    def addPage(self, page):
        self.__tabs.addTab(page, page.name)
        self.__timeout.finished.connect(page.reset)
        page.activity.connect(self.resetTimeout)
