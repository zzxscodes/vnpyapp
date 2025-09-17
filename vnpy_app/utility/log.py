import datetime
import logging
import os
from contextlib import contextmanager
from logging import config as logging_config
from time import time
from typing import Optional


class Logger:
    def __init__(self, module_name):
        self.module_name = module_name
        # this feature name conflicts with the attribute with Logger
        # rename it to avoid some corner cases that result in comparing `str` and `int`
        self.__level = 0

    @property
    def logger(self):
        logger = logging.getLogger(self.module_name)
        logger.setLevel(self.__level)
        return logger

    def set_level(self, level):
        self.__level = level

    def __getattr__(self, name):
        # During unpickling, python will call __getattr__. Use this line to avoid maximum recursion error.
        if name in {"__setstate__"}:
            raise AttributeError
        return self.logger.__getattribute__(name)


class LoggerManager:
    def __init__(self):
        self._loggers = {}

    def set_level(self, level):
        for logger in self._loggers.values():
            logger.set_level(level)

    def __call__(self, module_name, level: Optional[int] = None) -> Logger:
        """
        Get a logger for a specific module.

        :param module_name: str
            Logic module name.
        :param level: int
        :return: Logger
            Logger object.
        """
        cwd = os.getcwd()
        if not os.path.exists(cwd + '/log'):
            os.makedirs(cwd + '/log')
        if level is None:
            level = logging.NOTSET

        if not module_name.startswith("system."):
            # Add a prefix of qlib. when the requested ``module_name`` doesn't start with ``qlib.``.
            # If the module_name is already qlib.xxx, we do not format here. Otherwise, it will become qlib.qlib.xxx.
            module_name = "system.{}".format(module_name)

        # Get logger.
        module_logger = self._loggers.setdefault(module_name, Logger(module_name))
        module_logger.set_level(level)
        return module_logger


get_module_logger = LoggerManager()


# noinspection PyClassHasNoInit
class TimeInspector:
    timer_logger = get_module_logger("system.timer")

    time_marks = []

    @classmethod
    def set_time_mark(cls):
        """
        Set a time mark with current time, and this time mark will push into a stack.
        :return: float
            A timestamp for current time.
        """
        _time = time()
        cls.time_marks.append(_time)
        return _time

    @classmethod
    def pop_time_mark(cls):
        """
        Pop last time mark from stack.
        """
        return cls.time_marks.pop()

    @classmethod
    def get_cost_time(cls):
        """
        Get last time mark from stack, calculate time diff with current time.
        :return: float
            Time diff calculated by last time mark with current time.
        """
        cost_time = time() - cls.time_marks.pop()
        return cost_time

    @classmethod
    def log_cost_time(cls, info="Done"):
        """
        Get last time mark from stack, calculate time diff with current time, and log time diff and info.
        :param info: str
            Info that will be logged into stdout.
        """
        cost_time = time() - cls.time_marks.pop()
        cls.timer_logger.info("Time cost: {0:.3f}s | {1}".format(cost_time, info))

    @classmethod
    @contextmanager
    def logt(cls, name="", show_start=False):
        """logt.
        Log the time of the inside code

        Parameters
        ----------
        name :
            name
        show_start :
            show_start
        """
        if show_start:
            cls.timer_logger.info(f"{name} Begin")
        cls.set_time_mark()
        try:
            yield None
        finally:
            pass
        cls.log_cost_time(info=f"{name} Done")


def set_log_with_config(log_config: dict):
    """set log with config

    :param log_config:
    :return:
    """
    logging_config.dictConfig(log_config)


_default_logging_config = {
    "logging_config": {
        "version": 1,
        "formatters": {
            "logger_format": {
                "format": "[%(process)s:%(threadName)s](%(asctime)s) %(levelname)s -"
                          " %(name)s - [%(filename)s:%(lineno)d] - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": logging.DEBUG,
                "formatter": "logger_format",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": logging.DEBUG,
                "filename": f"log/{datetime.date.today()}.log",
                "formatter": "logger_format",
            },
        },
        "loggers": {
            "system": {"level": logging.DEBUG, "handlers": ["console", "file"]},
            "user": {"level": logging.DEBUG, "handlers": ["console", "file"]},
        },
        "disable_existing_loggers": False,
    },
}

set_log_with_config(_default_logging_config['logging_config'])
