#!/usr/bin/env python

import os
import sys 
import json
import time
from collections import OrderedDict
lib_path = os.path.abspath('../../mdwf_lib')
sys.path.append(lib_path)
import mdwf_functions as mdwf

""" A python script to help do the data preprocessing before submitting the job."""

jobid   = sys.argv[1]     # job id of submitted job.  
jobtype = sys.argv[2]     # job type, 

def main():
## read details from 'local job details file':
    ljdf_t     = mdwf.read_local_job_details_file(".", "local_job_details.json" )
    account    =      ljdf_t[ "Account"         ] 
    run_number = int( ljdf_t[ "CurrentRun"      ] )
    total_runs = int( ljdf_t[ "TotalRuns"       ] )
    diskspace  = int( ljdf_t[ "DiskSpaceCutOff" ] )

## update the local job details file: 
    mdwf.update_local_job_details_file( "CurrentJobId",  jobid      )
    mdwf.update_local_job_details_file( "JobStatus",    "running"   )
    mdwf.update_local_job_details_file( "JobStartTime",  time.time()) 

## performs checks before launching the job:  
    mdwf.check_for_pausejob()                      
    mdwf.check_disk_quota( account, diskspace )    
    mdwf.check_run_count( run_number, total_runs ) 

## add +1 to RunCount in ljdf, set round to 0 if opt job
       
if __name__ == "__main__":
    main()



