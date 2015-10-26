#!/bin/bash
##
## PBS render launching script          June 2013  MK
##
## -to run multiple rendering jobs, taking a plot file from Inbox, 
##  processing the image and moving the plot file to Outbox      

#PBS -l nodes=1:ppn=8           
#PBS -l walltime=24:0:0
#PBS -A VR0012


## Tachyon Rendering Variables: 
set aas    8     # aasampling higher is better quality, but slower! 8 is usually good enough. 
set xres   1024  # x resolution  - best to match with original input files 
set yres   768   # y resolution  - best to match with original input files  (ie 1024 x 768,  1900 x 1080 )
# set tachyon path:
tachyon_path="/usr/local/vmd/1.9.1-gcc/lib/tachyon_LINUXAMD64"

cd $PBS_O_WORKDIR
module load vmd-gcc/1.9.1
module load imagemagick

cd Inbox;

for i in *
 do
  if [ -f "$i" ]; then
   touch -f $i
## move file to Temp directory:
   mv $i ../Temp

## render command: 

$tachyon_path -aasamples $aas -res $xres $yres ../Temp/$i -format TARGA -o ../Frames/$i.tga

##  post rendering processing: (optional!) 
# convert from tga format to jpg, remove old tga if successful. 

 convert  ../Frames/$i.tga ../Frames/$i.jpg

 if [ -f ../Frames/$i.jpg ]; 
 then 
  rm ../Frames/$i.tga
 fi


##  move plot file to OutBox
  mv ../Temp/$i ../Outbox
  fi
done

#cleanup
cd ../
mv *.e* Errors/
mv *.o* Output/



