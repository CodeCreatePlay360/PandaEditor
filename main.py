import os
import sys

current_working_dir = os.getcwd()
editor_path = current_working_dir + "\\" + "src"

sys.path.append(editor_path)

from editor.app import MyApp

app = MyApp()
app.init()
app.showbase.run()
