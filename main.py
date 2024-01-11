import os, sys, pathlib
import argparse
import panda3d.core as p3d


current_script_path = os.path.realpath(__file__)
current_dir = os.path.dirname(current_script_path)
editor_path = os.path.join(current_dir, "src")

sys.path.append(editor_path)

from demon import Demon
import demos
# from exclude.TestClass import TestClass


# command line arguments parser
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--Demo")
parser.add_argument("-ds", "--DefaultScene")
parser.add_argument("-le", "--OpenLE")

# AnimatedCharacter": demos.AnimatedCharacter
samples = {}


class DemonApp(Demon):
    def __init__(self, *args, **kwargs):
        Demon.__init__(self, *args, **kwargs)
        
        # parse input arguments
        args = parser.parse_args()
        
        # load the sample program if specified in input args
        if args.Demo:
            try:
                sample = samples[args.Demo]
            except KeyError:
                print("Sample {0} not found".format(args.Demo))
                sample = None
            finally:
                if sample:
                    self.sample = samples[args.Demo](self.engine)
                    
        # otherwise create a default scene if specified in input args
        elif args.DefaultScene and args.DefaultScene == "DefaultScene":
            self.engine.grid_np.hide()
            self.engine.render.setShaderAuto()
            self.create_default_lights()
            self.setup_scene()
            
            self.engine.cam.move(p3d.LVector3f(0, 280, 0))
            self.engine.cam.orbit(p3d.LVector2f(20, 5))
                
    def on_any_event(self, evt, *args):
        """event sent from c++ side can be handled here"""
        super().on_any_event(evt, args)


app = DemonApp()
app.run()
