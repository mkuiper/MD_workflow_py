#!/usr/bin/env python

import os
import sys 
import time
lib_path = os.path.abspath('../../mdwf_lib')
sys.path.append(lib_path)
import mdwf_functions as mdwf

""" A python script to help do the data pre-processing before submitting the job."""

jobid   = sys.argv[1]     # job id of submitted job.  
jobtype = sys.argv[2]     # job type, 

def main():

## update the local job details file: 
    mdwf.update_local_job_details( "CurrentJobId",  jobid      )
    mdwf.update_local_job_details( "JobStatus",    "running"   )
 
    timestamp = "started at " + time.strftime("%Y_%d%b_%H:%M", time.localtime())
    mdwf.update_local_job_details( "JobMessage",  timestamp  )
    mdwf.update_local_job_details( "JobStartTime",  time.time()) 

## performs checks before launching the job:  
    mdwf.check_for_pausejob()      # -checking for pause flags                
    mdwf.check_disk_quota()        # -checks disk quota on system
    mdwf.check_run_counter(0)      # -checks job countdown/increments job:

## re-read local job details script, check for fails. Cancel if required.
    ljdf_t = mdwf.read_local_job_details_file( ".", "local_job_details.json" )
    pauseflag  = ljdf_t[ "PauseJobFlag" ] 
    
    if pauseflag != "0":
        mdwf.cancel_job( jobid )   # -the job should stop here if checks fail    	    

if __name__ == "__main__":
    main()

