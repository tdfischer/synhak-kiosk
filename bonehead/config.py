
class Config(object):
    def __init__(self, path):

    @property
    def pages(self):
        return self

class Page(object):
    def __init__(self, plugin, name, config):
        self._name = name
        self._config = config
        self._plugin = plugin

    def widget(self):
