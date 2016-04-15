#!/usr/bin/env python

import os
import sys 
import shutil
import subprocess
import fileinput

""" A python script to help run benchmarking postprocessing on avoca."""



for line in fileinput.FileInput( f, inplace=True ):
line = line.replace( '#SBATCH --nodes=X',   nnodes   )
                line = line.replace( '#SBATCH --time=X',    ntime    )
                line = line.replace( '#SBATCH --account=X', naccount )
                line = line.replace( 'ntpn=X',              nntpn    )
                line = line.replace( 'ppn=X',               nppn     )
                line = line.replace( 'module load X',       nmodule  )
                line = line.replace( 'optimize_script=X',   nopt     )
                line = line.replace( 'production_script=X', nprod    )
                sys.stdout.write(line)

