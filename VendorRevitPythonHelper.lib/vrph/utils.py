# -*- coding: utf-8 -*-
import os.path

from System.Diagnostics import Stopwatch

import datetime
import inspect
import sys
import re


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


def get_latest_file_in_dir_by_iso_date_and_extension(search_dir, extension):
    """
    Attempts to retrieve the file with the latest iso short YYYYMMDD timestamp as file name start
    and specified extension. Exits on no file candidates found.
    :param search_dir:
    :param extension:
    :return:
    """
    print("searching for latest {} in directory: {}".format(extension, search_dir))
    re_mpp_file_name = re.compile(r"^(?P<iso_date>\d{8}).*")
    found_paths = {}
    for node in search_dir.iterdir():
        if not node.name.endswith(extension):
            continue
        if re.match(re_mpp_file_name, node.name):
            # print(node)
            found = re.findall(re_mpp_file_name, node.name)
            if found:
                found_paths[found[0]] = node
    if not found_paths:
        exit_on_error("no file paths found in {} matching search criteria.".format(search_dir))
    # for k,v in found_paths.items():
    #     print(k,v)
    latest_file = found_paths[max(found_paths)]
    # print("found latest file: {}".format(latest_file))
    return latest_file
