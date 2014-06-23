#!/usr/bin/env python

import sys 
from ../mdwf_lib import mdwf_functions as mdwf

""" A python script to help setup the optimization phase of a MD simulation."""

jobid   = argv[2]
jobtype = argv[3]

def main():
    # read Local Job Details File and master_config file
    ljdf = mdwf.read_local_job_details_file()
    
    # check Ok for job to run:
    mdwf.check_disk_quota(ljdf["Account"],ljdf["DiskSpaceCutoff"])
    mdwf.check_for_pausejob()
    
    # initialize job counter if optimize flag set.  
    if "optimize" in jobtype:
        ljdf["RunCountDown"] = ljdf["TotalRuns"]    

    else: 
        # move files about:
        print ""


        
    # record job details:
    mdwf.log_job_details(jobid)
    
if __name__ = "__main__":
    main()

