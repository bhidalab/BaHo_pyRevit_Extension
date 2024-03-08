
# List of available BaHo_pyRevit_Extension scripts:
2024-03-08

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
parameter: "config_mpp_dir"
example config: "d:\tmp\plan_4.0\"
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
parameter: "config_mpp_dir"
example config: "d:\tmp\plan_4.0\"
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
according to sheet parameter "GLS-PHA_Désignation"
with found matching sheet information from mpp:
Reads specified mpp (1), matches sheet information in mpp with
rvt sheet elements. rvt sheet number must match mpp 'Plannummer'.
accordingly the sheet parameters are filled:
sheet_name,
"GLS-PHA_Construction-debut",
"GLS-PHA_Construction-fin",
Note: Only for project Gare de Lausanne
(1)
* either specified mpp directory set in rvt project information
parameter: "config_mpp_dir"
example config: "d:\tmp\plan_4.0\"
* or this button run with shift-click, which provides an
 open file dialog.


###### required parameters:

` Name: config_mpp_dir` <br>
`Categories: ProjectInformation` <br>
`Group_parameter_under: Data` <br>
`Shared_Parameter_Group: GENERAL` <br>
`Type_Instance: Instance` <br>
`Type_of_parameter: Text` <br>


## info


### info


#### Bootstrap_mpxj

Runs the bootstrap process for retrieving mpxj libs needed for reading .mpp files.

