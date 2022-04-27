#!/bin/bash
# Job reminder script. 
# A simple script to help remind which jobs are running in which directories 
# by reading the input psf file from the configuration file, namd_equilibration_script.conf 
Red='\033[0;31m' # Red
Lbl='\033[1;34m' # Light blue
Yel='\033[0;33m' # Yellow
Lgr='\033[0;37m' # Light gray
NC='\033[0m'     # No Color


# Edit the list of job directories here:
for job_dir in  jobdir1 jobdir2 jobdir3  

do 
 printf "\n${Yel} /$job_dir ${NC} Input files: \n"

 for d in ../$job_dir/*/ ; 
  do 
   (cd "$d" && printf " ${Lgr} $d: ${Lbl}  " |tr -d "\n"; less namd_eq*| grep '.psf'| grep InputFiles |
    sed "s/structure     //" | sed "s/     ..\/..\/InputFiles\///"   ); 
  done

done
printf "${NC}"
