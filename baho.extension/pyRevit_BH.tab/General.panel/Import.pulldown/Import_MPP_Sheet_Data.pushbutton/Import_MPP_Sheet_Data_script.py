# -*- coding=utf-8 -*-
"""
Reads specified mpp (1), matches sheet information in mpp with
rvt sheet elements. rvt sheet number must match mpp 'Plannummer'.
accordingly the sheet parameters are filled:
sheet_name,
"GLS-PHA_Construction-debut",
"GLS-PHA_Construction-fin",
Note: Only for project Gare de Lausanne
(1)
* either specified mpp directory set in rvt project information
parameter: "pyrevit_config_mpp_dir"
example config: "d:\tmp\plan_4.0"
* or this button run with shift-click, which provides an
 open file dialog.
"""
import pathlib2
import sys

from Autodesk.Revit.DB import BuiltInCategory as Bic
from Autodesk.Revit.DB import FilteredElementCollector as Fec

from pyrevit import forms
from pyrevit.revit import doc, uidoc
from pyrevit.revit.db import transaction
from vrph import utils
utils.check_mpxj_lib_available()
from vrph import mpp, param


def ensure_correct_selection():
    sheet_category_id = -2003100
    if doc.ActiveView.ViewType.ToString() == "ProjectBrowser":
        selection = [doc.GetElement(elem_id) for elem_id in uidoc.Selection.GetElementIds()]
        target_selection = [elem for elem in selection if elem.Category.Id.IntegerValue == sheet_category_id]
        if len(target_selection) == 0:
            utils.exit_on_error("selection needs to contain at least one sheet element")
        print("using {} sheets from project browser selection".format(len(target_selection)))
    else:
        message = "No sheet selection was made in project browser. Do you want to write sheet data for all sheets?"
        confirmation = forms.alert(message, cancel=True)
        if confirmation:
            all_sheets = Fec(doc).OfCategory(Bic.OST_Sheets).WhereElementIsNotElementType().ToElements()
            target_selection = all_sheets
        else:
            print("script run aborted by user.")
            sys.exit()
        print("using {} sheets from project browser selection".format(len(target_selection)))

    if len(target_selection) == 0:
        utils.exit_on_error("selection needs to contain at least one sheet element")
    return target_selection


def parse_project_info_param_config(param_name):
    # example config: "d:\tmp\plan_4.0"
    file_menu = False
    config_txt = ""
    config_param = doc.ProjectInformation.LookupParameter(param_name)
    if not config_param:
        file_menu = True
    else:
        config_txt = config_param.AsString()
    if not config_txt:
        file_menu = True
    if __shiftclick__:  # noqa: F821
        file_menu = True
    if file_menu:
        config_txt = forms.pick_file()
    if config_txt:
        mpp_node = pathlib2.Path(config_txt)
        if not mpp_node.exists():
            utils.exit_on_error("mpp file/dir not found / accessible: '{}'!".format(mpp_node))
        if mpp_node.is_file():
            return None, mpp_node
        if mpp_node.is_dir():
            mpp_dir = mpp_node
            return mpp_dir, None
    utils.exit_on_error("mpp directory not specified!")


__fullframeengine__ = True
construction_start_param_name = "GLS-PHA_Construction-début"
construction_end_param_name   = "GLS-PHA_Construction-fin"

SheetInfo = mpp.SheetInfo

# ::_Required_SP_:: T:Text; TI:Instance; G:Data; C:ProjectInformation; SPG:GENERAL
config_param_name = "pyrevit_config_mpp_dir"

mpp_dir, mpp_path = parse_project_info_param_config(config_param_name)

if not mpp_path:
    mpp_path = utils.get_latest_file_in_dir_by_iso_date_and_extension(mpp_dir, ".mpp")

print("using mpp: {}".format(mpp_path))

# mpp_path = pathlib2.Path(r"d:\tmp\plan_4.0\20201026-P1.mpp")

tasks = [mpp.convert_mpxj_task_to_sheet_info(task) for task in mpp.get_tasks_from_mpp(str(mpp_path))]

# tasks = mpp.get_mpp_overview(mpp_path)
sheet_info_by_sheet_number = {task.sheet_number:task for task in tasks if task.sheet_number}

sheets_to_process = ensure_correct_selection()

stopwatch = utils.start_script_timer()

written_dates = 0
written_names = 0

with transaction.Transaction("Import_MPP_Sheet_Data", doc=doc):
    print(45 * "=")
    print("processing {} sheets: ".format(len(sheets_to_process)))
    for sheet in sheets_to_process:
        rvt_sheet_number = sheet.SheetNumber
        if rvt_sheet_number not in sheet_info_by_sheet_number:
            continue
        sheet_info = sheet_info_by_sheet_number[rvt_sheet_number]
        # print("match found: ", rvt_sheet_number, sheet.Id.IntegerValue, sheet_info_by_sheet_number[rvt_sheet_number])

        construction_start_date = getattr(sheet_info, "start_date", None) or 0
        construction_end_date   = getattr(sheet_info, "end_date",   None) or 1
        param.set_val(sheet, construction_start_param_name, construction_start_date)
        param.set_val(sheet, construction_end_param_name,   construction_end_date)
        written_dates += 1

        sheet_name = sheet_info.sheet_name
        if len(sheet_name) < 2:
            print("WARNING: matching sheet {} is skipped for name change due to short name: '{}'.".format(
                rvt_sheet_number,
                sheet_name
            ))
            continue
        else:
            sheet.Name = sheet_name
            written_names += 1


print(45 * "=")
print("written {} sheet dates.".format(written_dates))
print("written {} sheet names.".format(written_names))

utils.end_script_timer(stopwatch, file_name=__file__)
