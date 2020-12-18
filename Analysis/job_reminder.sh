#!/bin/bash
# Job reminder script. 
DIR = "CoV19_Spike_01"

for i in {1..10}
do 
  printf $i 
  less ../CoV19Spike_01/Spike_$i/namd_equil* |grep psf | grep structure
done
