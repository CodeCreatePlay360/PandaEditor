from editor.core.resource import Resource


class TextFile(Resource):
    def __init__(self, path):
        """ Class representing a Runtime User module or Editor plugin """
        Resource.__init__(self, path)

        with open(path, "r", encoding="utf-8") as file:
            readme_text = file.read()
            self.__text = readme_text

    @property
    def text(self):
        return self.__text
