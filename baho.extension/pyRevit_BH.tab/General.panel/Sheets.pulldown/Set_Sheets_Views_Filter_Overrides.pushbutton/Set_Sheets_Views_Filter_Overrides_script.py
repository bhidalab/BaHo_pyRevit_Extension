# -*- coding=utf-8 -*-
"""
Applies filter overrides for views of the selected sheets in project browser.
( unless they are excluded from filter overrides by parameter: "GLS-PHA_Designation",
with value set to either "sansFiltres" or "exclude_view_from_script_filters").
The filters are generated according to the sheets parameters:
GLS-PHA_Construction-debut,
GLS-PHA_Construction-fin,
and the project information parameter "pyrevit_config_project_start".
The filters are combined with filter overrides from view template:
"Z_GLS_PHA_filter_overrides_template" to hide or colorize elements on views
according to their respective parameter values.
The set of filter overrides are:
Z_GLS_PHA_401020_deja_demoli_template
Z_GLS_PHA_441122_pas_encore_construit_template
Z_GLS_PHA_401020_en_construction_template
Z_GLS_PHA_441122_en_demolition_template
Z_GLS_PHA_301020_existant_definitiv_template
Z_GLS_PHA_401020_441122_deja_construit_template
in the order as set in the template view template.
At the end a clean-up for all unused script filters is run.
Note: Only for project Gare de Lausanne
"""
import collections
import re

from Autodesk.Revit.DB import ElementFilter, ElementParameterFilter
from Autodesk.Revit.DB import OverrideGraphicSettings, ViewType
from Autodesk.Revit.DB import FilterIntegerRule, LogicalAndFilter
from Autodesk.Revit.DB import FilterNumericGreater, FilterNumericGreaterOrEqual
from Autodesk.Revit.DB import FilterNumericLess, FilterNumericLessOrEqual
from Autodesk.Revit.DB import ParameterFilterElement, ParameterValueProvider, SharedParameterElement
from Autodesk.Revit.DB import BuiltInCategory as Bic
from Autodesk.Revit.DB import FilteredElementCollector as Fec
from System.Collections.Generic import List

from rph import param, utils
from rpw import db, doc, uidoc


StateInfo = collections.namedtuple(
    typename="StateInfo",
    field_names=[
        "name",
        "name_fr",
        "filter_name_template",
    ]
)


FilterOverrideInfo = collections.namedtuple(
    typename="FilterOverrideInfo",
    field_names=[
        "state_info",
        "filter",
        "filter_enabled",
        "filter_visible",
        "override",
    ]
)


def ensure_correct_view_type(view, view_type):
    if view.ViewType != view_type:
        message = "Please select sheets in {}.".format(view_type)
        utils.exit_on_error(message)


def ensure_correct_selection():
    target_selection = []
    selection = [doc.GetElement(elem_id) for elem_id in uidoc.Selection.GetElementIds()]
    keep_category_ids = (
        -2003100,  # sheets
    )
    for element in selection:
        elem_category_id = element.Category.Id.IntegerValue
        if elem_category_id not in keep_category_ids:
            continue
        target_selection.append(element)
    if len(target_selection) == 0:
        utils.exit_on_error("Selection needs to contain at least one sheet element")
    return target_selection


def remove_unused_view_filters(views, filters, re_filter_name):
    print(35 * "=")
    print("INFO: starting filter clean-up")
    filter_used_on_views = collections.defaultdict(list)
    script_filter_names = set([filter_.Name for filter_ in filters if re.match(re_filter_name, filter_.Name)])
    for view in views:
        view_name = view.Name.encode("utf-8")
        view_filter_ids = view.GetOrderedFilters()
        for filter_id in view_filter_ids:
            view_filter = doc.GetElement(filter_id)
            view_filter_name = view_filter.Name.encode("utf-8")
            # print("Filter: '{}'".format(view_filter.Name))
            filter_used_on_views[view_filter_name].append(view_name)
            if view_filter.Name in script_filter_names:
                script_filter_names.remove(view_filter.Name)

    unused_script_filter_names = script_filter_names
    clean_up_filters_count = len(unused_script_filter_names)
    print("found {} unused script filters of pattern: {}.".format(
        clean_up_filters_count,
        re_filter_name.pattern,
    ))
    for filter_ in filters:
        if not re.match(re_filter_name, filter_.Name):
            continue
        if filter_.Name not in unused_script_filter_names:
            continue
        print(filter_.Name)
        _ = doc.Delete(filter_.Id)

    print("cleaned up {} unused script filters of pattern: {}.".format(
        clean_up_filters_count,
        re_filter_name.pattern,
    ))


