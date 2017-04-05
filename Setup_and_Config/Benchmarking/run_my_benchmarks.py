#!/usr/bin/env python

import os
import sys 
import shutil
import json
import subprocess
import fileinput
from datetime import datetime
from Benchmark_setup import read_benchmark_parameters

""" A python script to help run benchmarking runs on barcoo"""
def run_benchmark():
    # check if input files exists.
    if not os.path.exists("bm_input.coor"):
        print("Input files not found. Have you run the benchmark setup to generate input files? \n(python Benchmark_setup.py)")
        exit()

    # read benchmark parameters:
    bmp = read_benchmark_parameters()
    nodelist = bmp["NODELIST"]
    account  = bmp["ACCOUNT"]
    runtime  = bmp["RUNTIME"]
    module   = bmp["MODULEFILE"]

    date = datetime.now().strftime("%d:%m:%Y %H:%M ")
    p = "Starting new benchmark run: " + date + "\nNodes  \tns/day\tns/node            (ns- nanoseconds)"    
    with open("raw_benchmark_data.txt", "w") as f:
            f.write(p)
            f.write("\n")
            f.close
    
    for i in nodelist:
        bm_script = write_benchmark_config(i, account, runtime, module)
        subprocess.Popen(['sbatch', bm_script])

def write_benchmark_config(i, account, runtime, module):
    '''simple script to substitute values into benchmarking config script'''
    
    bm_name = 'bm_config.' + str(i) + '.sbatch'
    name = bm_name
    shutil.copy( 'Templates/sbatch_benchmark_template', 'temp_bm_config')
    
    for line in fileinput.FileInput( 'temp_bm_config', inplace=True ):
        line = line.replace('XXXnodes', str(i)    )
        line = line.replace('XXXaccount', account)
        line = line.replace('XXXtime', runtime)
        line = line.replace('XXXmodule', module)
        sys.stdout.write(line)
   
    shutil.copy( 'temp_bm_config', bm_name ) 
    os.remove('temp_bm_config')
    return name  
    
if __name__ == "__main__": 
    run_benchmark()

