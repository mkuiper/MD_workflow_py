#!/usr/bin/env python

import os
import sys 
import shutil
import json
import subprocess
import fileinput
from datetime import datetime


""" A python script to help setup benchmarks runs on barcoo"""
def read_benchmark_parameters():
    """ Reads the json file 'BENCHMARK_SETUP.json' and
         returns the dictionary  """

    if os.path.isfile( 'BENCHMARK_SETUP.json' ):
        with open('BENCHMARK_SETUP.json') as json_data:
            bmp = json.load(json_data)
            json_data.close()
            return bmp
    else:
        print(("{}Can't see 'BENCHMARK_SETUP.json' {} "\
                .format(RED, DEFAULT)))
        exit()

def setup_benchmark():
    """ Sets up initial benchmark files and launches job """

    # read benchmark parameters:
    bmp = read_benchmark_parameters()
    psffile  = bmp["PSFFILE"] 
    pdbfile  = bmp["PDBFILE"] 
    pbcX     = bmp["PBC_X"] 
    pbcY     = bmp["PBC_Y"] 
    pbcZ     = bmp["PBC_Z"] 

    EqNode   = bmp["EquilNodes"]
    account  = bmp["ACCOUNT"]
    runtime  = bmp["RUNTIME"]
    module   = bmp["MODULEFILE"]

    # make equilibration config file.     
    shutil.copy( 'Templates/namd_equilibration_script.template', 'namd_equilibration_script.conf')
    shutil.copy( 'Templates/sbatch_initial_benchmark.template', 'sbatch_initial_benchmark')
    
    for line in fileinput.FileInput( 'namd_equilibration_script.conf', inplace=True ):
        line = line.replace('XXX.psf',  psffile)
        line = line.replace('XXX.pdb',  pdbfile)
        line = line.replace('PBCX',  pbcX)
        line = line.replace('PBCY',  pbcY)
        line = line.replace('PBCZ',  pbcZ)
        sys.stdout.write(line)

    for line in fileinput.FileInput( 'sbatch_initial_benchmark', inplace=True ):
        line = line.replace('XXXnode',    EqNode)
        line = line.replace('XXXtime',    runtime)
        line = line.replace('XXXmodule',  module)
        line = line.replace('XXXaccount', account)
        sys.stdout.write(line)

    # launch equilibration job
    subprocess.Popen(['sbatch', 'sbatch_initial_benchmark'])
    
if __name__ == "__main__": 
    setup_benchmark()

