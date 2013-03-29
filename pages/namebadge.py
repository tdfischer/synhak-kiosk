import os
from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork
import cups
import subprocess 
from mako.template import Template
from bonehead.ui import Page
from bonehead import Plugin

class NamebadgePlugin(Plugin):
    def newPage(self, name, args, ui):
        return NamebadgePage(args['printer'], ui)

class NamebadgePage(Page):
    def __init__(self, printer='QL-7000', parent=None):
        super(NamebadgePage, self).__init__('Namebadge', parent)
        self._printer = printer
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
        conn.printFile(self._printer, "%s/out.pdf"%(tempDir), "Label for %s"%(name), {'PageSize':'29x90','BrMirror':'OFF', 'orientation-requested': '5'})
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


