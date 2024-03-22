
# List of available BaHo_pyRevit_Extension scripts:
2024-03-22

## General


### Import


#### Import_MPP_Element_Data

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


###### required parameters:

` Name: pyrevit_config_mpp_dir` <br>
`Categories: ProjectInformation` <br>
`Group_parameter_under: Data` <br>
`Shared_Parameter_Group: GENERAL` <br>
`Type_Instance: Instance` <br>
`Type_of_parameter: Text` <br>


#### Import_MPP_Sheet_Data

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


###### required parameters:

` Name: pyrevit_config_mpp_dir` <br>
`Categories: ProjectInformation` <br>
`Group_parameter_under: Data` <br>
`Shared_Parameter_Group: GENERAL` <br>
`Type_Instance: Instance` <br>
`Type_of_parameter: Text` <br>


### Sheets


#### Duplicate_Sheet_Into_MPP_Sheet_Series

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


###### required parameters:

` Name: pyrevit_config_mpp_dir` <br>
`Categories: ProjectInformation` <br>
`Group_parameter_under: Data` <br>
`Shared_Parameter_Group: GENERAL` <br>
`Type_Instance: Instance` <br>
`Type_of_parameter: Text` <br>


#### Set_Sheets_Views_Filter_Overrides

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


###### required parameters:

` Name: pyrevit_config_project_start` <br>
`Categories: ProjectInformation` <br>
`Group_parameter_under: Data` <br>
`Shared_Parameter_Group: GENERAL` <br>
`Type_Instance: Instance` <br>
`Type_of_parameter: Text` <br>


## info


### info


#### Bootstrap_mpxj

Runs the bootstrap process for retrieving mpxj libs needed for reading .mpp files.

