#!/usr/bin/env python

#!/usr/bin/env python

import sys
from ../mdwf_lib import mdwf_functions as mdwf

""" A python script to post process data files after a MD simulation."""

jobid   = argv[2]
jobtype = argv[3]

def main():

    check_job_runtime()
    check_for_clean_exit()
    
    redirect_output()
    
    



if __name__ = "__main__":
    main()
