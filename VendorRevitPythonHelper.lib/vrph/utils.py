# -*- coding: utf-8 -*-
import os.path

from System.Diagnostics import Stopwatch

import datetime
import inspect
import pathlib
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


def end_script_timer(stopwatch, file_name=None):
    """
    Stops given stopwatch and shows script run time with given script name.
    :param stopwatch:
    :param file_name:
    :return:
    """
    if not file_name:
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


def check_mpxj_lib_available():
    """
    Check if mpxj lib is installed. If not error out and
    inform the user to run mpxj boostrap.
    :return:
    """
    existing_files = []
    print("INFO: check if mpxj lib download is required..")
    this_script_path = pathlib.Path(__file__)
    repo_root_path = this_script_path.parent.parent.parent
    lib_target_dir_path = repo_root_path / "mpxj_dot_net.lib" / "src.net" / "lib" / "net45"
    for node in lib_target_dir_path.iterdir():
        if node.is_file():
            existing_files.append(node.name)
    required_count = len(REQUIRED_DLLS["mpxj"])
    found_count = 0
    for path in REQUIRED_DLLS["mpxj"]:
        file_name = path.split("/")[-1]
        if file_name in existing_files:
            found_count += 1
    if found_count == required_count:
        return True
    else:
        exit_on_error("mpxj lib is missing - please install it, using 'pyRevit / info / Bootstrap_mpxj'")


REQUIRED_DLLS = {
    "mpxj": [
        "mpxj/src.net/lib/net45/commons-collections4-4.4.dll",
        "mpxj/src.net/lib/net45/commons-io-2.11.0.dll",
        "mpxj/src.net/lib/net45/commons-lang3-3.10.dll",
        "mpxj/src.net/lib/net45/commons-logging-1.2.dll",
        "mpxj/src.net/lib/net45/commons-math3-3.6.1.dll",
        "mpxj/src.net/lib/net45/IKVM.AWT.WinForms.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.Beans.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.Charsets.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.Cldrdata.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.Corba.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.Core.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.Jdbc.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.Localedata.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.Management.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.Media.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.Misc.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.Naming.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.Nashorn.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.Remoting.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.Security.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.SwingAWT.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.Text.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.Tools.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.Util.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.XML.API.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.XML.Bind.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.XML.Crypto.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.XML.Parse.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.XML.Transform.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.XML.WebServices.dll",
        "mpxj/src.net/lib/net45/IKVM.OpenJDK.XML.XPath.dll",
        "mpxj/src.net/lib/net45/IKVM.Reflection.dll",
        "mpxj/src.net/lib/net45/IKVM.Runtime.dll",
        "mpxj/src.net/lib/net45/IKVM.Runtime.JNI.dll",
        "mpxj/src.net/lib/net45/ikvm-native-win32-x64.dll",
        "mpxj/src.net/lib/net45/ikvm-native-win32-x86.dll",
        "mpxj/src.net/lib/net45/jackcess-4.0.1.dll",
        "mpxj/src.net/lib/net45/jsoup-1.15.3.dll",
        "mpxj/src.net/lib/net45/junit.dll",
        "mpxj/src.net/lib/net45/log4j-api-2.17.2.dll",
        "mpxj/src.net/lib/net45/mpxj.dll",
        "mpxj/src.net/lib/net45/mpxj-for-csharp.dll",
        "mpxj/src.net/lib/net45/mpxj-for-vb.dll",
        "mpxj/src.net/lib/net45/mpxj-test.dll",
        "mpxj/src.net/lib/net45/MpxjUtilities.dll",
        "mpxj/src.net/lib/net45/poi-5.2.2.dll",
        "mpxj/src.net/lib/net45/rtfparserkit-1.16.0.dll",
        "mpxj/src.net/lib/net45/sqlite-jdbc-3.42.0.0.dll",
    ]
}
