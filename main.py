import os
import sys

current_script_path = os.path.realpath(os.path.realpath(__file__))
current_dir = os.path.dirname(current_script_path)
editor_path = os.path.join(current_dir, "src")

sys.path.append(editor_path)

from editor.app import MyApp

app = MyApp()
app.init()
app.show_base.run()
