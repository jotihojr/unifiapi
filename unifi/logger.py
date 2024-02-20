import sys
import os
import io
import traceback
import logging
from enum import IntEnum


class LogLevel(IntEnum):
    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARN
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL


class Logger:
    def __init__(self, name: str, level=LogLevel.DEBUG):
        self.__logger = logging.getLogger(name)
        ch = logging.StreamHandler()
        fh = logging.Formatter(
            datefmt="%FT%T",
            fmt="%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s.%(funcName)s: %(message)s",
        )
        ch.setFormatter(fh)
        self.__logger.addHandler(ch)
        self.__logger.setLevel(level.value)

    def debug(self, *message, stackDepth: int | None = None):
        self.__logger.debug(
            stack_info=isinstance(stackDepth, int),
            stacklevel=0 if stackDepth is None else stackDepth,
            *message,
        )

    def info(self, *message, stackDepth: int | None = None):
        self.__logger.info(
            stack_info=isinstance(stackDepth, int),
            stacklevel=0 if stackDepth is None else stackDepth,
            *message,
        )

    def warn(self, *message, stackDepth: int | None = None):
        self.__logger.warn(
            stack_info=isinstance(stackDepth, int),
            stacklevel=0 if stackDepth is None else stackDepth,
            *message,
        )

    def error(self, *message, stackDepth: int | None = None):
        self.__logger.warn(
            stack_info=isinstance(stackDepth, int),
            stacklevel=0 if stackDepth is None else stackDepth,
            *message,
        )

    def critical(self, *message, stackDepth: int | None = None):
        self.__logger.critical(
            stack_info=isinstance(stackDepth, int),
            stacklevel=0 if stackDepth is None else stackDepth,
            *message,
        )

    def fatal(self, *message, stackDepth: int | None = None):
        self.__logger.fatal(
            stack_info=isinstance(stackDepth, int),
            stacklevel=0 if stackDepth is None else stackDepth,
            *message,
        )

    def setLevel(self, level: LogLevel) -> LogLevel:
        ll = LogLevel(self.__logger.level)
        self.__logger.setLevel(level.value)
        return ll

    def getLevel(self) -> LogLevel:
        return LogLevel(self.__logger.level)


# https://stackoverflow.com/a/58532960
# Get both logger's and this file's path so the wrapped logger can tell when its looking at the code stack outside of this file.
_loggingfile = os.path.normcase(logging.__file__)
if hasattr(sys, "frozen"):  # support for py2exe
    _srcfile = "logging%s__init__%s" % (os.sep, __file__[-4:])
elif __file__[-4:].lower() in [".pyc", ".pyo"]:
    _srcfile = __file__[:-4] + ".py"
else:
    _srcfile = __file__
_srcfile = os.path.normcase(_srcfile)
_wrongCallerFiles = set([_loggingfile, _srcfile])


class WrappedLogger(logging.Logger):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

    # Modified slightly from cpython's implementation https://github.com/python/cpython/blob/master/Lib/logging/__init__.py#L1374
    def findCaller(self, stack_info=False, stacklevel=1):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        f = logging.currentframe()
        if f is None:
            raise ValueError()

        # On some versions of IronPython, currentframe() returns None if
        # IronPython isn't run with -X:Frames.
        orig_f = f
        while f and stacklevel > 1:
            f = f.f_back
            stacklevel -= 1
        if f is None:
            f = orig_f

        rv = "(unknown file)", 0, "(unknown function)", None
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename in _wrongCallerFiles:
                f = f.f_back
                continue
            sinfo = None
            if stack_info:
                sio = io.StringIO()
                sio.write("Stack (most recent call last):\n")
                traceback.print_stack(f, file=sio)
                sinfo = sio.getvalue()
                if sinfo[-1] == "\n":
                    sinfo = sinfo[:-1]
                sio.close()
            rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
            break
        return rv


logging.setLoggerClass(WrappedLogger)
