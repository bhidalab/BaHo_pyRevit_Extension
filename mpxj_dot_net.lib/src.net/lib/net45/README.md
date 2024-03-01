# About
In order for this pyRevit addon to be able to read from .mpp files, 
this directory needs to contain the mpxj library.
It can be found at https://github.com/joniles/mpxj
Any script missing the dlls on the system will error and inform 
the user to run `Bootstrap_mpxj`:
That bundled script [Bootstrap_mpxj](../../../../baho.extension/pyRevit_BH.tab/info.panel/info.pulldown/Bootstrap_mpxj.pushbutton/Bootstrap_mpxj_script.py) 
will download the required package to this directory.
