#!/usr/bin/env python

import sys
import os 

""" A python script to post-process data of a MD simulation."""
jobid = argv[2]


def optimization_cleanup():
    # read Local Job Details File
    ljdf = read_local_job_details_file()

    # check that job ran as expected:
    record_finish_time()
    check_job_fail()
    log_job_timing()

    update_job_status("ok")
    redirect_optimization_output()


def production_cleanup():
    # series of functions to perform a typical data post-processing
    # read Local Job Details File
    ljdf = read_local_job_details_file()

    # check that job ran as expected:
    record_finish_time()
    check_job_fail()
    log_job_timing()

    # redirect data
    update_job_status("ok")
    check_md5sum(filename)
    redirect_production_output()
    
    # adjust countdown timer:       
    countdown_timer()
    check_for_pausejob()
    update_job_status("ok:postjob cleanup")
    
    # ready to relaunch. 
    
if __name__ = "__main__":
    production_cleanup()

