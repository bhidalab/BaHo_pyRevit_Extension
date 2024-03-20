# -*- coding=utf-8 -*-
"""
Reads specified mpp (1), matches task designation in mpp with
rvt element parameter "GLS-PHA_Designation" value and fills
accordingly the element construction and demolition date
parameters:
"GLS-PHA_Construction-debut"
"GLS-PHA_Construction-fin"
"GLS-PHA_Demolition-debut"
"GLS-PHA_Demolition-fin"
Note: Only for project Gare de Lausanne
(1)
* either specified mpp directory set in rvt project information
parameter: "pyrevit_config_mpp_dir"
example config: "d:\tmp\plan_4.0"
* or this button run with shift-click, which provides an
 open file dialog.
"""
import collections
import pathlib2

from Autodesk.Revit.DB import BuiltInCategory, ElementId
from Autodesk.Revit.DB import FilteredElementCollector as Fec

from pyrevit import forms
from rpw import db, doc, ui
from vrph import utils
utils.check_mpxj_lib_available()
from vrph import mpp, param


def get_built_in_categories_by_id():
    bic_categories_by_id = {}
    for attr_name in dir(BuiltInCategory):
        if attr_name.startswith("OST_"):
            built_in_category = getattr(BuiltInCategory, attr_name)
            # print(built_in_category)
            bic_categories_by_id[ElementId(built_in_category).IntegerValue] = built_in_category
    return bic_categories_by_id


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
        config_txt = ui.forms.select_file()
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

print("using mpp: {}".format(mpp_path))

Task = mpp.Task

field_name_by_id = mpp.TASK_FIELD_NAME_BY_ID

# task_list = mpp.get_mpp_overview(mpp_path)

tasks = mpp.get_tasks_from_mpp(mpp_path)
task_list = []
tasks_by_task_type_by_designation = {
    "construction": {},
    "demolition"  : {},
}
spelling_variations = {
    "construction": ("construction"),
    "demolition"  : ("demolition", "dèmolition", "démolition"),
}
tasks_by_designation = collections.defaultdict(list)
for task in tasks:
    # print(35 * "-")
    # print(task)
    project_task = mpp.convert_mpxj_task_to_task(task)
    # print(project_task)
    task_list.append(project_task)
    tasks_by_designation[project_task.designation].append(project_task)
    if   project_task.task_type.lower() in spelling_variations["construction"]:
        tasks_by_task_type_by_designation["construction"][project_task.designation] = project_task
    elif project_task.task_type.lower() in spelling_variations["demolition"]:
        tasks_by_task_type_by_designation["demolition"  ][project_task.designation] = project_task
    # for i in range(1,13):
    #    text = task.getText(i)
    #    if text:
    #        print(i, field_name_by_id.get(i) or "", text)

all_chosen = "<all_of_the_below_designation>"
designation_choices = [key for key in sorted(tasks_by_designation.keys()) if key]
designation_count = len(designation_choices)
designation_choices.insert(0, all_chosen)

# print(designation_choices, type(designation_choices))
# user_designation_choice = ui.forms.SelectFromList(
#     title="Please choose 'designation' for element data sync:",
#     options=designation_choices,
#     sort=False,
#     exit_on_close=True,
# )
user_designation_choice = forms.SelectFromList.show(
    designation_choices,
    button_name="Please choose 'designation' for element data sync:",
)
if not user_designation_choice:
    utils.exit_on_error("no 'designation' was chosen.")
print("user_designation_choice: {}".format(user_designation_choice))
if user_designation_choice == all_chosen:
    user_designation_choice = None
    print("all following {} 'designation':".format(designation_count))
    for designation in designation_choices[1:]:
        print(designation)

stopwatch = utils.start_script_timer()

designation_param_name = "GLS-PHA_Désignation"

construction_start_param_name = "GLS-PHA_Construction-début"
construction_end_param_name   = "GLS-PHA_Construction-fin"
demolition_start_param_name   = "GLS-PHA_Démolition-début"
demolition_end_param_name     = "GLS-PHA_Démolition-fin"

