#!/bin/bash
# Job reminder script. 
DIR = "CoV19_Spike_01"

for i in {1..30}
 do
   if [ "$i" -lt "10" ]; then
     echo "Spike_0$i"
     less ../CoV19Spike_01/Spike_0$i/namd_equil* |grep psf | grep structure
   fi

   if [ "$i" -gt "9" ]; then
     echo "Spike_$i"
     less ../CoV19Spike_01/Spike_$i/namd_equil* |grep psf | grep structure
   fi
   echo " "

done

