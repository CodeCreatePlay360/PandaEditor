import argparse
import os
import sys

import panda3d.core as p3d

current_script_path = os.path.realpath(__file__)
current_dir = os.path.dirname(current_script_path)
editor_path = os.path.join(current_dir, "src")
sys.path.append(editor_path)

from demon import Demon


# command line arguments parser
parser = argparse.ArgumentParser()
parser.add_argument("-demo", "--Demo")
parser.add_argument("-le", "--LE")
parser.add_argument("-projpath", "--ProjPath")

# AnimatedCharacter": demos.AnimatedCharacter
demos = {}


class DemonApp(Demon):    
    def __init__(self, *args, **kwargs):
        
        # parse input arguments
        cmd_args = parser.parse_args()
        
        Demon.__init__(self, cmd_args.ProjPath, *args, **kwargs)
                
        # load the demo program if specified in input args
        if cmd_args.Demo:
            demo = None
            try:
                demo = demos[cmd_args.Scene]
            except KeyError:
                print("-- Demo {0} not found".format(cmd_args.Scene))
                demo = None
            finally:
                if demo:
                    self.demo = demos[cmd_args.Scene](self.engine)
                    
        if cmd_args.LE and cmd_args.LE == "Off":
            print("-- LevelEditor Off")
        else:
            print("-- Starting LevelEditor")
            self.start_level_editor()


app = DemonApp()
app.run()
