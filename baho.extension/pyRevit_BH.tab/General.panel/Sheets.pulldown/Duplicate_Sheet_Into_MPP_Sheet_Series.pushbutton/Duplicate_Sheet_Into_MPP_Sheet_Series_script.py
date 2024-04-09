# -*- coding=utf-8 -*-
"""
Duplicates current active sheet with placed views
according to sheet parameter "GLS-PHA_Designation"
with found matching sheet information from mpp*.
Sheet sorting parameters are matched from active sheet:
"_DOSSIER", "_SOUS-DOSSIER", "_SORT" .
According to the mpp the sheet parameters are filled:
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

from Autodesk.Revit.DB import SheetDuplicateOption
from Autodesk.Revit.DB import BuiltInCategory as Bic
from Autodesk.Revit.DB import FilteredElementCollector as Fec

from pyrevit import forms
from pyrevit.revit import doc, uidoc
from pyrevit.revit.db import transaction
from vrph import utils
utils.check_mpxj_lib_available()
from vrph import mpp, param


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

# ::_Required_SP_:: T:Text; TI:Instance; G:Data; C:ProjectInformation; SPG:GENERAL
config_param_name = "pyrevit_config_mpp_dir"

mpp_dir, mpp_path = parse_project_info_param_config(config_param_name)

if not mpp_path:
    mpp_path = utils.get_latest_file_in_dir_by_iso_date_and_extension(mpp_dir, ".mpp")

stopwatch = utils.start_script_timer()

# mpp_path = pathlib2.Path(r"d:\tmp\plan_4.0\20201026-P1.mpp")

print("using mpp: {}".format(mpp_path))

designation_param_name        = "GLS-PHA_Désignation"
construction_start_param_name = "GLS-PHA_Construction-début"
construction_end_param_name   = "GLS-PHA_Construction-fin"

sheet_grouping_param_name     = "_DOSSIER"
sheet_sub_grouping_param_name = "_SOUS-DOSSIER"
sheet_sorting_param_name      = "_SORT"

if not doc.ActiveView.Category:
    utils.exit_on_error("active view needs to be a sheet.")

if doc.ActiveView.Category.Id.IntegerValue != -2003100:
    utils.exit_on_error("active view needs to be a sheet.")

all_sheets = Fec(doc).OfCategory(Bic.OST_Sheets).WhereElementIsNotElementType().ToElements()
all_sheet_numbers = {sheet.SheetNumber for sheet in all_sheets}

active_sheet = doc.ActiveView
active_sheet_designation = param.get_val(active_sheet, designation_param_name)
if not active_sheet_designation:
    utils.exit_on_error("active sheet has no designation set.")
print("active sheet designation {}.".format(active_sheet_designation))

active_sheet_number    = active_sheet.SheetNumber
active_sheet_name      = active_sheet.Name
active_sheet_group     = param.get_val(doc.ActiveView, sheet_grouping_param_name)
active_sheet_sub_group = param.get_val(doc.ActiveView, sheet_sub_grouping_param_name)
active_sheet_sorting   = param.get_val(doc.ActiveView, sheet_sorting_param_name)

duplicate_option = SheetDuplicateOption()
duplicate_option = duplicate_option.DuplicateSheetWithViewsAndDetailing

mpp_tasks = [mpp.convert_mpxj_task_to_task(task) for task in mpp.get_tasks_from_mpp(str(mpp_path))]

found_matching_mpp_sheets_count = 0

with transaction.Transaction("duplicate_sheet_into_mpp_sheet_series", doc=doc):
    for task in mpp_tasks:
        if not task.name:
            continue
        if not task.designation:
            continue
        if task.designation != active_sheet_designation:
            continue
        if not task.sheet_number:
            continue
        if task.sheet_number == active_sheet_number:
            continue
        if task.sheet_number in all_sheet_numbers:
            print("skipped creating of sheet number: {} - existed already!".format(task.sheet_number))
            continue
        print(task.designation, task.sheet_number, task.name)
        found_matching_mpp_sheets_count += 1
        duplicated_sheet_id = active_sheet.Duplicate(duplicate_option)
        duplicated_sheet = doc.GetElement(duplicated_sheet_id)
        duplicated_sheet.SheetNumber = task.sheet_number
        duplicated_sheet.Name = task.name
        param.set_val(duplicated_sheet, designation_param_name, task.designation)

        param.set_val(duplicated_sheet, construction_start_param_name, task.start_date)
        param.set_val(duplicated_sheet, construction_end_param_name  , task.end_date)

        param.set_val(duplicated_sheet, sheet_grouping_param_name    , active_sheet_group)
        param.set_val(duplicated_sheet, sheet_sub_grouping_param_name, active_sheet_sub_group)
        param.set_val(duplicated_sheet, sheet_sorting_param_name     , active_sheet_sorting)

print("count of created matching mpp sheets: {}".format(found_matching_mpp_sheets_count))

utils.end_script_timer(stopwatch, file_name=__file__)
