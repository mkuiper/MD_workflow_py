#!/usr/bin/env python

import os
import sys

""" A python script to help with post-processing of data of a MD simulation."""

outfile = sys.argv[1]

timings = []
b= outfile.split('.')
nodes = int(b[1])

# extracting timing data from the output file: 
def extract_timing_data(outfile):
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
    
      # calulate nanoseconds per day 
        nspd = 86400/ave * timestep /1000000.0    # Nanoseconds per day

    line = ( "%8.3f" % (nspd))
    return line

#def update_benchmarks():
   

def main():
    # check outputfile exists. 
    if os.path.isfile(outfile):
        timing= round((float(extract_timing_data(outfile))),3)     
        eff   = round((float(timing)/float(nodes)),3) 
        line2 = str(nodes)+",\t"+str(timing)+",\t"+str(eff) 
        with open("raw_benchmark_data.txt", "a") as f:
            f.write(line2)
            f.write("\n")
            f.close
    else:
        print "outputfile not found"

if __name__ == "__main__":
    main()



