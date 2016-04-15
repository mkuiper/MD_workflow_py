### MD_workflow_py

==================================================
 Molecular dynamics workflow framework in python.
==================================================
## working draft  1/04/2016
Note: This is a reworking of the MD workflow directory structure which 
was originally written in bash scripts.

===========
 Overview
===========
Molecular dynamics simulations have become much longer over time, which
reflects the advances in computation. Often, researchers also have much 
more computational capacity available, which allows them to run many 
more replicate jobs than before, gathering important statistical data
making their simulations more robust. The management of the simuations 
and subsequent data can be difficult.  

The aim of this workflow is to be able to easily set up and manage numerous 
molecular dynamics simulations. Most of the operations are designed to be 
run from the top of the directory, with a single function, './mdwf' which 
can do things like start and stop jobs on a cluster, monitor progress and 
even gather all the data for analysis. 

Requirements: 
The scripts used in this directory structure are written in python 2.7 
so you will need to have pyhton 2.7 somewhere in your path. On clusters 
systems, you may need to load a python2.7 module. 

A note before we start. This folder structure is just one way of organizing 
running of multiple jobs on a cluster. It may not be the best for your
research, but this folder is flexible enough you can populate it with 
your own scripts and design. 

======================
 The MD Job heirarcy. 
======================

Rather than running one long molecular dynamics simulation, it is better 
to break the simulations into a string of shorter runs which can be 
reassembled once complete. This makes it easier to schedule jobs on a 
cluster and provides better protection against data corruption. 
This workflow is designed to allow you to do just that, but also to create 
any number of replicate jobs and variants. 

The standard job block configuration scripts are located under the 
/Setup_and_Config directory though you can design your own workflow quite 
easily, even defining your own job directory structure under /JobTemplate

At the top of the job heirarcy is the "JobStreams"
Usually there is only one, but there can be multiple streams. These are
supposed to be a single sort of simulation. For example, one jobstream 
could be the wildtype solution. Another might be the mutant form, so the 

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

So for the example we have 2 main simulations:

  ProteinX_wt:			ProteinX_mutant:
	prot_wt_01		prot_mut_01
	prot_wt_02		prot_mut_02
	prot_wt_03		prot_mut_03
	prot_wt_04             (3 replicates)
	prot_wt_05
      (5 replicates)

Each replicate will run five times. 

Once you have defined your job structure in the 'master_config_file' 
and your inputfiles in '/Setup_and_Config' you can check everything 
with:
 ./mdwf -c          (which stands for 'checkjob') 

This will give you an overview of your setup and check that you have 
the correct input files. It will also estimate the amount of data you 
will generate and the amount of simulation time you will actually perform. 

Once you are satisfied with your setup, you will need to 'initialize' the
directory structure.  You can do this with: 
./mdwf -i 

This will build the directory structure you defined in 'master_config_file'
and add the folders as in /Setup_and_Config/JobTemplate
(you can define your own job structure here!) 

After the directory structure is initialized, you will need to populate the
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
This will recopy the files across but will not update the local_details_file
(we want to keep trak of where we are!) 

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

This should submit the jobs in each directory one by one. 

You can monitor the status of each job with the command:
./mdwf -m 

Should you need to stop all the jobs you can do so with: 
./mdwf --stop_jobs


After all your jobs are finished, you will be interested to concatenate 
and view your MD data with VMD.  This can be done with: 
./mdwf -g       

This descends through the directory structure, and makes a list of the 
data files which will be available in the /Analysis folder. 






To cleanup .git related files you may use:
rm -rf .git
also:
find . -name .gitkeep -type f -delete

 
