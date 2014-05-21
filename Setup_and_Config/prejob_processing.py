#!/usr/bin/env python

import sys 
from ../mdwf_lib import mdwf_functions as mdwf

""" A python script to help setup the optimization phase of a MD simulation."""

jobid   = argv[2]
jobtype = argv[3]

def main():
    # read Local Job Details File and master_config file
    ljdf = read_local_job_details_file()
    
    # check Ok for job to run:
    check_disk_quota(ljdf["Account"],ljdf["DiskSpaceCutoff"])
    check_for_pausejob()

    # record job details:
    log_job_details(jobid)
#    record_start_time()
    update_job_status("ready")
    
if __name__ = "__main__":
    main()

