class Systems(object):
    """This class provide a common interface to most common systems
    to avoid repeated imports in individual modules, end users should not
    directly modify these attributes these are set automatically by editor
    or game at time of initialization."""

    class classproperty(object):
        def __init__(self, f):
            self.f = classmethod(f)

        def __get__(self, *a):
            return self.f.__get__(*a)()
        
    demon = None
    win = None
    mw = None
                                
    dr = None
    render = None
    cam = None
                                
    dr2d = None
    render2d = None
    aspect2d = None
    cam2d = None
                                
    evt_mgr = None
    resources = None
    
    coll_trav = None
    
    game = None

    __args_list = (("demon", "demon"),
                   
                   ("win", "win"),
                   ("mw", "mw"),
                   
                   ("dr", "dr"),
                   ("render", "render"),
                   ("cam", "cam"),
                   
                   ("dr2d", "dr2d"),
                   ("render2d", "render2d"),
                   ("aspect2d", "aspect2d"),
                   ("cam2d", "cam2d"),
                   
                   ("evt_mgr", "evt_mgr"),
                   ("resources", "resources"),
                   
                   ("coll_trav", "coll_trav"),
                   
                   ("game", "game"))

    def __new__(cls, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Systems, cls).__new__(cls)
            cls.update(**kwargs)
        else:
            print("Tried to instantiate singleton class '{0}' twice.".format("System"))

        return cls.instance

    @staticmethod
    def update(**kwargs):
        for val in Systems.__args_list:
            arg = val[0]
            attr = val[1]

            if hasattr(Systems, attr):
                setattr(Systems, attr, kwargs.pop(arg, None))