def get_filter_overrides_template_view(views):
    search_name = "Z_GLS_PHA_filter_overrides_template"
    for view in views:
        if view.IsTemplate and view.Name == search_name:
            return view
    utils.exit_on_error("No overrides_template_view found with name: {}".format(search_name))


def get_project_start_date_truncated():
    project_start = 0
    re_date_iso8601 = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    re_date_iso8601_short = re.compile(r"^\d{8}$")
    re_date_iso8601_short_truncated = re.compile(r"^\d{6}$")
    project_start_text = param.get_val(doc.ProjectInformation, project_start_param_name)
    if not project_start_text:
        utils.exit_on_error("project_start not found in project info parameter: {}".format(
            project_start_param_name
        ))
    if   re.match(re_date_iso8601, project_start_text):
        project_start = int(project_start_text.replace("-", "")[2:])
    elif re.match(re_date_iso8601_short, project_start_text):
        project_start = int(project_start_text[2:])
    elif re.match(re_date_iso8601_short_truncated, project_start_text):
        project_start = int(project_start_text)
    if project_start:
        print("INFO: found project start date: {}".format(project_start))
        return project_start
    utils.exit_on_error("unable to parse date format: {}".format(project_start_text))


def get_shared_param_id_by_name(param_name):
    shared_param_elements = Fec(doc).OfClass(SharedParameterElement).ToElements()
    for shared_param_element in shared_param_elements:
        if shared_param_element.Name == param_name:
            return shared_param_element.Id
    utils.exit_on_error("shared param {} not found".format(param_name))


def get_or_create_filter_override(script_filters_by_name, sheet_dates, param_value_providers,
                                  filter_info_with_state_name, template_filter_category_ids_by_name):
    state_info = filter_info_with_state_name.state_info
    filter_info = {
        "state_info"   : state_info,
        "state_name_fr": state_info.name_fr,
    }
    filter_info.update(sheet_dates)
    # print("filter_info: ", filter_info)
    filter_name = state_info.filter_name_template.format(**filter_info)
    # print("filter_name: ", filter_name)
    filter_info["filter_name"] = filter_name
    filter_found = script_filters_by_name.get(filter_name)
    if not filter_found:
        print("INFO: could not find filter - it will be created: {}".format(filter_name))
        filter_info["category_ids"] = template_filter_category_ids_by_name[state_info.name]
        filter_found = create_filter(filter_info, param_value_providers)
    # else:
    #     print("found already existing filter: {}".format(filter_found))
    return FilterOverrideInfo(
        state_info=state_info,
        filter=filter_found,
        filter_enabled=filter_info_with_state_name.filter_enabled,
        filter_visible=filter_info_with_state_name.filter_visible,
        override=filter_info_with_state_name.override,
    )


def create_filter(filter_info, param_value_providers):
    created_filter = None
    state_name = filter_info["state_info"].name
    create_filter_function_by_state = {
        "existing"           : create_filter_existing,             # existant_definitiv
        "already_demolished" : create_filter_already_demolished,   # deja_demoli
        "already_constructed": create_filter_already_constructed,  # deja_construit
        "under_construction" : create_filter_under_construction,   # en_construction
        "being_demolished"   : create_filter_being_demolished,     # en_demolition
        "not_yet_constructed": create_filter_not_yet_constructed,  # pas_encore_construit
    }
    if state_name in create_filter_function_by_state:
        create_filter_function = create_filter_function_by_state[state_name]
        created_filter = create_filter_function(
            filter_info=filter_info,
            param_value_providers=param_value_providers,
        )
    else:
        print("WARNING: filter not created! creation of {} not implemented!".format(state_name))
        print(filter_info)
    if created_filter:
        # print("created: ", state_name, created_filter)
        return created_filter


