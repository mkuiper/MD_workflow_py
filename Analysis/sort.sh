#!/bin/bash
# Trajectory sorting template

# Simple template for sorting output from main fileloader 
# Usually would first run 'gather' (./mdwf -g from top directory)
# to generate dcd_trajectory_fileloader.vmd in /Analysis
# then run ./sort.sh here. 

less dcd_trajectory_fileloader.vmd |grep SEL_001 > sel_001.vmd 
less dcd_trajectory_fileloader.vmd |grep SEL_002 > sel_002.vmd 
less dcd_trajectory_fileloader.vmd |grep SEL_003 > sel_003.vmd 
less dcd_trajectory_fileloader.vmd |grep SEL_004 > sel_004.vmd
less dcd_trajectory_fileloader.vmd |grep SEL_005 > sel_005.vmd 
less dcd_trajectory_fileloader.vmd |grep SEL_006 > sel_006.vmd 
less dcd_trajectory_fileloader.vmd |grep SEL_007 > sel_007.vmd 
less dcd_trajectory_fileloader.vmd |grep SEL_008 > sel_008.vmd 

