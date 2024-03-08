# BaHo_pyRevit_Extension

## About
Basler & Hofmann pyRevit addon running on top of [pyRevit](http://gitlab.ideas.baho.ch/bim/revit/pyrevit/pyrevit) 4.8.14
Contains the partial reimplementation of C# addon "Plan 4.0".

## Dependencies
Tested on and written for
* rvt 2023, 2024
* pyRevit 4.8.14 <br>
  recommended install location: `c:\programdata\pyrevit_4.8.14`
* mpxj library 12.7.0 <br>
  not provided in this repo, use bundled pyRevit `BaHo_pyRevit_Extension / info / Bootstrap_mpxj`

## Installation
* Basler & Hofmann users: <br>
  use our regular [pyRevit_Installer](http://gitlab.ideas.baho.ch/bim/revit/pyrevit/pyrevit_installer) or ask @FBE
* external users:
  * install: rvt 2023 or 2024
  * install: pyRevit 4.8.14
    recommended install location: `c:\programdata\pyrevit_4.8.14`
  * download and unpack BaHo_pyRevit_Extension to: `c:\programdata\baho_pyrevit_extension`
  * in `pyRevit / Settings` add BaHo_pyRevit_Extension under `Custom Extension Directories` <br>
    preferred location for BaHo_pyRevit_Extension: `c:\programdata\baho_pyrevit_extension`
  * run the bootstrap script `info / Bootstrap_mpxj` to supply the required mpxj library

## Development
### Tooling
* whole code base checked with `ruff check --ignore=E402` with the aim of having no ruff fix suggestions
  * since we run IronPython and have to extend our path or `clr.AddReference` in order to do imports, 
    we cannot fulfill E402