def create_filter_existing(filter_info, param_value_providers):
    # existant_definitiv
    param_value_provider = param_value_providers["construction_end_param_name"]
    filter_rule = FilterIntegerRule(param_value_provider, FilterNumericLess(), filter_info["project_start"])
    start_filter = ElementParameterFilter(filter_rule)
    existing_filter = ParameterFilterElement.Create(doc, filter_info["filter_name"], filter_info["category_ids"])
    existing_filter.SetElementFilter(start_filter)
    return existing_filter


def create_filter_already_demolished(filter_info, param_value_providers):
    # deja_demoli
    param_value_provider = param_value_providers["demolition_end_param_name"]
    filter_rule = FilterIntegerRule(param_value_provider, FilterNumericLessOrEqual(), filter_info["sheet_start"])
    start_filter = ElementParameterFilter(filter_rule)
    already_demolished_filter = ParameterFilterElement.Create(doc, filter_info["filter_name"], filter_info["category_ids"])
    already_demolished_filter.SetElementFilter(start_filter)
    return already_demolished_filter


def create_filter_already_constructed(filter_info, param_value_providers):
    # deja_construit
    param_value_provider_construction_end = param_value_providers["construction_end_param_name"]
    param_value_provider_demolition_start = param_value_providers["demolition_start_param_name"]

    filters = List[ElementFilter]()
    filters.Add(ElementParameterFilter(
        FilterIntegerRule(
            param_value_provider_construction_end,
            FilterNumericLessOrEqual(),
            filter_info["sheet_start"],
    )))
    filters.Add(ElementParameterFilter(
        FilterIntegerRule(
            param_value_provider_demolition_start,
            FilterNumericGreaterOrEqual(),
            filter_info["sheet_end"],
    )))
    combined_filters = LogicalAndFilter(filters)
    already_constructed_filter = ParameterFilterElement.Create(doc, filter_info["filter_name"], filter_info["category_ids"])
    already_constructed_filter.SetElementFilter(combined_filters)
    return already_constructed_filter


def create_filter_under_construction(filter_info, param_value_providers):
    # en_construction
    param_value_provider = param_value_providers["construction_end_param_name"]
    filter_rule = FilterIntegerRule(param_value_provider, FilterNumericGreater(), filter_info["sheet_start"])
    start_filter = ElementParameterFilter(filter_rule)
    under_construction_filter = ParameterFilterElement.Create(doc, filter_info["filter_name"], filter_info["category_ids"])
    under_construction_filter.SetElementFilter(start_filter)
    return under_construction_filter


def create_filter_being_demolished(filter_info, param_value_providers):
    # en_demolition
    param_value_provider = param_value_providers["demolition_start_param_name"]
    filter_rule = FilterIntegerRule(param_value_provider, FilterNumericLess(), filter_info["sheet_end"])
    start_filter = ElementParameterFilter(filter_rule)
    being_demolished_filter = ParameterFilterElement.Create(doc, filter_info["filter_name"], filter_info["category_ids"])
    being_demolished_filter.SetElementFilter(start_filter)
    return being_demolished_filter


def create_filter_not_yet_constructed(filter_info, param_value_providers):
    # pas_encore_construit
    param_value_provider = param_value_providers["construction_start_param_name"]
    filter_rule = FilterIntegerRule(param_value_provider, FilterNumericGreater(), filter_info["sheet_end"])
    start_filter = ElementParameterFilter(filter_rule)
    not_yet_constructed_filter = ParameterFilterElement.Create(doc, filter_info["filter_name"], filter_info["category_ids"])
    not_yet_constructed_filter.SetElementFilter(start_filter)
    return not_yet_constructed_filter


def remove_existing_view_script_filters(view, regex):
    for filter_id in view.GetOrderedFilters():
        filter_name = doc.GetElement(filter_id).Name
        if not re.match(regex, filter_name):
            # print("skipping non-script-filter: {}".format(filter_name))
            continue
        # print("removing existing script filter: ", filter_name)
        view.RemoveFilter(filter_id)


def set_view_filter_and_overrides(view, override_info):
    filter_id = override_info.filter.Id
    view.AddFilter(filter_id)
    view.SetFilterOverrides( filter_id, override_info.override)
    view.SetFilterVisibility(filter_id, override_info.filter_visible)
    view.SetIsFilterEnabled( filter_id, override_info.filter_enabled)


