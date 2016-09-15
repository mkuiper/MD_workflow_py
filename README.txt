### MD_workflow_py

==================================================
 Molecular dynamics workflow framework in python.
==================================================
## working draft document 1/04/2016
Note: This is a reworking of the MD workflow directory structure which 
was originally written in bash scripts.

===========
 Overview
===========
Molecular dynamics simulations have typically become much longer as the 
advances in computation make this feasible. Additionally, researchers 
have also much more computational capacity available, which allows them to 
run many more replicate jobs than before, thereby gathering important 
statistical data making their simulations more robust. However, with these
advances also come new problems, particularly the management of large numbers 
simulations and data.   

The aim of this workflow is to be able to easily set up and manage numerous 
molecular dynamics simulations. It was originally designed to help run namd 
jobs on Avoca, a Bluegene/Q supercomputer, but can be adapted for most cluster. 
The philosophy of this workflow was to create a self-contained folder where a
researcher could contain all the files they used to build, run and analyse their 
simulations with a good deal of reproducibility. 

===========================
 The Directory Structure:
===========================

/Analysis		<- md analysis done here
/BUILD_DIR		<- models built here
/Examples		<- some example files here
/InputFiles		<- input files and parameters stored here
/JobLog			<- Job running details recorded here 
/mdwf_lib		<- Script files stored here 
/Project 		<- Files related to project here, also movie making scripts 
/Setup_and_Config       <- Where the job is defined and setup        
  |-JobTemplate
  |-Benchmarking
/<JOBSTREAM>         	<- created at initialization, defined in master_config_file
                           (directory to contain simulation data, can have any name) 
master_config_file      <- file to control set-up and running
mdwf                    <- master python script to control running 
project_plan.txt	<- to help you plan your simulations 

----------------------------------------

Most of the operations are designed to be run from the top of the directory, 
with a single function, './mdwf' which can do things like start and stop jobs 
on a cluster, monitor progress and even gather all the data for analysis. 

Requirements: 
The scripts used in this directory structure are written in python 2.7 
so you will need to have python 2.7 somewhere in your path. On clusters 
systems, you may need to load a python2.7 module. 

A note before we start. This folder structure is just one way of organising 
running of multiple NAMD jobs on a cluster. It may not be the best for your
research, but this folder is flexible enough you can populate it with 
your own scripts and design. 

======================
 The MD Job hierarchy. 
======================

Rather than running one long molecular dynamics simulation, it is often 
better to break the simulations into a string of shorter runs which can be 
reassembled once complete. This makes it easier to schedule jobs on a 
cluster and provides better protection against data corruption should crash
occur. This workflow is designed to allow you to do just that, but also to create 
any number of replicate jobs and variants. 

The standard job block configuration scripts are located under the 
/Setup_and_Config directory though you can design your own workflow, even 
defining your own job directory structure under /JobTemplate. A very important 
configuration file called 'master_config_file' (which is a json file) sit at the 
top of the directory and defines the overall job structure. 

At the top of the job hierarchy is the 'JobStreams'
Usually there is only one, but there can be multiple streams. These are
supposed to represent a single sort of simulation. For example, one jobstream 
could be the wildtype protein. Another might be the mutant form, so the 
JobStreams would be defined in the master_config_file as: 
"JobStreams"    : ["ProteinX_wt","ProteinX_mutant"],

Under each "JobStreams" we define the number of "Job replicates" we wish to 
run. Say for the previous example we want 5 replicates for the wild type 
but only 3 for the mutant. Our JobReplicate line would look like: 
"JobReplicates" : ["5","3"],

We also define the base directory name for each replicate:
"BaseDirNames"  : ["prot_wt_","prot_mut_"],
(these will be labelled incrementally)

We also define the base names for the replicates themselves:
"JobBaseNames"  : ["wt_run1_","mutant_run1_" ],

and finally we define the number of simulations to perform with "Runs"
"Runs"          : ["5","5"],

So for this example we have 2 main simulations:

  ProteinX_wt:	  ProteinX_mutant:     <- Job Streams
 -------------   ------------------
  prot_wt_01	  prot_mut_01          <- Job Replicates
  prot_wt_02	  prot_mut_02
  prot_wt_03	  prot_mut_03
  prot_wt_04     (3 replicates)
  prot_wt_05
 (5 replicates)

Each replicate will run five times, giving a total of 5x5(wt) + 3x5(mutant) 
of 40 simulations runs to be completed. All the input files for both streams 
are usually located in the /InputFiles directory.    

============================== 
 Setting up the simulations:
==============================
Once you have defined your job structure in the 'master_config_file' 
and your input files in '/Setup_and_Config' you can check everything 
with:
 ./mdwf -c          (which stands for 'checkjob') 

This will give you an overview of your setup and check that you have 
the correct input files. It will also estimate the amount of data you 
will generate and the amount of simulation time you will actually perform. 

Once you are satisfied with your setup, you will need to 'initialize' the
directory structure.  You can do this with: 
./mdwf -i 

This will build the directory structure you defined in 'master_config_file'
ie) as by the lists in 'JobStreams', 'JobReplicates','baseDirNames',etc
and add the folders as in /Setup_and_Config/JobTemplate
(you can define your own job structure here!) 

After the directory structure is initialized, you will need to 'populate' the
folders.  Do this with the -p flag.  ie:
./mdwf -p 

This should copy all the important files in Setup_and_Config to each job 
folder. There is quite some flexibility in this system, you can upload any 
number of files needed for your job. Just park them in /Setup_and_Config  
(I have some additional python scripts here, which do the prejob and postjob
processing and handling of the data files.)

The 'populate' function is also a handy way of doing a bulk update of 
running files across all job folders.  Simply make the script changes in 
/Setup_and_Config , go to the top directory and type ./mdwf -p
This will recopy the files across but *will not* update the local_details_file
(we want to keep track of where we are!). 

If you mess everything up, and want to start again, use:
./mdwf --erase_all_data
    
Careful. This will do what it says and remove all the job folders, 
(Other folders such as /Setup_and_Config remain untouched.) 

===============================
 Running and monitoring jobs:
===============================

Once you have set up your job structures and populated them with files, 
you are ready to launch the jobs. You can do this with: 
./mdwf -s 

This submits the jobs in each directory one by one. 

You can monitor the status of each job with the command:
./mdwf -m 

Should you need to stop all the jobs immediately you can do so with: 
./mdwf --stop_jobs

If you prefer to pause the jobs, allowing current runs to finish, use
./mdwf --pause
This writes a 'pausejob' file in each directory which causes the runs to stop.  


After all your jobs are finished, you will be interested to concatenate 
and view your MD data with VMD.  This can be done with: 
./mdwf -g       

This descends through the directory structure, and makes a list of the 
data files which will be available in the /Analysis folder. 
Once in the Analysis folder, open VMD and read in the model_loader.vmd file 
and dcd_trajectory_fileloader.vmd file.  This will read in the data, ready 
for analysis. 




=================
 Miscellaneous:
=================

To cleanup .git related files you may use:
rm -rf .git
also:
find . -name .gitkeep -type f -delete



 
