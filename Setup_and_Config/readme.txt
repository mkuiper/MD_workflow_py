Setup_and_Config directory notes. 

This directory contains the 'template' files which propagate to all 
production jobs under /Main_Job_Dir

Typically a job might start with an equilibration phase before starting 
a series of production runs. 

The equilibrating phase is launched with the "sbatch_start.template" and 
runs the "sim_opt.conf" script. At the completion of the equilibration 
run the "sbatch_start.template" will automatically launch the production 
runs, which is controlled by the "sbatch_production.template" script. 



 


