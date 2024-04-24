import argparse
import os
import sys

import panda3d.core as p3d

current_script_path = os.path.realpath(__file__)
current_dir = os.path.dirname(current_script_path)
editor_path = os.path.join(current_dir, "src")
sys.path.append(editor_path)

from demon import Demon
from level_editor import LevelEditor

# from exclude.testTask import TestTask


# command line arguments parser
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--Scene")
parser.add_argument("-le", "--LE")

# AnimatedCharacter": demos.AnimatedCharacter
samples = {}


class DemonApp(Demon):
    def __init__(self, *args, **kwargs):
        Demon.__init__(self, *args, **kwargs)

        self.__evt_map = {}  # evt_map[evt_name] = (call, list_args)

        # parse input arguments
        args = parser.parse_args()
        sample = None

        # load the sample program if specified in input args
        if args.Scene:
            if args.Scene == 'Default':
                pass
            else:
                try:
                    sample = samples[args.Scene]
                except KeyError:
                    print("Sample {0} not found".format(args.Scene))
                    sample = None
                finally:
                    if sample:
                        self.sample = samples[args.Scene](self.engine)

        if args.LE != "Off":
            self.engine.render.setShaderAuto()
            self.create_default_lights()
            # self.setup_scene()
            self.engine.cam.move(p3d.LVector3f(0, 480, 0))
            self.engine.cam.orbit(p3d.LVector2f(20, 5))

            self.__level_editor = LevelEditor(self)

        # test_task = TestTask(name="TestTask")
        # test_task.start(sort=0, late_update_sort=1)
        # print(self.x())

        # -------------------------------------
        # for button events

        # self.accept("a", self.foo)
        # self.accept("a-up", self.foo_up)
        # self.accept("shift-a", self.bar)
        # self.accept("control-alt-a", self.foo_bar)

    def accept(self, evt, callback, *args):
        if not self.__evt_map.__contains__(evt):
            self.__evt_map[evt] = []  # TODO -- replace this with tuple

        self.__evt_map[evt].append((callback, args))

    def on_any_event(self, evt, *args):
        """event sent from c++ side can be handled here"""

        super().on_any_event(evt, *args)

        if evt.name in self.__evt_map.keys():
            res = self.__evt_map[evt.name]

            has_callable_arguments = False

            for i in range(len(res)):
                callback = res[i][0]
                args = res[i][1]

                for j in range(len(args)):
                    if callable(args[j]):
                        has_callable_arguments = True
                        break

                # if we have callables arguments replace them with the result from callable
                if has_callable_arguments:
                    args = tuple(val() if callable(val) else val for val in args)

                if args is not None and len(args) > 0:
                    callback(*args)
                else:
                    callback()


app = DemonApp()
app.run()
