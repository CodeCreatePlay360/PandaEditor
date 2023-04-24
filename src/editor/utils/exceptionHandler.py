import sys
import traceback


def safe_execute(func, *args, **kwargs):
    return_func_val = kwargs.pop("return_func_val", False)

    try:
        val = func(*args, **kwargs)
    except Exception as e:
        if sys.platform == "linux":
            print(e)
        else:
            tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
            for x in tb_str:
                print(x)

        if return_func_val:
            return None
        else:
            return False

    if return_func_val:
        return val
    else:
        return True


def try_execute(func, *args, **kwargs):
    """Try to execute a function, return value is False in case of an exception,
    otherwise True"""

    try:
        func(*args, **kwargs)
    except Exception as exc:
        tb_str = traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__)
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
