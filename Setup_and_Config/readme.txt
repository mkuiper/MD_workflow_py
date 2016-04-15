/Setup_and_Config directory notes. 

The purpose of the /Setup_and_Config directory is to setup the  
design and workflow of your experiment. Though this was developed with 
molecular dynamics in mind, it could be adapted to run and manage any 
number of programs. 

There are 2 python scripts to do pre-processing and post-processing of the
data which are specific to the NAMD workflow. These could be modified for any
program. 

This directory structure has a number of template files which are copied 
and modified when the 'populate' flag is used in the top directory ie) 
./mdwf -p
This is defined in /mdwf_lib/mdwf_functions.py

