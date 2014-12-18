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

def main():
    # open and modify local job details file. 
    ljdf_t = mdwf.read_local_job_details_file(".", "local_job_details.json")
    ljdf_t['CurrentJobId'] = jobid
    ljdf_t['JobStatus'] = 'finished'
    ljdf_t['JobFinishTime'] = str(time.time())

    with open("local_job_details.json", 'w') as outfile:
        json.dump(ljdf_t, outfile, indent=2)
    outfile.close()

    #check runtime/create pauseflag if less than designated runtime
    start = float(ljdf_t['JobStartTime'])
    finish = float(ljdf_t['JobFinishTime'])
    limit = int(ljdf_t['JobFailTime'])
    mdwf.check_job_fail(start,finish,limit)

    #check run counter/create pauseflag in the event of an error
    current =  int(ljdf_t['RunCount'])
    total = int(ljdf_t['TotalRuns'])
    mdwf.check_run_count(current,total)

    #check if job has hit walltime
    #walltime = int(ljdf_t['WallTime'])
    #mdwf.check_walltime(start,finish,walltime)

    #move around and rename files 
    name = ljdf_t['JobBaseName']
    run = str(ljdf_t['RunCount'])
    if "opt" in jobtype:
        mdwf.redirect_optimization_output(name, run)
    else:
        mdwf.redirect_production_output(name, run)

    #check if all runs have completed and perform postjob clean if they have
    current =  int(ljdf_t['RunCount'])
    total = int(ljdf_t['TotalRuns'])
    mdwf.check_final_run(current, total)

 
    
if __name__ == "__main__":
    main()



