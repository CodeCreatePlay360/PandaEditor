
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
    
    __demon = -1
    __event_system = -1
    __resource_manager = -1
    
    __args_list = (("demon", "_Editor__demon"),
                   ("event_system", "_Editor__event_system"),
                   ("resource_manager", "_Editor__resource_manager"))
    
    def __new__(cls, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Systems, cls).__new__(cls)
            cls.update(**kwargs)
            # cls.__event_system = kwargs.pop("event_manager", None)
        else:
            print("Tried to instantiate singelton class '{0}' twice.".format("A"))
            
        return cls.instance
        
    def update(**kwargs):
        for val in Systems.__args_list:
            
            arg = val[0]
            attr = val[1]

            if hasattr(Systems, attr):
                setattr(Systems, attr, kwargs.pop(arg, None))
        
    @classproperty
    def demon(self):
        return Systems.__demon
        
    @classproperty
    def event_manager(self):
        return Systems.__event_system
    
    @classproperty
    def resource_manager(self):
        return Systems.__resource_manager
