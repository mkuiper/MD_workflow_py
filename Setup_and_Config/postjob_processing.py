#!/usr/bin/env python

import os
import sys 
import time
lib_path = os.path.abspath('../../mdwf_lib')
sys.path.append(lib_path)
import mdwf_functions as mdwf

""" A python script to help with post-processing of data of a MD simulation."""

jobid   = sys.argv[1]
jobtype = sys.argv[2]

# ansi color variables for formatting purposes: 
c0 = '\033[0m'        # default
c1 = '\033[31;2m'     # dark red
c3 = '\033[32;2m'     # dark green

## generic name of working MD files, (must be the same in .conf files). 
filename = "current_MD_run_files"

def main():
##  update local job details file: 
    mdwf.update_local_job_details( "JobStatus", "ready" )
    timestamp = "finished: " + time.strftime("%d%b:%H:%M", time.localtime())

    mdwf.update_local_job_details( "JobMessage",    timestamp )
    mdwf.update_local_job_details( "JobFinishTime", time.time() )

    mdwf.redirect_namd_output( filename, jobtype )  # -redirect output
    mdwf.check_job_runtime()                        # -check job ran long enough
    mdwf.post_jobrun_cleanup()                      # -cleanup files 

    mdwf.check_run_counter()                        # -check job counter

if __name__ == "__main__":
    main()



