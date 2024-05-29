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
        
        # check if user defined project project path exists,
        # otherwise use default
        if cmd_args.ProjPath:
            assert os.path.exists(cmd_args.ProjPath),\
            "Project path does not exists."
        
        if cmd_args.ProjPath:
            proj_path = cmd_args.ProjPath
        else:
            proj_path = os.path.join(current_dir, "defaultProject")
            
        Demon.__init__(self, proj_path, *args, **kwargs)
                
        # load the demo program if specified in input args
        if cmd_args.Demo:
            demo = None
            try:
                demo = demos[cmd_args.Demo]
            except KeyError:
                print("-- DemoProject '{0}' not found.".format(cmd_args.Demo))
                demo = None
            finally:
                if demo:
                    self.demo = demos[cmd_args.Demo](self.engine)
                    
        if cmd_args.LE and cmd_args.LE == "off":
            print("-- LevelEditor Off")
        else:
            print("-- Starting LevelEditor")
            self.start_level_editor()


app = DemonApp()
app.run()
