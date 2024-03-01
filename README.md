# BaHo_pyRevit_Extension

## About
Basler & Hofmann pyRevit addon running on top of [pyRevit](http://gitlab.ideas.baho.ch/bim/revit/pyrevit/pyrevit)
Contains the reimplementation of the C# addon "Plan 4.0".

## Dependencies
Tested on and written for
* rvt 2023, 2024
* pyRevit 4.8.14
* mpxj library 12.7.0

## Development
### Tooling
* whole code base checked with `ruff check --ignore=E402` with the aim of having no ruff fix suggestions
  * since we run IronPython and have to extend our path or `clr.AddReference` in order to do imports, 
    we cannot fulfill E402
