#!/usr/local/python/3.6.0-gcc/bin/python3

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
    mdwf.update_local_job_details("JobFinishTime", time.time())
    mdwf.check_job_runtime()       

    timestamp = "Finished: " + time.strftime("%d%b:%H:%M", time.localtime())
    mdwf.update_local_job_details("JobMessage", timestamp)
    mdwf.update_local_job_details("JobStatus", "stopped")

    mdwf.redirect_namd_output(filename, jobtype)  # -redirect output
    mdwf.check_run_counter()                      # -check job counter
    mdwf.post_jobrun_cleanup()                    # -cleanup files 

if __name__ == "__main__":
    main()



