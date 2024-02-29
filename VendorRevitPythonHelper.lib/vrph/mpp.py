# -*- coding: utf-8 -*-
import collections
import sys

MPXJ_DOT_NET_LIB_PATH = r"C:\ProgramData\baho_pyrevit_extension\mpxj_dot_net.lib\src.net\lib\net45"
if not MPXJ_DOT_NET_LIB_PATH in sys.path:
    sys.path.append(MPXJ_DOT_NET_LIB_PATH)
# ^^ using mpxj version: 12.7.0
import clr
clr.AddReference("rtfparserkit-1.16.0")
clr.AddReference("mpxj")
from net.sf import mpxj


SheetInfo = collections.namedtuple(
    typename="SheetInfo",
    field_names=[
        "id",
        "sheet_number",
        "sheet_name",
        "start_date",
        "end_date",
        "mpp_task",
    ]
)


Task = collections.namedtuple(
    typename="Task",
    field_names=[
        "id",
        "name",
        "designation",
        "start_date",
        "end_date",
        "sheet_number",
        "task_type",
        "zone_name",
        "version_number",
        "version_date",
        "mpp_task",
    ],
)


def _get_date_truncated_iso_short(task_date):
    """
    Retrieves YYMMDD date format from mpp task date.
    :param task_date:
    :return:
    """
    if not task_date:
        return ""
    day   = str(task_date.getDayOfMonth()).zfill(2)
    month = str(task_date.getMonthValue()).zfill(2)
    year  = str(task_date.getYear())
    truncated = "{}{}{}".format(year[-2:], month, day)
    # iso_short = "{}{}{}".format(year, month, day)
    # print("{} -> {}".format(iso_short, truncated))
    return int(truncated)


def convert_mpxj_task_to_sheet_info(task):
    """
    Converts task from mpp file into a convenient namedtuple SheetInfo object.
    :param task:
    :return:
    """
    return SheetInfo(
        id=task.getID().intValue() or -1,
        sheet_number=task.getText(4) or "",
        sheet_name=task.getName(),
        start_date=_get_date_truncated_iso_short(task.getStart()),
        end_date=_get_date_truncated_iso_short(task.getFinish()),
        mpp_task=task,
    )


def convert_mpxj_task_to_task(task):
    """
    Converts task from mpp file into a convenient namedtuple Task object.
    :param task:
    :return:
    """
    return Task(
        id=task.getID().intValue() or -1,
        name=task.getName(),
        designation=task.getText(1) or "",
        start_date=_get_date_truncated_iso_short(task.getStart()),
        end_date=_get_date_truncated_iso_short(task.getFinish()),
        sheet_number=task.getText(4) or "",
        task_type=task.getText(2) or "",
        zone_name=task.getText(11) or "",
        version_number=task.getText(5) or "",
        version_date=task.getText(6) or "",
        mpp_task=task,
    )


def get_mpp_overview(mpp_path):
    """
    Iterates enumerated over all tasks in a mpp file and returns them.
    :param mpp_path:
    :return:
    """
    if not mpp_path.exists():
        print("mpp not found: ", mpp_path)
    reader = mpxj.reader.UniversalProjectReader()
    project = reader.read(str(mpp_path))
    task_list = []
    tasks = project.getTasks()
    for i, task in enumerate(tasks):
        project_task = convert_mpxj_task_to_sheet_info(task)
        task_list.append(project_task)
        print(i, project_task)
    return task_list
