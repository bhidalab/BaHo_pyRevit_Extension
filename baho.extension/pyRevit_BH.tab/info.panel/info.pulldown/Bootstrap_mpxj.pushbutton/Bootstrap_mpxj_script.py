"""
Runs the bootstrap process for retrieving mpxj libs needed for reading .mpp files.
"""
from vrph import bootstrap_mpxj_lib, utils


stopwatch = utils.start_script_timer()

bootstrap_mpxj_lib.run_bootstrap()

utils.end_script_timer(stopwatch)
