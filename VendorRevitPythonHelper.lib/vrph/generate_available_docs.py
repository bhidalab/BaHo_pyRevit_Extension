# -*- coding: utf-8 -*-
"""
Creates pyRevit scripts listing from multiple repos in AVAILABLE.md
Collects all required shared parameter data from scripts in json
"""
import collections
import datetime
import re
import json
import sys
sys.path.append(r"C:\ProgramData\pyrevit_4.8.14\site-packages")
import pathlib
from pprint import pprint

from System.Diagnostics import Stopwatch


ScriptInfo = collections.namedtuple(
    typename="ScriptInfo",
    field_names=[
        "panel_name",
        "pulldown_name",
        "script_name",
        "doc_string",
        "path",
        "sp_info",
    ],
)


def get_top_doc_string(script_lines):
    doc_count = 0
    doc_string = ""
    for line in script_lines:
        if line.startswith('"""'):
            doc_count += 1
            continue
        if not doc_count == 1:
            continue
        if doc_count == 2:
            break
        doc_string += line
        # print(line)
    return doc_string


def get_param_info(script_lines, sp_data):
    param_lines = []
    param_marker = "::_Required_SP_::"
    param_marker_line = ""
    for line in script_lines:
        if param_marker_line:
            param_name = {" Name": line.split('"')[-2]}
            print(param_name)
            found = [m.groupdict() for m in re_param_info.finditer(param_marker_line)]
            group_dict = found[0]
            group_dict.update(param_name)
            sp_data.append(group_dict)
            param_doc = " <br>\n".join(["`{}: {}`".format(k, group_dict[k]) for k in sorted(group_dict)])
            param_lines.append(param_doc + " <br>\n\n")
            param_marker_line = ""
        if param_marker in line:
            # print("found!!", line)
            param_marker_line = line
    return param_lines, sp_data


def write_markdown_script_documentation(script_infos_map, markdown):
    markdown.write(header)
    for panel_name in sorted(script_infos_map):
        # print(35 * "-")
        # print(panel_name)
        markdown.write("\n## {}\n\n".format(panel_name))
        for pulldown_name in sorted(script_infos_map[panel_name]):
            # print(25*"-")
            # print(pulldown_name)
            markdown.write("\n### {}\n\n".format(pulldown_name))
            for script_name in sorted(script_infos_map[panel_name][pulldown_name]):
                script_info = script_infos_map[panel_name][pulldown_name][script_name]
                markdown.write("\n#### {}\n\n".format(script_info.script_name))
                markdown.write(script_info.doc_string + "\n")
                if script_info.sp_info:
                    markdown.write("\n###### required parameters:\n\n")
                for param_string in script_info.sp_info:
                    markdown.write(param_string)


stopwatch = Stopwatch()
stopwatch.Start()

D_TEMP = pathlib.Path("d:/tmp")

THIS_FILE = pathlib.Path(__file__)
PYREVIT_REPO_ROOT = pathlib.Path(__file__).parent.parent.parent

baho_ext_bh_tab = PYREVIT_REPO_ROOT / "baho.extension" / "pyRevit_BH.tab"

docs_md = PYREVIT_REPO_ROOT / "AVAILABLE.md"

today = datetime.datetime.now().date().isoformat()

# ::_Required_SP_:: T:YesNo; TI:Instance; G:Data; C:Doors, Rooms; SPG:GENERAL
re_param_info = re.compile(
    "# ::_Required_SP_:: "
    "T:(?P<Type_of_parameter>.+); "
    "TI:(?P<Type_Instance>.+); "
    "G:(?P<Group_parameter_under>.+); "
    "C:(?P<Categories>.+); "
    "SPG:(?P<Shared_Parameter_Group>.+)"
)

sp_data = []
script_infos = {}
script_count = 0

header = """
# List of available BaHo_pyRevit_Extension scripts:
{today}
""".format(today=today)

for extension_root in [baho_ext_bh_tab]:
    for panel_node in extension_root.iterdir():
        if not panel_node.name.endswith(".panel"):
            continue
        # print(35 * "=")
        # print(panel_node)
        panel_node_path = extension_root / panel_node
        panel_name = panel_node.name.split(".")[0]
        # print(35 * "-")
        # print(panel_name)
        for pulldown_node in panel_node_path.iterdir():
            if not pulldown_node.name.endswith(".pulldown"):
                continue
            if not pulldown_node.is_dir():
                continue
            pulldown_node_path = panel_node_path / pulldown_node
            pulldown_name = pulldown_node.name.split(".")[0]
            # print(25*"-")
            # print(pulldown_name)
            for pushbutton_node in pulldown_node_path.iterdir():
                if not pushbutton_node.name.endswith(".pushbutton"):
                    continue
                sub_dir_path = pulldown_node_path / pushbutton_node
                script_name = pushbutton_node.name.split(".")[0]
                script_py_file_name = script_name + "_script.py"
                script_py_path = sub_dir_path / script_py_file_name
                if not script_py_path.exists():
                    print("no .py found!!: {} !!!!".format(script_name))
                    continue
                # print(script_name)
                with open(str(script_py_path)) as script:
                    script_lines = script.readlines()
                doc_string = get_top_doc_string(script_lines)
                # print(doc_string)
                param_lines, sp_data = get_param_info(script_lines, sp_data)
                # print(param_lines)
                # print("")
                if doc_string:
                    script_count += 1

                    if panel_name not in script_infos:
                        script_infos[panel_name] = {}
                    if pulldown_name not in script_infos[panel_name]:
                        script_infos[panel_name][pulldown_name] = {}

                    script_infos[panel_name][pulldown_name][script_name] = ScriptInfo(
                            panel_name=panel_name,
                            pulldown_name=pulldown_name,
                            script_name=script_name,
                            doc_string=doc_string,
                            path=script_py_path,
                            sp_info=param_lines
                    )

with open(str(docs_md), "w") as md:
    write_markdown_script_documentation(script_infos, md)


json_path = D_TEMP / "pyRevit_BH_required_shared_parameters.json"

sp_map = {}

for info in sp_data:
    # print(info)
    spg  = info.pop("Shared_Parameter_Group")
    name = info.pop(" Name")
    if spg not in sp_map:
        sp_map[spg] = {}
    if name not in sp_map[spg]:
        sp_map[spg][name] = {}

    for k, v in info.items():
        # print(k, v)
        if k == "Categories":
            v = [c.strip() for c in v.split(",")]
        sp_map[spg][name][k] = v

pprint(sp_map)

with open(str(json_path), "w") as js_file:
    json.dump(sp_map, js_file, indent=2)


print("found {} scripts with docstring".format(script_count))
print("written required sp info to: {}".format(json_path))

print("_" * 45)
print("{} ran in: {}".format(__file__, stopwatch.Elapsed))
