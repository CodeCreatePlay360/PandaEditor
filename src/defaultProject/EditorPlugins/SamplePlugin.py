import math
import sys
import panda3d.core as p3d_core
from game.resources import EditorPlugin
import traceback


class SamplePlugin(EditorPlugin):
    def __init__(self, *args, **kwargs):
        # __init__ should not contain anything except for field declaration
        EditorPlugin.__init__(self, *args, **kwargs)
        print(1/0)

    def on_start(self):
        # this method is called only once
        # self.foo()
        pass

    def on_update(self):
        # this method is called every frame
        pass

    def foo(self):
        try:
            self.bar()
        except Exception as exception:
            # technically, editor should fix or stop immediately after an exception, otherwise I think
            # this formatted trace back is a costly operation.
            # print(trace)

            trace = traceback.format_tb(exception.__traceback__)
            exception = "\n" + "Exception: {0}".format(exception.__str__()[0].upper() + exception.__str__()[1:] + "\n")

            sys.stderr.write(exception)
            sys.stderr.write("__traceback__" + "\n")

            for i in range(len(trace)):
                t = "{0} ".format(str(i)) + trace[i].replace(" ", "", 1)  # remove the blank space at start
                sys.stderr.write(t)

            sys.stderr.write("\n")

    def bar(self):
        x = 1 / 0
