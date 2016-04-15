# MD_workflow_py

Molecular dynamics workflow framework in python.

## 16/12/2015

This is a reworking of the MD workflow directory structure which was originally
written in bash scripts.

The aim of this workflow is to be able to easily set up and manage numerous 
molecular dynamics simulations.

Rather than running one long simulation, it is better to break the simulations 
into a string of shorter runs as this is easier to schedule on a cluster and 
is better protection against data corruption. This workflow allows you to do 
just that, but also easily create any number of replicate jobs and variants. 

The standard job block configuration scripts are located under the /Setup_and_Config directory
and are usually set for a simulation for a relatively short simulation length.
(less than 24 hours). 



At the top of the job heirarcy is the "JobStreams"
Usually there is only one, but there can be multiple streams. These are
supposed to be a single sort of simulation. For example, one jobstream 
could be the wildtype solution.  Another might be the mutant form, so the 
JobStreams would be defined in the master_config_file as: 
"JobStreams"    : ["ProteinX_wt","ProteinX_mutant"],

Under each "JobStreams" we define the number of "job replicates" we wish to 
run. Say for the previous example we want 5 replicates for the wild type but only 
3 for the mutant. Our JobReplicate line would look like: 
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

Each replicate will run five times 



To cleanup .git related files you may use:
rm -rf .git
also:
find . -name .gitkeep -type f -delete

 
