#!/usr/bin/env python

import os
import sys 
import shutil
import subprocess
import fileinput

""" A python script to help run benchmarking runs on avoca."""

# number of nodes to try for job (must be a multiple of 2 (or 1)):
nodelist = [1,2,4,8,16]
# nodelist = [1,2,4,8,16,32,64]        # -use a longer node list for bigger test jobs. 

# processors per node:
ppn = [1,4,8,16,64] 

# -------------------------------------------------------------
def run_benchmark():
    for i in nodelist:
	for j in ppn:
	    ntpn = 64/j
            bm_script = write_benchmark_config(i,j,ntpn)
            
            subprocess.Popen(['sbatch', bm_script])
            

def write_benchmark_config(i,j,ntpn):
    '''simple script to substitute values into benchmarking config script'''
    
    bm_name = 'bm_config.' + str(i) + '.' + str(j) + '.' + 'sbatch'
    name = bm_name
    shutil.copy( 'sbatch_benchmark_template', 'temp_bm_config')
    
    for line in fileinput.FileInput( 'temp_bm_config', inplace=True ):
        line = line.replace( 'XXXnodes', str(i)    )
        line = line.replace( 'XXXppn',   str(j)    )
        line = line.replace( 'XXXntpn',  str(ntpn) )
        sys.stdout.write(line)
   
    shutil.copy( 'temp_bm_config', bm_name ) 
    os.remove('temp_bm_config')
    return name  
    
if __name__ == "__main__": 
    run_benchmark()

