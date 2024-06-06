from .script import Script

class RuntimeScript(Script):
    def __init__(self, path, name):
        Script.__init__(self, path, name)
