from yapsy.IPlugin import IPlugin

class Plugin(IPlugin):
    def newPage(self, name, args, ui):
        raise NotImplementedError
