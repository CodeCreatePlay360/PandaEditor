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
        Demon.__init__(self, *args, **kwargs)
                
        # parse input arguments
        args = parser.parse_args()
        
        # load the demo program if specified in input args
        if args.Demo:
            demo = None
            try:
                demo = demos[args.Scene]
            except KeyError:
                print("-- Demo {0} not found".format(args.Scene))
                demo = None
            finally:
                if demo:
                    self.demo = demos[args.Scene](self.engine)

        if args.LE and args.LE == "Off":
            print("-- LevelEditor Off")
        else:
            print("-- Starting LevelEditor")
            self.start_level_editor(args.ProjPath)


app = DemonApp()
app.run()
