#!/usr/bin/env python
# startjob_initialize.py 

import os 


""" A python script to help setup the optimization phase of a MD simulation."""


jobid = argv[2]

def main():
    # read Local Job Details File
    ljdf = read_local_job_details_file()

    # check Ok for job to run:
    check_for_pausejob()
    try:
        check_disk_quota()
    except:
        print "system disk quota not checked properly"

    # record job details:
    log_job_details()
    record_start_time()
    update_job_status("ready")
    
if __name__ = "__main__":
    main()

