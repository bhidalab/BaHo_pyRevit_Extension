# -*- coding: utf-8 -*-
import os.path

from System.Diagnostics import Stopwatch

import datetime
import inspect
import sys


def exit_on_error(message):
    """
    Exits current script with provided message.
    :param message:
    :return:
    """
    print("ERROR: {}".format(message))
    sys.exit()


def start_script_timer():
    """
    Starts a timer stopwatch and return ist
    :return:
    """
    stopwatch = Stopwatch()
    stopwatch.Start()
    return stopwatch


def end_script_timer(stopwatch):
    """
    Stops given stopwatch and shows script run time with given script name.
    :param stopwatch:
    :param file_name:
    :return:
    """
    calling_script_path = inspect.stack()[1][1]
    file_name = os.path.split(calling_script_path)[1]
    stopwatch.Stop()
    print("_" * 45)
    print("{} ran in: {}".format(file_name, stopwatch.Elapsed))


def today_iso_date():
    """
    Returns today's date in iso8601 format. e.g. 2023-12-31
    :return:
    """
    return datetime.datetime.now().date().isoformat()


def today_iso_short_date():
    """
    Returns today's date in iso8601 short format. e.g. 20231231 for 2023-12-31
    :return:
    """
    return datetime.datetime.now().date().isoformat().replace("-", "")