category_name_by_ids = {
    -2008013: "Air Terminals",
    -2009630: "Analytical Beams",
    -2009633: "Analytical Braces",
    -2009636: "Analytical Columns",
    -2009639: "Analytical Floors",
    -2009643: "Analytical Foundation Slabs",
    -2009641: "Analytical Isolated Foundations",
    -2009657: "Analytical Links",
    -2009645: "Analytical Nodes",
    -2000983: "Analytical Pipe Connections",
    -2008185: "Analytical Spaces",
    -2008186: "Analytical Surfaces",
    -2009642: "Analytical Wall Foundations",
    -2009640: "Analytical Walls",
    -2003200: "Areas",
    -2000267: "Assemblies",
    -2008126: "Cable Tray Fittings",
    -2008150: "Cable Tray Runs",
    -2008130: "Cable Trays",
    -2001000: "Casework",
    -2000038: "Ceilings",
    -2000100: "Columns",
    -2008081: "Communication Devices",
    -2008128: "Conduit Fittings",
    -2008149: "Conduit Runs",
    -2008132: "Conduits",
    -2000170: "Curtain Panels",
    -2000340: "Curtain Systems",
    -2000171: "Curtain Wall Mullions",
    -2008083: "Data Devices",
    -2002000: "Detail Items",
    -2000023: "Doors",
    -2008016: "Duct Accessories",
    -2008010: "Duct Fittings",
    -2008123: "Duct Insulations",
    -2008124: "Duct Linings",
    -2008160: "Duct Placeholders",
    -2008015: "Duct Systems",
    -2008000: "Ducts",
    -2008037: "Electrical Circuits",
    -2001040: "Electrical Equipment",
    -2001060: "Electrical Fixtures",
    -2001370: "Entourage",
    -2008085: "Fire Alarm Devices",
    -2008020: "Flex Ducts",
    -2008050: "Flex Pipes",
    -2000032: "Floors",
    -2000080: "Furniture",
    -2001100: "Furniture Systems",
    -2000151: "Generic Models",
    -2000220: "Grids",
    -2008107: "HVAC Zones",
    # -2000240: "Levels",
    -2008087: "Lighting Devices",
    -2001120: "Lighting Fixtures",
    -2008212: "MEP Fabrication Containment",
    -2008193: "MEP Fabrication Ductwork",
    -2008203: "MEP Fabrication Hangers",
    -2008208: "MEP Fabrication Pipework",
    -2003400: "Mass",
    # -2000700: "Materials",
    -2001140: "Mechanical Equipment",
    -2000985: "Mechanical Equipment Sets",
    -2000095: "Model Groups",
    # -2008077: "Nurse Call Devices",
    -2001180: "Parking",
    # -2000269: "Parts",
    -2008055: "Pipe Accessories",
    -2008049: "Pipe Fittings",
    -2008122: "Pipe Insulations",
    -2008161: "Pipe Placeholders",
    -2008044: "Pipes",
    -2008043: "Piping Systems",
    -2001360: "Planting",
    -2001160: "Plumbing Fixtures",
    # -2003101: "Project Information",
    # -2001352: "RVT Links",
    -2000126: "Railings",
    -2000180: "Ramps",
    -2009013: "Rebar Shape",
    -2001220: "Roads",
    -2000035: "Roofs",
    -2000160: "Rooms",
    # -2000573: "Schedules",
    -2008079: "Security Devices",
    -2000996: "Shaft Openings",
    # -2003100: "Sheets",
    -2001260: "Site",
    -2003600: "Spaces",
    -2001350: "Specialty Equipment",
    -2008099: "Sprinklers",
    -2000120: "Stairs",
    -2009003: "Structural Area Reinforcement",
    -2001327: "Structural Beam Systems",
    -2001330: "Structural Columns",
    -2009030: "Structural Connections",
    -2009017: "Structural Fabric Areas",
    -2009016: "Structural Fabric Reinforcement",
    -2001300: "Structural Foundations",
    -2001320: "Structural Framing",
    -2009009: "Structural Path Reinforcement",
    -2009000: "Structural Rebar",
    -2009060: "Structural Rebar Couplers",
    -2001354: "Structural Stiffeners",
    -2001336: "Structural Trusses",
    -2008101: "Switch System",
    -2008075: "Telephone Devices",
    -2001340: "Topography",
    # -2000279: "Views",
    -2000011: "Walls",
    -2000014: "Windows",
    -2008039: "Wires",
}

bic_categories_by_id = get_built_in_categories_by_id()

params_written_total_count = 0

with db.Transaction("set_mpp_element_params"):
    for cat_id, cat_name in category_name_by_ids.items():
        built_in_category = bic_categories_by_id[cat_id]
        category_elements = Fec(doc).OfCategory(built_in_category).WhereElementIsNotElementType().ToElements()
        element_count = len(category_elements)
        category_params_written_count = 0
        if element_count == 0:
            continue
        print(45 * "-")
        print("\ncategory: {} - element_count: {}".format(cat_name, element_count))

        for element in category_elements:
            # print(35 * "-")
            # print(elem.Id)

            element_designation_param = element.LookupParameter(designation_param_name)
            if not element_designation_param:
                continue
            element_designation = element_designation_param.AsString()
            # print(elem_designation)
            if not element_designation:
                continue
            if user_designation_choice:
                if not element_designation == user_designation_choice:
                    # print("skipped: '{}' is not user chosen designation: {}".format(
                    #     elem_designation,
                    #     user_designation_choice,
                    # ))
                    continue

            construction_task = tasks_by_task_type_by_designation["construction"].get(element_designation)
            demolition_task   = tasks_by_task_type_by_designation["demolition"  ].get(element_designation)

            if construction_task or demolition_task:
                construction_start_date = getattr(construction_task, "start_date", None) or 0
                construction_end_date   = getattr(construction_task, "end_date"  , None) or 1
                demolition_start_date   = getattr(demolition_task  , "start_date", None) or 999998
                demolition_end_date     = getattr(demolition_task  , "end_date"  , None) or 999999

                param.set_val(element, construction_start_param_name, construction_start_date)
                param.set_val(element, construction_end_param_name  , construction_end_date)
                param.set_val(element, demolition_start_param_name  , demolition_start_date)
                param.set_val(element, demolition_end_param_name, demolition_end_date)

                category_params_written_count += 1

        print("param values written for category: {}".format(category_params_written_count))
        params_written_total_count += category_params_written_count


print(45 * "=")
print("params_written_total_count: {}".format(params_written_total_count))

utils.end_script_timer(stopwatch)
