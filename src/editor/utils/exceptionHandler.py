import traceback


def try_execute(func, *args, **kwargs):
    """Try to execute a function, return value is False in case of an exception,
    otherwise True"""

    try:
        func(*args, **kwargs)
    except Exception as exc:
        tb_str = traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__)
        
        print("Exception occurred...!")

        for x in tb_str:
            print(x)
            
        return False

    return True


def try_execute_1(func, *args, **kwargs):
    """Try to execute a function, return value is None in case of an exception,
    otherwise returns the value returned by function"""

    try:
        val = func(*args, **kwargs)
    except Exception as exc:
        tb_str = traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__)

        print("Exception occurred...!")

        for x in tb_str:
            print(x)

        return None

    return val