__fullframeengine__ = True

stopwatch = utils.start_script_timer()
re_template_filter_name = re.compile(r"^Z_GLS_PHA_.*\d{6}_(?P<construction_state>.*)_template$")
re_script_filter_name   = re.compile(r"^Z_GLS_PHA_\d{6}_.*")

# ::_Required_SP_:: T:Text; TI:Instance; G:Data; C:ProjectInformation; SPG:GENERAL
project_start_param_name = "pyrevit_config_project_start"

project_start = get_project_start_date_truncated()

designation_param_name = "GLS-PHA_Désignation"

construction_start_param_name = "GLS-PHA_Construction-début"
construction_end_param_name   = "GLS-PHA_Construction-fin"
demolition_start_param_name   = "GLS-PHA_Démolition-début"
demolition_end_param_name     = "GLS-PHA_Démolition-fin"

exclude_view_from_script_filters = [
    "sansFiltres",
    "exclude_view_from_script_filters",
]

state_infos = [
    #         name,                  name_fr,                filter_name_template
    # past
    StateInfo("existing",            "existant_definitiv",   "Z_GLS_PHA_{project_start}_{state_name_fr}"),
    StateInfo("already_demolished",  "deja_demoli",          "Z_GLS_PHA_{sheet_start}_{state_name_fr}"),
    StateInfo("already_constructed", "deja_construit",       "Z_GLS_PHA_{sheet_start}_{sheet_end}_{state_name_fr}"),
    # present
    StateInfo("under_construction",  "en_construction",      "Z_GLS_PHA_{sheet_start}_{state_name_fr}"),
    StateInfo("being_demolished",    "en_demolition",        "Z_GLS_PHA_{sheet_end}_{state_name_fr}"),
    # future
    StateInfo("not_yet_constructed", "pas_encore_construit", "Z_GLS_PHA_{sheet_start}_{state_name_fr}"),
]
state_infos_by_name = {info.name:info         for info in state_infos}
state_names_fr_en   = {info.name_fr:info.name for info in state_infos}

param_value_provider_by_param_name = {
    "construction_start_param_name": ParameterValueProvider(get_shared_param_id_by_name(construction_start_param_name)),
    "construction_end_param_name"  : ParameterValueProvider(get_shared_param_id_by_name(construction_end_param_name)),
    "demolition_start_param_name"  : ParameterValueProvider(get_shared_param_id_by_name(demolition_start_param_name)),
    "demolition_end_param_name"    : ParameterValueProvider(get_shared_param_id_by_name(demolition_end_param_name)),
}

ensure_correct_view_type(doc.ActiveView, ViewType.ProjectBrowser)
selected_sheets = ensure_correct_selection()

all_views   = Fec(doc).OfCategory(Bic.OST_Views).WhereElementIsNotElementType().ToElements()
all_filters = Fec(doc).OfClass(ParameterFilterElement).WhereElementIsNotElementType().ToElements()

script_filters_by_name = {
    filter_.Name: filter_ for filter_ in all_filters if re.match(re_script_filter_name, filter_.Name)
}

overrides_template_view = get_filter_overrides_template_view(all_views)

template_filter_category_ids_by_name = {}
template_filter_state_infos = []
template_view_filter_ids = [filter_id for filter_id in overrides_template_view.GetOrderedFilters()]

filter_info_by_state_name = {}

print(35 * "=")
print("scanning template view filter overrides:")
for filter_id in template_view_filter_ids:
    filter_name      = doc.GetElement(filter_id).Name
    filter_visible   = overrides_template_view.GetFilterVisibility(filter_id)
    filter_enabled   = overrides_template_view.GetIsFilterEnabled(filter_id)
    filter_overrides = overrides_template_view.GetFilterOverrides(filter_id)
    if re.match(re_template_filter_name, filter_name):
        found_state_fr = next(iter(re.findall(re_template_filter_name, filter_name)))
        found_state = state_names_fr_en[found_state_fr]
        state_info = state_infos_by_name[found_state]
        print("{} : {}".format(found_state, filter_name))
        template_filter_category_ids_by_name[found_state] = doc.GetElement(filter_id).GetCategories()
        template_filter_state_infos.append(state_infos_by_name[found_state])
        filter_info_by_state_name[found_state] = FilterOverrideInfo(
            state_info=state_info,
            filter=doc.GetElement(filter_id),
            filter_enabled=filter_enabled,
            filter_visible=filter_visible,
            override=OverrideGraphicSettings(filter_overrides),
        )

