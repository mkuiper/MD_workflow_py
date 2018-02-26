#!/bin/bash

# Bracewell NAMD script. 

# Original Author: Tim Ho <tim.ho@csiro.au> modified by Mike Kuiper
# Support: contact schelp@csiro.au

# Slurm variables:   
#--------------------------------------------------------------
#SBATCH --nodes 2
#SBATCH --tasks-per-node 28
#SBATCH --gres gpu:2
#SBATCH --time=2:0:0

CONFIG=namd_production_script.conf

# Modules
#--------------------------------------------------------------
module load openmpi
module load namd/2.12-ibverbs-smp-cuda

# Job variables:
#--------------------------------------------------------------
NNODE=$SLURM_JOB_NUM_NODES
NTASKS=$SLURM_NTASKS_PER_NODE

GPUS=""
if [ "$CUDA_VISIBLE_DEVICES" != "" ]
then
  GPUS="+idlepoll +devices $CUDA_VISIBLE_DEVICES"
fi

# Logging data:
#--------------------------------------------------------------
echo $GPUS >> cuda.info
echo nvidia-smi >> cuda.info
scontrol show job $SLURM_JOBID >>scontrol.info

# Pre-processing script:
#--------------------------------------------------------------
if [ -f ../prejob_processing.py ];
 then python3 ../prejob_processing.py $SLURM_JOBID -production;
 else echo "No pre-processing script." > pausejob
fi

# Runaway checkpoint:
#--------------------------------------------------------------
if [ -f pausejob ]; then
    scancel $SLURM_JOBID;
    exit;
fi    

# Launching job:
#--------------------------------------------------------------
if [ $NNODE == 1 ]
 then
  # Single-node SMP
  namd2 ++ppn $NTASKS $GPUS "$CONFIG" >temp_working_outputfile.out 2>temp_working_errorsfile.err;

else
  # Multi-node SMP via MPI
  # PPN=`expr $SLURM_NTASKS_PER_NODE - 1 `   # <- usually one core reserved for comms. 
  PPN=`expr $SLURM_NTASKS_PER_NODE - 0 `
  P="$(($PPN * $SLURM_NNODES))"

  charmrun ++verbose ++mpiexec \
    ++remote-shell "`which mpirun` --map-by node" \
    `which namd2` ++p $P ++ppn $PPN +setcpuaffinity $GPUS \
    "$CONFIG" >temp_working_outputfile.out 2>temp_working_errorsfile.err;
fi

# Post-processing script:
#--------------------------------------------------------------
if [ -f ../postjob_processing.py ];
 then python3 ../postjob_processing.py $SLURM_JOBID -production;
 else echo "No post-processing script." > pausejob
fi

# Runaway checkpoint:
#--------------------------------------------------------------
if [ -f pausejob ]; then
    scancel $SLURM_JOBID;
    exit;
fi    
 
# Launch nextjob:
#--------------------------------------------------------------
sbatch sbatch_production_script


