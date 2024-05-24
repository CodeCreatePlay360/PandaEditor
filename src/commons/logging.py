import sys
import traceback


def is_msg_ok(msg):
    if not type(msg) is str:
        msg = "ed_logging.log messages must be of type string"
        sys.stdout.write(msg, editor.ui_config.widget_color("_ConsolePanel", "Std_warning_stream_color"))
        return msg
    
    return True


class Logging:
    __ALTERNATING_ERR_STREAM_COLOR = True  # red on true, blue on false
    _blue_color_turn = False
    __last_log_type = -1  # 0=err, 1=warning, 2=log

    @staticmethod
    def log_exception(exception: Exception, extra_msg: str = ""):
        if not is_msg_ok(extra_msg):
            return
        
        # technically, editor should fix or stop immediately after an exception, otherwise I think
        # this is a costly operation

        trace = traceback.format_tb(exception.__traceback__)
        exception = "\n" + "Exception: {0}".format(exception.__str__()[0].upper() + exception.__str__()[1:] + "\n")
        exception += "__traceback__" + "\n"

        for i in range(len(trace)):
            t = "{0} ".format(str(i)) + trace[i].replace(" ", "", 1)  # remove the blank space at start
            exception += t

        if Logging.__ALTERNATING_ERR_STREAM_COLOR:
            if Logging._blue_color_turn:
                txt_color = editor.ui_config.widget_color("_ConsolePanel", "std_err_stream_color_b")
                Logging._blue_color_turn = False
            else:
                txt_color = editor.ui_config.widget_color("_ConsolePanel", "std_err_stream_color_r")
                Logging._blue_color_turn = True

            sys.stderr.write(exception, txt_color)

        else:
            sys.stderr.write(exception)

        Logging.__last_log_type = 0

    @staticmethod
    def log_warning(msg: str):
        if is_msg_ok(msg) is not True:
            return
        
        if Logging.__last_log_type == 0:
            msg = "\n" + msg + "\n"
        else:
            msg += "\n"

        sys.stdout.write(msg, editor.ui_config.widget_color("_ConsolePanel", "Std_warning_stream_color"))
        Logging.__last_log_type = 1

    @staticmethod
    def log(msg: str):
        if is_msg_ok(msg) is not True:
            return
        
        if Logging.__last_log_type == 0:
            msg = "\n" + msg + "\n"
        else:
            msg += "\n"

        sys.stdout.write(msg, editor.ui_config.widget_color("_ConsolePanel", "Std_log_stream_color"))
        Logging.__last_log_type = 2
