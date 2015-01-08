#!/usr/bin/env python

import os
import sys 
import json
import time
from collections import OrderedDict

lib_path = os.path.abspath('../../mdwf_lib')
sys.path.append(lib_path)
import mdwf_functions as mdwf

""" A python script to help with postprocessing of data of a MD simulation."""

jobid   = sys.argv[1]
jobtype = sys.argv[2]

## generic name of working MD files. (for naming and redirection)
currentworkingfile = "current_MD_run_files"

def main():
## open and modify local job details file. 
    ljdf_t = mdwf.read_local_job_details_file(".", "local_job_details.json")

    ljdf_t['CurrentJobId'] = jobid
    ljdf_t['JobStatus'] = 'finished'
    ljdf_t['JobFinishTime'] = str(time.time())

    if "opt" in jobtype:
        ljdf_t['JobMessage'] = 'finished equilibration phase'

## check runtime/create pauseflag if less than designated runtime
    start  = float(ljdf_t['JobStartTime'])
    finish = float(ljdf_t['JobFinishTime'])
    limit  = int(ljdf_t['JobFailTime'])
    mdwf.check_job_fail(start,finish,limit)

## check run counter/create pauseflag in the event of an error
    current =  int(ljdf_t['CurrentRun'])
    total = int(ljdf_t['TotalRuns'])
    mdwf.check_run_count(current,total)

## rename and redirect current working filess 
    name = ljdf_t['JobBaseName']
    run  = str(ljdf_t['CurrentRun'])

    if "opt" in jobtype:
        mdwf.redirect_output('opt' + name, run, currentworkingfile )
    else:
        mdwf.redirect_output(name, run, currentworkingfile )

## check if all runs have completed and perform postjob clean if they have
    current =  int(ljdf_t['CurrentRun'])
    total = int(ljdf_t['TotalRuns'])
    mdwf.check_final_run(current, total)

## close local job details file:
    with open("local_job_details.json", 'w') as outfile:
        json.dump(ljdf_t, outfile, indent=2)
    outfile.close()
 
    
if __name__ == "__main__":
    main()



