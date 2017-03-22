#!/usr/local/python/3.6.0-gcc/bin/python3

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

##  performs checks before launching the job:  
    mdwf.check_disk_quota()        # -checks disk quota on system 
    mdwf.check_pausejob_flag()     # -checks for pausejob flag
 
##  update the local job details file: 
    mdwf.update_local_job_details( "CurrentJobId", jobid )
    mdwf.update_local_job_details( "JobStatus", "running" )
 
    timestamp = "started: " + time.strftime( "%d%b:%H:%M", time.localtime() )
    mdwf.update_local_job_details( "JobMessage",   timestamp  )
    mdwf.update_local_job_details( "JobStartTime", time.time()) 

if __name__ == "__main__":
    main()

