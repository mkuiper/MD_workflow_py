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
    if "opt" in jobtype:
        ljdf_t["RunCountDown"] = ljdf_t["TotalRuns"]


    with open("local_job_details.json", 'w') as outfile:
        json.dump(ljdf_t, outfile, indent=2)
    outfile.close()

    mdwf.check_job_fail() #create pausejob flag if job has crashed

#  move around data. 
 
    
if __name__ == "__main__":
    main()