if len(template_filter_state_infos) != len(state_infos):
    print("ERROR: found {} out of {} required view template filter overrides:".format(
        len(template_filter_state_infos), len(state_infos)
    ))
    print("INFO: required view template filter overrides:")
    for info in state_infos:
        print("{}_template".format(info.name))
    print("ERROR: missing view template filter overrides:")
    found_names = [info.name for info in template_filter_state_infos]
    for info in state_infos:
        if info.name not in found_names:
            print("{}_template".format(info.name))
    utils.exit_on_error("not all required view template filter overrides found")


with db.Transaction("Set_Sheets_Views_Filter_Overrides"):
    print(35 * "=")
    sheet_rule_dates = {
        "project_start": project_start,
        "sheet_start"  : None,
        "sheet_end"    : None,
    }

    existing_filter_override_info = get_or_create_filter_override(
        script_filters_by_name=script_filters_by_name,
        sheet_dates=sheet_rule_dates,
        param_value_providers=param_value_provider_by_param_name,
        filter_info_with_state_name=filter_info_by_state_name["existing"],
        template_filter_category_ids_by_name=template_filter_category_ids_by_name,
    )

    view_filter_override_infos = {
        "existing"           : existing_filter_override_info,  # existant_definitiv
        "under_construction" : None,                           # en_construction
        "being_demolished"   : None,                           # en_demolition
        "already_demolished" : None,                           # deja_demoli
        "already_constructed": None,                           # deja_construit
        "not_yet_constructed": None,                           # pas_encore_construit
    }

    for sheet in selected_sheets:
        print(35 * "=")
        print("sheet: {} :: {}".format(sheet.SheetNumber, sheet.Name))
        sheet_start = param.get_val(sheet, construction_start_param_name)
        sheet_end   = param.get_val(sheet, construction_end_param_name)

        sheet_rule_dates["sheet_start"] = sheet_start
        sheet_rule_dates["sheet_end"  ] = sheet_end
        print("sheet_rule_dates: ", sheet_rule_dates)

        for state_name, override_info in view_filter_override_infos.items():
            if override_info:  # existing is already populated
                continue
            # print(state_name)
            wrong_dates = filter_info_by_state_name[state_name]
            view_filter_override_infos[state_name] = get_or_create_filter_override(
                script_filters_by_name=script_filters_by_name,
                sheet_dates=sheet_rule_dates,
                param_value_providers=param_value_provider_by_param_name,
                filter_info_with_state_name=filter_info_by_state_name[state_name],
                template_filter_category_ids_by_name=template_filter_category_ids_by_name,
            )

        for view_id in sheet.GetAllPlacedViews():
            print(25 * "-")
            view = doc.GetElement(view_id)
            print("sheet: {} :: {}".format(sheet.SheetNumber, sheet.Name))

            print("sheet: {} - view: {}".format(sheet.Name, view.Name))

            if view.ViewType == ViewType.Legend:
                print("skipped view due to view type: legend")
                continue

            if view.LookupParameter(designation_param_name):
                view_designation = param.get_val(view, designation_param_name)
                if view_designation in exclude_view_from_script_filters:
                    print("skipped view for filter overrides due to parameter set to exclusion: {}".format(view_designation))
                    continue

            remove_existing_view_script_filters(view, re_script_filter_name)

            for state_info in template_filter_state_infos:
                state_name = state_info.name
                filter_override_info = view_filter_override_infos[state_name]
                # print("will add filter override: ", state_name, filter_override_info)
                set_view_filter_and_overrides(view, filter_override_info)

with db.Transaction("Remove_Unused_Script_Filters"):
   remove_unused_view_filters(all_views, all_filters, re_script_filter_name)

utils.end_script_timer(stopwatch, file_name=__file__)
