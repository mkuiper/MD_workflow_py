#!/usr/bin/env python

import os
import sys

""" A python script to help with post-processing of data of a MD simulation."""

outfile = sys.argv[1]
jobID = sys.argv[2]

timings = []
b= outfile.split('.')
nodes = int(b[1])
ppn = int(b[2])
ntpn = 64/ppn

# this script extracts timing data from the output file. 

def extract_data(outfile):
    with open(outfile,"r") as f:
        for line in f:
	   if 'Info: TIMESTEP' in line:           # Find timestep information. 
	       ll = line.split()
               timestep = float(ll[2])
           if 'TIMING:' in line:                  
	       ll = line.split()
               timings.append(float(ll[4][:-5]))  # Extract seconds per step, append to list.

    if (len(timings)>=3):                         # Take average of last 3 timings:
        ave = (timings[-1]+timings[-2]+timings[-3])/3.0 
    
        nspd = 86400/ave * timestep /1000000.0    # Nanoseconds per day

    
    line = ( "%8.3f" % (nspd))
    #print neline   
    return line

#def update_benchmarks():
   

def main():
    # check outputfile exists. 
    if os.path.isfile(outfile):
        timing = extract_data(outfile)    
        p = "%d,  %d,  %d,  %s " % (nodes, ppn, ntpn, timing)
        with open("raw_benchmark_data.txt", "a") as f:
            f.write(p)
            f.write("\n")
            f.close

#   update_benchmarks()
    else:
        print "outputfile not found"

if __name__ == "__main__":
    main()





