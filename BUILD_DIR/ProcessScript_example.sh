#!/bin/bash
# Process Script Example                    Oct 2021  M kKuiper
# A better way,.... 

# This process script is designed to automate the reliable replication of any  
# modelliing process, including mdel building and trajectory analysis. 

# Building models and performing analysis typically involve a series of complex operations 
# that may be hard to reproduce accurately without a script. 

# This process script is an example for running a sequential scripts to build 
# various models and prepare input for production runs. 

# Dependencies: bash, python3, VMD, NAMD

run=01  # for different runs
home=/scratch1/kui001/NewMouse_2021/

for i in  model_01  model_02 model_03

do 

    # Build model with VMD  (must have already prepared build_ scripts, ie) build_model_01, etc)   
echo " Building model:"
vmd -dispdev text -e build_$i

# Solvate model using hexagonal PBC with vmd script. 
echo "Solvating model:"
vmd -dispdev text -e solvate_ionize_script.vmd 

# Optimize model (submits short NAMD job to queue and waits for completion) 
echo "Optimizing model:"
sbatch --wait sbatch_optimization &
wait
echo "Done optimizing."

# Process ionized dcd file -> Prepare production run
echo "Preparing production input."
vmd -dispdev text -e process_ionized_dcd.vmd
cp ionized.psf $home/InputFiles/$i.psf
cp ionized.pdb $home/InputFiles/$i.pdb





## Temmporary block:
# Copy old input files back for new production:
cp  $home/InputFiles/$i.psf ionized.psf
cp  $home/InputFiles/$i.pdb ionized.pdb
# Reporcess to set correct constraints:
vmd -dispdev text -e $home/BUILD_DIR/process_ionized_dcd.vmd


# Run production trajectory
echo "Running production: $i " 
sbatch --wait $home/BUILD_DIR/sbatch_production &
wait

# Process production run to extract B and D chains
rm evoef2_pdbfile.pdb  # remove old data file 
vmd -dispdev text -e process_production_dcd.vmd
cp evoef2_trajectory.pdb $home/BUILD_DIR/Output/Trajectory/$i.$run.pdb

# Prepare Output data:
echo "Run $run |  `date`" >> $home/BUILD_DIR/Output/$i.txt

# Process pdb trajectory with EvoEf2 script:
echo "Procesing binding"
python $home/BUILD_DIR/EvoEF2_processing_script_V1.py &
wait

cat temp_evoef2_data.txt >> $home/BUILD_DIR/Output/$i.txt

done

