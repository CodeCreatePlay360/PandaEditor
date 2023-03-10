from editor.core import RuntimeModule


class TestModule(RuntimeModule):
    def __init__(self, *args, **kwargs):
        RuntimeModule.__init__(self, *args, **kwargs)

        # __init__ should not contain anything except for variable declaration.

    def on_start(self):
        # this method is called only once
        pass

    def on_update(self):
        # this method is called after update
        pass

    def foo(self):
        print("TestModule: Foo")
