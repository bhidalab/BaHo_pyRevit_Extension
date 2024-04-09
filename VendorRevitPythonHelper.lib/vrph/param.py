# -*- coding: utf-8 -*-
import collections
import re

from Autodesk.Revit.DB import BuiltInParameter as Bip, StorageType, Parameter, ElementId
from System import Convert

from pyrevit.revit import doc


def print_param_mapping(param_dict, title="", verbose=True):
    """
    Prints a key value pairs of the parameter dict
    :param param_dict:
    :param title:
    :param verbose:
    :return:
    """
    if verbose:
        print(title)
        for key in param_dict:
            print(35 * "-")
            print(key)
            print(param_dict[key])


def encode_cp1252_to_utf8(txt):
    """
    Converts cp1252 encoded string to utf8
    :param txt:
    :return:
    """
    if txt:
        return txt.decode("cp1252").encode("utf-8")
    return ""


def get_param_binding_entries_by_category_id():
    """
    Retrieve an overview map of parameter bindings in the document by category id.
    Returns: dict
    """
    param_binding_entries_by_cat_id = collections.defaultdict(dict)
    pb_iter = doc.ParameterBindings.ForwardIterator()
    pb_iter.Reset()
    while pb_iter.MoveNext():
        entry = pb_iter.Current
        name = pb_iter.Key.Name
        cat_ids = [c.Id.IntegerValue for c in entry.Categories]
        for cat_id in cat_ids:
            param_binding_entries_by_cat_id[cat_id][name] = pb_iter.Key

    return param_binding_entries_by_cat_id


def get_param_binding_entries_by_type_inst():
    """
    Retrieve an overview map of parameter bindings in the document by type or instance binding.
    Returns: dict
    """
    param_binding_entries_type_inst = {
        "inst": [],
        "type": [],
    }
    pb_iter = doc.ParameterBindings.ForwardIterator()
    pb_iter.Reset()
    while pb_iter.MoveNext():
        entry = pb_iter.Current
        binding_type = entry.ToString().split(".")[-1]
        if binding_type == 'InstanceBinding':
            param_binding_entries_type_inst["inst"].append(pb_iter.Key)
        elif binding_type == 'TypeBinding':
            param_binding_entries_type_inst["type"].append(pb_iter.Key)

    return param_binding_entries_type_inst


def parameter_binding_exists(param_name, as_instance_binding, category_id):
    """
    Checks if a parameter binding for param_name exists as_instance_binding
    or type binding for a specified category.
    :param param_name:
    :param as_instance_binding:
    :param category_id:
    :return:
    """
    param_binding_iter = doc.ParameterBindings.ForwardIterator()
    param_binding_iter.Reset()
    while param_binding_iter.MoveNext():
        skip = True
        item = param_binding_iter.Current
        type_inst = item.GetType().Name
        if   type_inst == "InstanceBinding" and as_instance_binding is True:
            skip = False
        elif type_inst == "TypeBinding"     and as_instance_binding is False:
            skip = False
        if skip:
            continue
        binding_name = param_binding_iter.Key.Name
        if binding_name != param_name:
            continue
        for category in item.Categories:
            if category_id == category.Id.IntegerValue:
                return True
    return False


def get_info_map(element, verbose=None, name=None, regex=None):
    """
    Retrieve an overview of parameters of the provided element.
    Prints out the gathered parameter information
    :param element: Element that holds the parameters.
    :param verbose:
    :param name:
    :param regex:
    :return: Returns two dictionaries: Instance dict, Type dict.
             If no type is available second dict is None
    """
    info_map = []
    info_map.extend(collect_infos(element))
    if "GetTypeId" in dir(element):
        if element.GetTypeId() != ElementId.InvalidElementId:
            elem_type = doc.GetElement(element.GetTypeId())
            info_map.extend(collect_infos(elem_type, is_type_param=True))

    if name:
        return sorted(pi for pi in info_map if pi.name == name)

    if regex:
        re_filter = re.compile(regex)
        return sorted(pi for pi in info_map if re.match(re_filter, str(pi)))

    return sorted(info_map)


def collect_infos(param_element, is_type_param=False):
    """
    Collects parameters of the provided element.
    :param param_element:
    :param is_type_param:
    :return: dictionary, with parameters.
    """
    parameters = param_element.Parameters
    param_infos = []

    for param in parameters:
        param_value = get_val(None, None, param)

        param_info = ParamInfo(
            is_type_param,
            param.Definition.Name,
            param_value,
            param.StorageType,
            param.HasValue,
            param.IsShared,
            param.IsReadOnly,
            param,
        )
        param_infos.append(param_info)

    return param_infos


def get_val(elem, param_name, param=None, bip=False):
    """
    Retrieves parameter value of element or parameter
    or its standard empty value for its type.
    :param elem: the element holding the parameter
    :param param_name: name of the parameter
    :param param: optionally the param instead of elem
    :param bip:
    :return: value of the parameter or empty of type
    """
    if not param:
        if bip:
            param = elem.get_Parameter(bip_map[param_name])
        else:
            param = elem.LookupParameter(param_name)
    if param:
        dtype = param.StorageType
        if param.HasValue:
            return dtype_methods[dtype](param)
        return dtype_empty[dtype]
    else:
        print("param not found: {}".format(param_name))


def set_val(elem, param_name, value, param=None, bip=False):
    """
    Sets parameter value of element or parameter.
    :param elem:
    :param param_name:
    :param value:
    :param param:
    :param bip:
    :return:
    """
    if not param:
        if bip:
            param = elem.get_Parameter(bip_map[param_name])
        else:
            param = elem.LookupParameter(param_name)
    if param:
        param.Set(value)
    else:
        print("param not found: {}".format(param_name))


