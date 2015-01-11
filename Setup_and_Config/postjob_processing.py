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

## generic name of working MD files, (must be the same in .conf files). 
filename = "current_MD_run_files"

def main():

##  update local job details file: 
    mdwf.update_local_job_details( "JobStatus",     "ready"   )
    mdwf.update_local_job_details( "JobMessage",    "finished job run" )
    mdwf.update_local_job_details( "JobFinishTime", time.time() )

    if "opt" in jobtype:
        mdwf.update_local_job_details( "JobMessage", "finished eqilibration " )

    mdwf.check_job_runtime()                        # -check job ran long enough
    mdwf.redirect_namd_output( filename, jobtype )  # -redirect output
    mdwf.post_jobrun_cleanup()                      # -cleanup files 
    mdwf.check_run_counter(1)                       # -counts down run counter

if __name__ == "__main__":
    main()



