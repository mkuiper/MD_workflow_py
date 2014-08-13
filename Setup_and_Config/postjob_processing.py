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
    ljdf_t['JobFinishTime'] = time.time()
    
    #create pausejob flag if the simulation has crashed
    start = int(ljdf_t['JobStartTime'])
    finish = int(ljdf_t['JobFinishTime'])
    limit = int(ljdf_t['JobFailTime'])
    mdwf.check_job_fail(start,finish,limit)

    if "opt" in jobtype:
        ljdf_t["RunCountDown"] = ljdf_t["TotalRuns"]


    with open("local_job_details.json", 'w') as outfile:
        json.dump(ljdf_t, outfile, indent=2)
    outfile.close()

#  move around data. 
 
    
if __name__ == "__main__":
    main()