def get_comments(elem):
    """
    Convenience function to get comments value from element.
    :param elem:
    :return:
    """
    return get_val(elem, "comments", bip=True)


def set_comments(elem, value):
    """
    Convenience function to set comments value for element.
    :param elem:
    :param value:
    :return:
    """
    set_val(elem, "comments", value, bip=True)


def get_mark(elem):
    """
    Convenience function to get mark value from element.
    :param elem:
    :return:
    """
    return get_val(elem, "mark", bip=True)


def set_mark(elem, value):
    """
    Convenience function to set mark value for element.
    :param elem:
    :param value:
    :return:
    """
    set_val(elem, "mark", value, bip=True)


def get_description(elem):
    """
    Convenience function to get type description value from element.
    :param elem:
    :return:
    """
    return get_val(elem, "description", bip=True)


def set_description(elem, value):
    """
    Convenience function to set type description value for element.
    :param elem:
    :param value:
    :return:
    """
    set_val(elem, "description", value, bip=True)


def get_type_name(elem):
    """
    Convenience function to get type name value from element.
    :param elem:
    :return:
    """
    return get_val(elem, "type_name", bip=True)


def set_type_name(elem, value):
    """
    Convenience function to set type name value for element.
    :param elem:
    :param value:
    :return:
    """
    set_val(elem, "type_name", value, bip=True)


RVT_MAJ_VERSION = int(doc.Application.VersionNumber)
dtype_methods = {
    StorageType.String   : Parameter.AsString,
    StorageType.Integer  : Parameter.AsInteger,
    StorageType.Double   : Parameter.AsDouble,
    StorageType.ElementId: Parameter.AsElementId,
}
dtype_empty = {
    StorageType.String : "",
    StorageType.Integer: 0,
    StorageType.Double : 0.0,
    StorageType.ElementId: ElementId(-1),
}
dtype_conversions = {
    StorageType.String   : Convert.ToString,
    StorageType.Integer  : Convert.ToInt32,
    StorageType.Double   : Convert.ToDouble,
    StorageType.ElementId: ElementId,
}
bip_map = {
    "comments"                   : Bip.ALL_MODEL_INSTANCE_COMMENTS,
    "department"                 : Bip.ROOM_DEPARTMENT,
    "description"                : Bip.ALL_MODEL_DESCRIPTION,
    "family_name"                : Bip.ALL_MODEL_FAMILY_NAME,
    "level_compute_height"       : Bip.LEVEL_ROOM_COMPUTATION_HEIGHT,
    "level_name"                 : Bip.DATUM_TEXT,
    "mark"                       : Bip.ALL_MODEL_MARK,
    "overall_size"               : Bip.RBS_REFERENCE_OVERALLSIZE,
    "phase_created"              : Bip.PHASE_CREATED,
    "pipe_diameter"              : Bip.RBS_PIPE_DIAMETER_PARAM,
    "pipe_insulation_thickness"  : Bip.RBS_REFERENCE_INSULATION_THICKNESS,
    "pipe_system_class"          : Bip.RBS_SYSTEM_CLASSIFICATION_PARAM,
    "project_number"             : Bip.PROJECT_NUMBER,
    "ramps_down_label_on"        : Bip.STAIRS_INST_DOWN_LABEL_ON,
    "ramps_up_label_on"          : Bip.STAIRS_INST_UP_LABEL_ON,
    "room_area"                  : Bip.ROOM_AREA,
    "room_ceiling_finish"        : Bip.ROOM_FINISH_CEILING,
    "room_department"            : Bip.ROOM_DEPARTMENT,
    "room_floor_finish"          : Bip.ROOM_FINISH_FLOOR,
    "room_name"                  : Bip.ROOM_NAME,
    "room_number"                : Bip.ROOM_NUMBER,
    "room_phase"                 : Bip.ROOM_PHASE,
    "room_wall_finish"           : Bip.ROOM_FINISH_WALL,
    "sheet_current_revision"     : Bip.SHEET_CURRENT_REVISION,
    "sheet_issue_date"           : Bip.SHEET_ISSUE_DATE,
    "sill_height"                : Bip.INSTANCE_SILL_HEIGHT_PARAM,
    "stairs_show_down_text"      : Bip.STAIRS_SHOW_DOWN_TEXT,
    "stairs_show_up_text"        : Bip.STAIRS_SHOW_UP_TEXT,
    "type_mark"                  : Bip.WINDOW_TYPE_ID,
    "type_name"                  : Bip.ALL_MODEL_TYPE_NAME,
    "wall_height"                : Bip.WALL_USER_HEIGHT_PARAM,
    "wall_room_bounding"         : Bip.WALL_ATTR_ROOM_BOUNDING,
    "wall_thickness"             : Bip.WALL_ATTR_WIDTH_PARAM,
    "wall_width"                 : Bip.WALL_ATTR_WIDTH_PARAM,
}
if RVT_MAJ_VERSION > 2022:
    bip_map.update(
        {
            "ifc_export_element_as"     : Bip.IFC_EXPORT_ELEMENT_AS,
            "ifc_export_element_type_as": Bip.IFC_EXPORT_ELEMENT_TYPE_AS,
        }
    )

bip_map_reverse_map = {v: k for k, v in bip_map.items()}

ParamInfo = collections.namedtuple("ParamInfo", "type_param name value dtype has_value shared read_only param")
TITLE_INST_PARAMS = "INSTANCE PARAMETERS" + 50 * "_"
TITLE_TYPE_PARAMS = "TYPE PARAMETERS    " + 50 * "_"
