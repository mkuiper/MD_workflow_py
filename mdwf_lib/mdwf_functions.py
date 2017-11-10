#!/usr/bin/env python3
# MD workflow functions.   mdwf
""" mdwf functions.                    version 0.5
"""
import os
import subprocess
import sys
from   collections import OrderedDict
import json
import shutil
import fileinput
import hashlib
import time
import datetime
from   glob import glob
import re

# ansi color variables for formatting purposes:
DEFAULT = '\033[0m'
RED     = '\033[31m'
GREEN   = '\033[32m'
YELLOW  = '\033[33m'
BLUE    = '\033[34m'

## Read File Functions:
def read_master_config_file():
    """ Reads the json file 'master_config_file' and
         returns the dictionary. """

    if os.path.isfile( 'master_config_file' ):
        master_json = open( 'master_config_file' )
        mcf = json.load(master_json,object_pairs_hook=OrderedDict)
        master_json.close()
        return mcf
    else:
        print(("{}Can't see 'master_config_file' {} "\
                .format(RED, DEFAULT)))
        print(("{}Have you populated the directory? (./mdwf -p){}"\
                .format(RED, DEFAULT)))
def read_local_job_details(path="Setup_and_Config",
        ljdf_target="local_job_details_template.json"):
    """ Reads the json file 'local_job_details.json' and
        returns the dictionary. """

    target = path + "/" + ljdf_target

    if os.path.isfile(target):
        local_json = open(target)
        ljdf = json.load(local_json,object_pairs_hook=OrderedDict)
        local_json.close()
        return ljdf
    else:
        print(("Can't see {} Have you populated job tree? ".format(target)))
        return
def read_namd_job_details(targetfile):
    """ Extracts simulation details from given namd config file
        and returns a dictionary and a list. The function assumes
        namd files are located in /Setup_and_Config. """

    target = os.getcwd() + "/Setup_and_Config/" + targetfile
    jdd = {}    # job-details dictionary
    jdpl = []   # job details parameter list

    if os.path.isfile(target):
        f = open(target,'r')
        for lline in f:
            line = lline[0:18]         # strip line to avoid artifacts
            if not  "#" in line[0:2]:   # leave out commented lines
                if 'structure ' in line:
                    pl = lline.split( )
                    jdd["psffilepath"] = pl[1]
                    nl = re.split(('\s+|/|'),lline)
                    for i in nl:
                        if '.psf' in i:
                            jdd["psffile"] = i
                            natom = get_atoms(i)
                            jdd["natom"] = natom

                if 'coordinates ' in line:
                    pl = lline.split( )
                    jdd["pdbfilepath"] = pl[1]
                    nl = re.split(('\s+|/|'),lline)
                    for i in nl:
                        if '.pdb' in i:
                            jdd["pdbfile"] = i

                if 'timestep ' in line:
                    nl = lline.split( )
                    jdd["timestep"] = nl[1]

                if 'NumberSteps ' in line:
                    nl = lline.split( )
                    jdd["steps"] = nl[2]

                if 'dcdfreq ' in line:
                    nl = lline.split( )
                    jdd["dcdfreq"] = nl[1]

                if 'run ' in line:
                    nl = lline.split( )
                    jdd["runsteps"] = nl[1]

                if 'restartfreq ' in line:
                    nl = lline.split( )
                    jdd["restartfreq"] = nl[1]

                if 'parameters ' in line:
                    nl = lline.split( )
                    jdpl.append(nl[1])
        f.close()
    else:
        print(("{} {} file not found.{}".format(RED,targetfile,DEFAULT)))
    return jdd, jdpl


## Job control functions:
def monitor_jobs():
    """ Function to monitor jobs status on the cluster. """

    mcf = read_master_config_file()
    if not mcf:
        return

    account  = mcf["Account"]
    walltime = mcf["Walltime"]
    nodes    = mcf["Nodes"]
    cwd = os.getcwd()
    JobStreams, Replicates, BaseDirNames, JobBaseNames, Runs, nJobStreams,\
                nReplicates, nBaseNames = check_job_structure()
    print((" Account: %6s    nodes: %-6s " % (account, nodes)))
    print( " Job Name:      |Count    |JobId    |Status     |Runtime |Job_messages:")
    print((" ---------------|---------|---------|-----------|{:^7} |------------ ".format( walltime[:-2])))

    for i in range(0,nJobStreams):
        JobDir = JobStreams[i]
        jobdirlist = get_current_dir_list(JobDir)
        if not jobdirlist:
            return

        print(("%-24s " %( GREEN + JobDir + ":"+ DEFAULT )))
        for j in jobdirlist:
            dir_path = JobDir + "/" + j
            ljdf_t = read_local_job_details(dir_path, "local_job_details.json")
            if not ljdf_t:
                return

            jdn    = ljdf_t["JobDirName"]
            qs     = ljdf_t["QueueStatus"]
            js     = ljdf_t["JobStatus"]
            jm     = ljdf_t["JobMessage"]
            startT = ljdf_t["JobStartTime"]
            T      = get_job_runtime( startT, js )
            cjid = str(ljdf_t["CurrentJobId"])
            prog =  str( ljdf_t["CurrentRun"] ) + "/" + \
                    str( ljdf_t["TotalRuns"] )
            print(("{:16}|{:>8} |{:>8} | {: <10}|{:^8}| {:<20} "\
                     .format(jdn[0:15], prog, cjid, js, T, jm)))

    print(("\n{}done.".format(DEFAULT)))

def initialize_job_directories():
    """ Function to setup and initialize job structure directories
        as defined in the 'master_config_file'. This function copies
        the job template from /Setup_and_Config. """

    cwd=os.getcwd()
    JobStreams, Replicates, BaseDirNames, JobBaseNames, Runs, nJobStreams,\
                nReplicates, nBaseNames = check_job_structure()

  # Create Job Stream structure:  /JobStreams/JobReplicates
    for i in range(0, nJobStreams):
        TargetJobDir = cwd + "/" + JobStreams[i]
        if not os.path.exists(TargetJobDir):
            print(("Job Stream directory /{} does not exist. \nMaking new directory.\n".format(TargetJobDir)))
            os.makedirs(JobStreams[i])

      # Copy directory structure from /Setup_and Config/JobTemplate
        print(("Making job replicates in /{}".format(JobStreams[i])))
        TemplatePath = cwd + "/Setup_and_Config/JobTemplate"

      # Check existance of JobTemplate directory:
        if not os.path.exists(TemplatePath):
            print("Can't find the /Setup_and_Config/JobTemplate \
                   directory. Exiting.")
            sys.exit(error)

        replicates = int(Replicates[i])
        zf = len(str(replicates)) + 1      # for zfill

        for j in range(1,replicates+1):
            suffix = str(j).zfill(zf)
            NewDirName = JobStreams[i] + "/" + BaseDirNames[i] + suffix

            if os.path.exists(NewDirName):
                print(("Replicate job directory {} already exists! \
                       -Skipping.".format(NewDirName)))
            else:
                shutil.copytree(TemplatePath, NewDirName)
                print(("Creating:{}".format(NewDirName)))
def populate_job_directories():
    """ Function to populate or update job directory tree
        with job scripts that are located in /Setup_and_Config. """

    JobStreams, Replicates, BaseDirNames, JobBaseNames, Runs, \
    nJobStreams, nReplicates, nBaseNames = check_job_structure()

    mcf    = read_master_config_file()
    ljdf_t = read_local_job_details()
    cwd=os.getcwd()
    ljdf_t[ 'BASE_DIR' ]        = cwd
    ljdf_t[ 'Account' ]         = mcf["Account"]
    ljdf_t[ 'Nodes' ]           = mcf["Nodes"]
    ljdf_t[ 'Walltime' ]        = mcf["Walltime"]
    ljdf_t[ 'JobFailTime' ]     = mcf["JobFailTime"]

    Flavour          = mcf["Flavour"]
    OptScript        = mcf["EquilibrateConfScript"]
    ProdScript       = mcf["ProductionConfScript"]
    ModuleFile       = mcf["ModuleFile"]
    startscript      = mcf["SbatchEquilibrateScript"]
    productionscript = mcf["SbatchProductionScript"]

  # List files to transfer:
    print(("{}Job Files to transfer from /Setup_and_Config:{}"\
           .format(GREEN, DEFAULT)))
    print(("{} {}\n {}".format(DEFAULT, startscript,\
            productionscript)))
    print(" local_job_details.json ")
    for pyfile in glob(r'Setup_and_Config/*.py' ):
        print((" " + pyfile[17:]))
    for conffile in glob(r'Setup_and_Config/*.conf' ):
        print((" " + conffile[17:]))

  # Descend through job structure and populate job directories:
    for i in range(0, nJobStreams):
        TargetJobDir = cwd + "/" + JobStreams[i]
        print(("{}\nPopulating JobStream: {} {}".format( GREEN,
                                      TargetJobDir, DEFAULT)))

  # Check to see if there actually are any job directories to fill:
        if not os.path.exists( TargetJobDir ):
            print(("Job directory {} not found. Have you initialized?"\
                   .format(TargetJobDir)))
            sys.exit()

  # Create temporary sbatch scripts:
        sb_start_template = "Setup_and_Config/" + startscript + ".template"
        sb_prod_template  = "Setup_and_Config/" + productionscript + ".template"
        if not os.path.exists( sb_start_template ) \
                  or not os.path.exists( sb_prod_template ):
            print("Can't find sbatch template files in Settup_and_Config. Exiting.")
            sys.exit()

  # Modify replicate elements in staging dictionary file:
        ljdf_t['JOB_STREAM_DIR'] = JobStreams[i]
        ljdf_t['CurrentRun']     = 0
        ljdf_t['TotalRuns']      = int( Runs[i] )
        ljdf_t['JobBaseName']    = JobBaseNames[i]

        nnodes   = "#SBATCH --nodes="   + mcf["Nodes"]
        ntime    = "#SBATCH --time="    + mcf["Walltime"]
        naccount = "#SBATCH --account=" + mcf["Account"]
        tpn      = "#SBATCH --tasks-per-node=" + mcf["TaskPerNode"]
        gpus     = "#SBATCH --gres gpu:"   + mcf["GPUsPerNode"]
        nmodule  = "module load "       + ModuleFile
        nopt     = "optimize_script="   + OptScript
        nprod    = "production_script=" + ProdScript

        shutil.copy( sb_start_template, 'sb_start_temp')
        shutil.copy( sb_prod_template,  'sb_prod_temp' )

  # Replace lines in sbatch files:
        for f in ["sb_start_temp", "sb_prod_temp"]:
            for line in fileinput.FileInput( f, inplace=True ):
                line = line.replace('#SBATCH --nodes=X',   nnodes  )
                line = line.replace('#SBATCH --time=X',    ntime   )
                line = line.replace('#SBATCH --account=X', naccount)
                line = line.replace('#SBATCH --tasks-per-node=X', tpn)
                line = line.replace('#SBATCH --gres gpu:X', gpus)
                line = line.replace('module load X',       nmodule )
                line = line.replace('optimize_script=X',   nopt    )
                line = line.replace('production_script=X', nprod   )
                sys.stdout.write(line)

  # Copy across python and config scripts from /Setup_and_Config to top of each job dir
        jobpath  = JobStreams[i] + "/"
        for pyfile in glob(r'Setup_and_Config/*.py' ):
            shutil.copy2( pyfile, jobpath )
        for conffile in glob(r'Setup_and_Config/*.conf' ):
            shutil.copy2(conffile, jobpath)

  # Populate job directories with local_job_details and sbatch files
        jobdirlist = sorted(get_current_dir_list(jobpath))
        if jobdirlist:
            for j in jobdirlist:
                print(("{} -populating: {}{}".format(DEFAULT, j, DEFAULT)))
                ljdf_t['JobDirName'] = j
                ljdfile = JobStreams[i] + "/" + j + "/local_job_details.json"


                if not os.path.isfile(ljdfile):
                    with open(ljdfile, 'w') as outfile:
                        json.dump(ljdf_t, outfile, indent=2)
                    outfile.close()
                else:
                    print(" skipping local_details_file: already exists ")

                jobpath  = JobStreams[i] + "/" + j + "/"
                sbs_path = jobpath       + "/" + startscript
                sbp_path = jobpath       + "/" + productionscript

                shutil.copy('sb_start_temp', sbs_path)
                shutil.copy('sb_prod_temp' , sbp_path)

  # Remove tempfiles.
    os.remove('sb_start_temp')
    os.remove('sb_prod_temp')
    print("\n -done populating directories")

def start_all_jobs():
    """ Function for starting all jobs. """
    mcf = read_master_config_file()
    startscript = mcf["SbatchEquilibrateScript"]
    execute_function_in_job_tree( start_jobs, startscript )
def start_jobs( startscript ):
    """ Function to start equilibrium jobs in a directory"""
    cwd = os.getcwd()
  # check files in directory
    filelist = get_current_file_list( "." )
    if not filelist:
        print(" No files in job directory {}. Have you populated?".format(cwd))
        return

    jobstatus, jobid, jobrun, totalruns = check_if_job_running()

    if jobstatus == "null":
        return
    if  jobstatus == "ready" and jobrun == 0:
        subprocess.Popen(['sbatch', startscript])
        update_local_job_details( "JobStatus",  "submitted" )
        update_local_job_details( "JobMessage", "Submitted to queue" )

    else:
        if jobstatus == "cancelled":
            print(("{}:jobid{} Appears this job was cancelled. Clear pauseflags \
                    before restart. (./mdwf --clear)".format(cwd[-20:], jobid )))
        if "running" in jobstatus:
            print(("{}:jobid: {} --A job appears to be already running here. \
                    ".format(cwd[-20:], jobid)))
        else:
            if jobrun >= 1:
                print(("{}{} Seems equilibration job already run here, don't \
                you want to restart instead? (./mdwf --restart)".format(cwd[-20:], jobid)))

def stop_jobs():
    """ Function to stop all jobs immediately. """
    print("-- stopping all jobs")
    execute_function_in_job_tree(stop_all_jobs_immediately)
def stop_all_jobs_immediately():
    """ Function to stop all jobs immediately """

    jobstatus, jobid, jobrun, totalruns  = check_if_job_running()
    if jobstatus in [ "stopped", "cancelled", "processing" ]:
        update_local_job_details( "JobMessage", "No job running" )
    else:
        print((" Stopping job: {}".format( jobid )))
        message = " scancel jobid: %s" % jobid
        pausejob_flag( "scancel command sent. " )
        update_local_job_details("JobFinishTime", time.time())
        update_local_job_details("JobMessage", "Sent scancel command")
        update_local_job_details("JobStatus", "stopped")
        update_local_job_details("PauseJobFlag", "cancelled")

        subprocess.Popen([ 'scancel', jobid ])
        update_local_job_details( "CurrentJobId",  -1 )

def extend_jobs(a):
    """ Function to change number of job runs. """
    execute_function_in_job_tree(extend_runs,a)
def extend_runs(a):
    """ Function to change number of job runs. """
    ljdf_t  = read_local_job_details( ".", "local_job_details.json" )
    total   = int( ljdf_t[ 'TotalRuns' ] )
    # Update the total of runs.
    newtotal = int( total ) + a
    update_local_job_details( "TotalRuns", newtotal )

def clear_jobs():
    """ Function to clear all pausejob and stop flags """
    mcf = read_master_config_file()
    execute_function_in_job_tree( clear_all_jobs )
def clear_all_jobs():
    """ Function to clear all stop flags in a directory"""
    cwd = os.getcwd()
    jobstatus, jobid, jobrun, totalruns = check_if_job_running()
    if not "running" in jobstatus:
        update_local_job_details( "JobStatus", "ready" )
        update_local_job_details( "CurrentJobId", 0 )
        update_local_job_details( "JobMessage", "Cleared stop flags" )
        update_local_job_details( "PauseJobFlag", 0 )

      # Remove explicit flag file.
        if  os.path.isfile( "pausejob" ):
            os.remove( "pausejob" )
        print(("{} cleared stop flags in: {} {}".format( GREEN, cwd, DEFAULT )))

    else:
        print(("A job appears to be running here:..{} : jobstatus:{}".format( cwd[-20:], jobid )))

def restart_all_production_jobs():
    """ Function to restart_all_production_jobs. """
    print("-- restarting production jobs.")
    mcf = read_master_config_file()
    restart_script = mcf["SbatchProductionScript"]
    execute_function_in_job_tree(restart_jobs, restart_script)
def restart_jobs(restart_script):
    """ Function to restart production jobs. """
    cwd = os.getcwd()
    jobstatus, jobid, jobrun, totalruns = check_if_job_running()
    if jobstatus =="null":
        return
    ljdf_t = read_local_job_details( ".", "local_job_details.json" )
    current   = ljdf_t["CurrentRun"]
    jobid     = ljdf_t["CurrentJobId"]
    total     = ljdf_t["TotalRuns"]
    message   = ljdf_t["JobMessage"]
    pauseflag = ljdf_t["PauseJobFlag"]

    if current >= total:
        print(("{}{}:{} Current run >= to Total runs. Extend runs first.    (./mdwf -e)".format(RED, cwd[-20:],DEFAULT)))
        return

    time.sleep(0.25)
    status1 = ["running", "submitted"]
    status2 = ["cancelled", "stopped"]
    status3 = ["finished", "ready"]

    if jobstatus in status1:
        print(("{}:{}  A job appears to be submitted or running here already.".format(cwd[-20:], jobid)))
        return

    if  jobstatus in status2 or pauseflag=="pausejob":
        print(("{}{}:{} Job is finished or stopped. Clear pauseflags first. (./mdwf --clear)".format(RED, cwd[-20:], DEFAULT)))
        return

    if jobstatus in status3:
        if "Cleared" in message:        # assume restarting from cancelled job.
            pausejob_flag("remove")     # -so we don't increment CurrentRun number
            update_local_job_details("CurrentRun",  (current+1))
            update_local_job_details("JobStatus",  "submitted")
            update_local_job_details("JobMessage", "Production job restarted")
            subprocess.Popen(['sbatch', restart_script])
        return

def recover_all_jobs():
    """ Function to recover and restore crashed jobs. """
    print("Crash recovery: ")
    print("Typically we expect binary output files like .dcd to be the")
    print("same size using this workflow. If a job has crashed we can ")
    print("restore the directory to the last known good point by entering")
    print("the name of the first bad file. Files will be restored to this")
    print("point. ")

    execute_function_in_job_tree( recovery_function )
def recovery_function():
    """ This function checks sizes and md5sums of outputfiles, giving the opportunity
        for a user to recover from the last known good file"""

    ljdf = read_local_job_details( ".", "local_job_details.json" )
    if not ljdf:
        return
    # The following constructs a string to find the "equilibration" dcd file
    # (which is numbered 0, but with zfill padding)

    total = ljdf["TotalRuns"]
    zf = len( str(total) ) + 1 + 4
    zf_bait = ".dcd".zfill( zf )

    FList = get_current_file_list( "OutputFiles" )
    
    DcdList = [item for item in FList if ".dcd" in item]
    #FileList = filter(lambda k: '.dcd' in k, FList)

    line = ljdf["JOB_STREAM_DIR"] + "/" + ljdf["JobDirName"] + "/" +  "OutputFiles:"
    print(("\n{}{}{}".format( GREEN, line, DEFAULT )))
    
    for i in DcdList:
        if "dcd" in i:
            path = 'OutputFiles/' + i
            size = os.path.getsize( path )
            if not zf_bait in i:
                print(("%-24s %12s " % ( i, size )))
            else:
                print(("{}%-24s %12s -equilibration file {} ".format( BLUE, DEFAULT )  % ( i, size )))
    print(("Enter the name of the last {}good file{} or press 'enter' to continue scanning. ('q' to quit)".format(GREEN, DEFAULT )))
    target = input()

    if target == "q":
        sys.exit("exiting" )

    if target != "":
        # find index of target in dirlist.
        if target in DcdList:
            # find index of target in dirlist.
            index = DcdList.index(target)+1
            print(("\n{}Files to delete:{}".format(DEFAULT, DEFAULT )))
            targetlist=[]
            for i in range( index, int(len(DcdList))):
                 print((DcdList[i]))
                 targetlist.append(DcdList[i])

            line = " {}Confirm:{} y/n ".format(YELLOW, DEFAULT )
            confirm = input(line)
            yes = ["Y","y","yes"]
            if confirm in yes:
                line = " {}Really? -this can't be undone! Confirm:{} y/n ".format(YELLOW, DEFAULT )
                confirm = input(line)
                if confirm in yes:
                    print("-deleting redundant output and restart files:")
                    for j in targetlist:
                        targetfile=os.getcwd()+"/OutputFiles/"+j
                        try:
                            os.remove(targetfile)
                        except OSError:
                            pass
                        #slice base name to remove other files:
                        basename = j[ :-4 ]
                        targetfile=os.getcwd()+"/OutputText/" + basename + ".txt"

                        try:
                            os.remove(targetfile)
                        except OSError:
                            pass

                        for k in ['.vel', '.coor', '.xsc', '.xst']:
                            targetfile=os.getcwd()+"/RestartFiles/" + basename + k
                            try:
                                os.remove(targetfile)
                            except OSError:
                                pass

                    # slice job number and basename from dcd job name:
                    num = int( target[-zf:-4] )
                    basename = target[ :-4 ]
                    print("-updating restart files:")
                    for k in ['.vel', '.coor', '.xsc', '.xst']:
                        src=os.getcwd()+"/RestartFiles/" + basename + k
                        dst=os.getcwd()+"/current_MD_run_files" + k
                        print(("copy /RestatFiles/{}{} to current_MD_run_files{}".format(basename, k, k)))
                        shutil.copyfile(src, dst)

                    print("-updating run number:")
                    update_local_job_details( "CurrentRun", num )

        else:
            print((target, " not found: "))

def pause_jobs():
    """ Function to stop all jobs gently, ie) at end of current run."""
    print("-- pausing all jobs")
    execute_function_in_job_tree(pause_all_jobs)
def pause_all_jobs():
    """ Adds pause job in directory. """
    jobstatus, jobid, jobrun, totalruns  = check_if_job_running()
    status4 = ["stopped", "cancelled", "processing"]
    if jobstatus in ["stopped", "cancelled", "processing"]:
        update_local_job_details("JobMessage", "No job running")
    else:
        pausejob_flag("Manual pausing of job.")
        update_local_job_details("JobMessage", "Pausejob request sent")

def gather_jobs():
    """ Function to create a convenient vmd input file to load and view trajectory data. """
    global dcdlist
  # Write basic model loader.
    mcf = read_master_config_file()
    psf   = mcf["PsfFileName"]
    pdb   = mcf["PdbFileName"]
    cwd = os.getcwd()
    with open("Analysis/model_loader.vmd", "w+") as mfile:
        mfile.write("# Basic vmd model loader \n")
        mfile.write("mol new     " + cwd + "/InputFiles/" + psf
              + " type psf first 0 last -1 step 1 filebonds 1 autobonds 1 waitfor all\n")
        mfile.write("mol addfile " + cwd + "/InputFiles/" + pdb
              + " type pdb first 0 last -1 step 1 filebonds 1 autobonds 1 waitfor all\n")
        mfile.close()

    with open("Analysis/dcd_trajectory_fileloader.vmd", "w+") as dcdlist:
        execute_function_in_job_tree(gather_list)
        dcdlist.close()
def gather_list():
    """function to create list of output files from OutputFiles folder"""
  # List dcd files in /OutputFiles folder
    cwd = os.getcwd()
    line = "# " + cwd + "\n"
    dcdlist.write(line)

    f_list = get_current_file_list("OutputFiles")
  # For creating vmd dcd fileloader
    head = "mol addfile "
    tail = " type dcd first 0 last -1 step 1 filebonds 1 autobonds 1 waitfor all\n"
    for l in f_list:
        if ".dcd" in l:
            dcdline = head + cwd + "/OutputFiles/" + l + tail
            dcdlist.write(dcdline)

def erase_all_data():
    """ Function to erase all data for a clean start. Use with caution!"""

    JobStreams, Replicates, BaseDirNames, JobBaseNames, Runs, \
                nJobStreams, nReplicates, nBaseNames = check_job_structure()

    cwd = os.getcwd()
    print("\nWe are about to erase all data in this directory, which can be useful")
    print("for making a clean start, but disasterous if this is the wrong folder!")
    print(("{}Proceed with caution!{}".format(RED, DEFAULT)))
    print("This operation will delete all data in the folders:\n")
    print(("/{}                              ".format(JobStreams,DEFAULT)))
    print("/Setup_and_Config/Benchmarking/  - Benchmarking data.")

    strg = input("\n Press enter to quit or type: '{}erase all my data{}': ".format(YELLOW, DEFAULT))
    print (strg)

    if strg in ['erase all my data']:
        print("Ok, well if you say so....")

        for j in range( 0, nJobStreams):
            TargetDir = cwd + "/" + JobStreams[j]
            print((" Erasing all files in:{}".format(TargetDir)))
            if os.path.isdir(  TargetDir ):
                shutil.rmtree( TargetDir )
            else:
                print((" Couldn't see {}".format(TargetDir)))
        # cleanup benchmark files:
        benchmark_delete = ["current_MD_run_files.*", "slurm*", "bm_config.*" ,"FFTW_*", "temp_working_errors", "bm_input.*"]
        for j in benchmark_delete:
            filetarget = cwd + "/Setup_and_Config/Benchmarking/" + j
            p = glob(filetarget)
            for m in p:
                os.remove(m)

        print("\nOh the humanity. I sure hope that wasn't anything important.")
    else:
        print("Phew! Nothing erased.")

def cleanup_job_runs():
    """ Cleans up folder. Updates local details. """
    update_local_job_details( "JobStatus",  "Finished" )
    update_local_job_details( "JobMessage", "Finished production runs" )
    update_local_job_details( "PauseJobFlag", "pausejob" )
    update_local_job_details( "CurrentJobId", -1 )
    pausejob_flag( "Job runs finished." )
    final_job_cleanup()

## Helper Functions:
## Checking Functions:
def execute_function_in_job_tree( func, *args ):
    """ Function to execute a given function throughout the entire job tree. """

    cwd = os.getcwd()
  # Read job structure tree as given in the "master_config_file":
    JobStreams, Replicates, BaseDirNames, JobBaseNames, Runs, \
                nJobStreams, nReplicates, nBaseNames = check_job_structure()

  # Descending into job tree:
    for i in range( 0, nJobStreams ):
        CurrentJobStream = cwd + '/' + JobStreams[i]

  # Descending into job directory tree of each JobStream
        if os.path.isdir( CurrentJobStream ):
            JobStreamDirList = get_current_dir_list( CurrentJobStream )

            for j in JobStreamDirList:
                CurrentJobDir = CurrentJobStream + '/' + j
                if os.path.isdir(CurrentJobDir):
                    os.chdir( CurrentJobDir )
                    func( *args )
                else:
                    print(("\nCan't descend into job directory tree. Have you populated?\n {}"\
                           .format(CurrentJobDir)))
        else:
            print(("Can't see job directories {}   -Have you initialized?"\
                           .format(CurrentJobStream)))
    os.chdir(cwd)

### Checking functions:
def check_pausejob_flag():
    """ A simple check for the pausejob flag in local details file.
        Creates and actual pauseflag file in the directory if present. """

    ljdf_t  = read_local_job_details( ".", "local_job_details.json" )
    pause = ljdf_t["PauseJobFlag"]

    if pause != 0:
        f = open( "pausejob", 'a' )
        f.write(" pauseflag already present in local_jobs_detail file. ")
        f.close()
        update_local_job_details( "JobStatus",  "pausejob" )
        update_local_job_details( "JobMessage", "paused" )
def check_disk_quota():
    """ Obselete function. """
    return
def check_job_runtime():
    """ Check for job failure based on run time. This function assumes
        that if a job completes too soon, it has probably failed.
        If the run time is less than a certain cutoff defined in the
        'master_config_file' it will create a pausejob flag.  """

    ljdf_t = read_local_job_details( ".", "local_job_details.json" )
    start  = int( ljdf_t[ 'JobStartTime'  ] )
    finish = int( ljdf_t[ 'JobFinishTime' ] )
    limit  = int( ljdf_t[ 'JobFailTime'   ] )
    runtime = finish - start

    if runtime < limit:
        update_local_job_details( "JobStatus",  "stopped" )
        update_local_job_details( "JobMessage", "Short run time detected" )
        pausejob_flag( "Short runtime detected - job fail??" )
def check_if_job_running():
    """ Function to check if job already running in current working directory """
    dir_path = os.getcwd()
    ljdf_t = read_local_job_details( dir_path, "local_job_details.json" )
    if not ljdf_t:
        return "null","null","null","null"
    current_jobid  = str( ljdf_t["CurrentJobId"] )
    current_jobstatus = ljdf_t["JobStatus"]
    current_run = ljdf_t["CurrentRun"]
    total_runs =  ljdf_t["TotalRuns"]
    return current_jobstatus, current_jobid, current_run, total_runs
def check_run_counter(processing="post"):
    """ Function to checks the run counter. Creates pause if total job run
        value exceeded. Increments job run counter as necessary """
  # read current state:
    ljdf_t     = read_local_job_details( ".", "local_job_details.json" )
    currentrun = int( ljdf_t['CurrentRun'] )
    totalruns  = int( ljdf_t['TotalRuns'] )
    jobid      = ljdf_t['CurrentJobId' ]
  # check to stop jobs if current run greater than total runs.
    if currentrun > totalruns:
        cleanup_job_runs()
        return
  # increment job number
    if (processing =="post"):
        newrun = int(currentrun) + 1
        update_local_job_details( "LastJobId",  jobid )
        if newrun > totalruns:
            cleanup_job_runs()
            return
        update_local_job_details( "CurrentRun", newrun )
def check_job_structure():
    """ Function to check job structure in 'master_config_file'
        The job structure has three tiers, JobStreams (we usually
        only have 1), job replicates in the stream, and number
        of job runs to perform in each replicate. """

    mcf = read_master_config_file()
    JobStreams   = mcf["JobStreams"]
    Replicates   = mcf["JobReplicates"]
    BaseDirNames = mcf["BaseDirNames"]
    JobBaseNames = mcf["JobBaseNames"]
    Runs         = mcf["Runs"]

  # Check that job details lists are the same length in master_config_file:
    nJobStreams   = int( len( JobStreams ))
    nReplicates   = int( len( Replicates ))
    nBaseNames    = int( len( BaseDirNames ))
    nJobBaseNames = int( len( JobBaseNames ))
    nRuns         = int( len( Runs ))
    if not nJobStreams==nReplicates==nBaseNames==nJobBaseNames==nRuns:
        print("Job Details Section lists do not appear to be the same length\
               in master_config_file.")
        sys.exit()
    return JobStreams, Replicates, BaseDirNames, JobBaseNames, Runs,\
           nJobStreams, nReplicates, nBaseNames
def check_job():
    """ Function to check the input of the current job and calculate
        resources required. """

    mcf = read_master_config_file()
    jd_opt,  jd_opt_pl  = read_namd_job_details(mcf["EquilibrateConfScript"])
    jd_prod, jd_prod_pl = read_namd_job_details(mcf["ProductionConfScript"])

  # Checking if files in configuration exist where they are supposed to be.
    print(("{}--------------------------------------------------------------------------------".format(BLUE)))
    print(("{}Checking configuration input files:{}".format(YELLOW, DEFAULT)))
    print(("{}--------------------------------------------------------------------------------".format( BLUE)))
    print(("{}{}:{}".format(BLUE,mcf["EquilibrateConfScript"],DEFAULT)))
    check_file_exists(jd_opt["psffilepath"])
    check_file_exists(jd_opt["pdbfilepath"])
    for i in jd_opt_pl:
        check_file_exists(i)

    print(("{}{}:{}".format(BLUE,mcf["ProductionConfScript"],DEFAULT)))
    check_file_exists(jd_prod["psffilepath"])
    check_file_exists(jd_prod["pdbfilepath"])
    for i in jd_prod_pl:
        check_file_exists(i)

    sr = 0             # Initalise no. of job repliates
    run = 0            # Initalise no. of runs in each replicate

    print(("{}------------------------------------------------------------------------------".format(BLUE)))
    print(("{}Node configuration:{}".format(YELLOW, DEFAULT)))
    print(("{}------------------------------------------------------------------------------".format(BLUE)))
    print(("{}Sbatch Scripts:     {} %s , %s  ".format(RED, DEFAULT) % \
           (mcf["SbatchEquilibrateScript"], mcf["SbatchProductionScript"])))
    print(("{}Nodes:              {} %-12s    ".format(RED, DEFAULT) % (mcf["Nodes"])))
    print(("{}Walltime:           {} %-12s    ".format(RED, DEFAULT) % (mcf["Walltime"])))
    if not mcf["Account"] == "VR0000":
        print(("{}Account:            {} %-12s    ".format(RED, DEFAULT) % (mcf["Account"])))
    else:
        print(("{}Account:               %-12s  -have you set your account?{} "\
          .format(RED, DEFAULT) % (mcf["Account"])))

    print(("\n{}--------------------------------------------------------------------------------".format(BLUE)))
    print(("{}Job check summary: ".format(YELLOW, DEFAULT)))
    print(("{}--------------------------------------------------------------------------------".format(BLUE)))
    print(("{} Main Job Directory:        {}{}".format(RED, DEFAULT,          mcf["JobStreams"])))
    print(("{} Simulation basename:       {}{}".format(RED, DEFAULT,          mcf["BaseDirNames"])))
    print(("{} Sbatch start template:     {}{}.template".format(RED, DEFAULT, mcf["SbatchEquilibrateScript"])))
    print(("{} Sbatch prouction template: {}{}.template".format(RED, DEFAULT, mcf["SbatchProductionScript"])))
    print(("{} Optimization script:       {}{}".format(RED, DEFAULT,          mcf["EquilibrateConfScript"])))
    print(("{} Production script:         {}{}".format(RED, DEFAULT,          mcf["ProductionConfScript"])))
    print(("{} Module file:               {}{}".format(RED, DEFAULT,          mcf["ModuleFile"])))

    Replicates   = mcf["JobReplicates"]
    Runs         = mcf["Runs"]
    nReplicates  = int(len(Replicates))
    nRuns        = int(len(Runs))

  # Calculating variables from input files:
    for i in range(0, nReplicates):
        sr += int(Replicates[i])                         # total no. of job replicate
    for j in range(0, nRuns):
        run += int(Runs[j])                              # total no. of runs in each replicate

    spr = jd_prod["steps"]                             # steps per run
    dcd = jd_prod["dcdfreq"]                           # dcd write frequency
    dfs = int(jd_prod["natom"])*12.0/(1024.0*1024.0)   # dcd frame size (based on number of atoms from psf)
    tdf = int(spr)/int(dcd)*int(run)*int(sr)             # total dcd frames
    dfs = int(jd_prod["natom"])*12.0/(1024.0*1024.0)   # dcd frame size (based on number of atoms from psf)
    tdf = int(spr)/int(dcd)*int(run)*int(sr)             # total dcd frames
    tpd = tdf*dfs/(1024)                                 # total production data
    tst = (int(sr)*int(run)*int(jd_prod["timestep"])*int(spr))/1000000.0  # total simulated time

    print(("{}--------------------------------------------------------------------------------".format(BLUE)))
    print(("{}Estimation of data to be generated from the production run of this simulation:{}".format(YELLOW, DEFAULT)))
    print(("{}--------------------------------------------------------------------------------".format(BLUE)))
    print(("{} Simulation directories:   {}%-8s      {}Runs per directory:   {}%-8s"\
              .format(BLUE, DEFAULT, BLUE, DEFAULT) % (sr, run)))
    print(("{} Steps per run:            {}%-8s      {}Dcdfreq in run:       {}%-8s"\
              .format(BLUE, DEFAULT, BLUE, DEFAULT) % (spr, dcd)))
    print(("{} Dcd frame size(MB)        {}%-8.3f      {}Total dcd frames:     {}%-8s"\
              .format(BLUE, DEFAULT, BLUE, DEFAULT) % (dfs, tdf)))
    print(("\n {} Total simulated time:{}  %12.2f nanoseconds"\
              .format(GREEN, DEFAULT) %(tst)))

    if not (tpd==0):
        print((" {} Total production data:{} %12.2f GB"\
                     .format(GREEN, DEFAULT) %(tpd)))
    else:
        print((" {}   Total production data:{} %12.2f {}GB - error in calculating \
                frame size. No psf file?".format(RED, DEFAULT, RED) %(tpd)))
    print(("{}--------------------------------------------------------------------------------{}".format(BLUE,DEFAULT)))
def check_file_exists(target):
    """ Check file exists, give appropriate message. """
    mesg1 = "{} found {} -ok{}".format(DEFAULT, GREEN, DEFAULT)
    mesg2 = "{} found {} -ok{} -example file?".format(DEFAULT, GREEN, DEFAULT)
    mesg3 = "{} not found.{} -Check config file.{}".format(DEFAULT, RED, DEFAULT)

    ntarget = target[6:]        # strip off "../../"
    if not "../../" in target[0:6]:
        print(("{}unexpected path structure to input files:{}".format(RED, DEFAULT)))

    if os.path.exists(ntarget):
        if "example" in target:
            print(("{} %-50s {}".format(RED, mesg2) %(ntarget)))
        else:
            print(("{} %-50s {}".format(RED, mesg1) %(ntarget)))
    else:
        print(("{} %-46s {}".format(RED, mesg3) %(ntarget)))

### Get info functions
def get_atoms(psffile):
    """ Function to estimate dcd frame size of simulation based on
        the numbers of atoms. Assumes the psf file is in
        /InputFiles directory.  Returns the number of atoms. """

    target=os.getcwd() + "/InputFiles/" + psffile
    atoms = 0
    if os.path.isfile(target):
        f = open(target,'r')
        for line in f:
            if 'NATOM' in line:
                nl = line.split( )
                atoms = nl[0]
        f.close()
        return atoms
    else:
        print(("{}Can't find {} in /InputFiles directory {}"\
               .format(RED,psffile,DEFAULT)))
def get_job_runtime( starttime, status ):
    """ Function to return runtime of current job in H:M format.
        Returns --:-- if job not running. """
    if "running" in status:
        seconds = int( time.time() - starttime )
        m, s = divmod( seconds, 60 )
        hours, min = divmod( m, 60 )
        Time = "%d:%02d" % ( hours, min)
    else:
        Time = "--:--"
    return Time
def get_current_dir_list(job_dir):
    """ Function to return a list of sorted directories in a given path. """

    if not os.path.isdir(job_dir):
        print("No directories {} found. Have you initialized? \n".format(job_dir))
        return
    dir_list=[f for f in os.listdir(job_dir) if os.path.isdir(os.path.join(job_dir, f))]
    if not dir_list:
        print("No directories found in {}. Have you initialized? \n".format(job_dir))
    return sorted(dir_list)
def get_current_file_list(job_dir):
    """ Function to return a list of files in a given path. """

    if not os.path.isdir(job_dir):
        print("No directory {} found. Have you initialized? \n".format(job_dir))
        return
    file_list=[f for f in os.listdir(job_dir) if os.path.isfile(os.path.join(job_dir, f))]
    if not file_list:
        return
    return sorted(file_list)
def get_file_size( filename ):
    """ Function to get file size. """
    size = os.path.getsize(filename)
    return size

def log_job_details( jobid ):
    """ Simple function to update 'local_job_details' from "scontrol show job" details. """

    jobdetails = subprocess.check_output(["scontrol", "show", "job", str(jobid) ] )
    jdsplit = re.split( ' |\n', jobdetails )
    for i in jdsplit:
        if "JobState=" in i:
            update_locate_job_details( "JobStatus",  i.split("=")[1] )
        if "NumNodes=" in i:
            update_locate_job_details( "Nodes",  i.split("=")[1] )
        if "NumCPUs=" in i:
            update_locate_job_details( "Cores",  i.split("=")[1] )
        if "StartTime=" in i:
            update_locate_job_details( "JobStartTime",  i.split("=")[1] )
        if "TimeLimit=" in i:
            update_locate_job_details( "Walltime",  i.split("=")[1] )
def md5sum( filename, blocksize=65536 ):
    """ Function to return md5 checksum. """
    hash = hashlib.md5()
    with open(filename, "r+b") as f:
        for block in iter(lambda: f.read(blocksize), ""):
            hash.update(block)
        f.close()
    return hash.hexdigest()
def pausejob_flag( directive ):
    """ Creates or removes pausejob flag. Pausejob are small text files
        as an extra precaution for job control.
        Their presence in the directory stops jobs launching. """

    if directive == "remove":
        update_local_job_details( "PauseJobFlag", 0 )
        if os.path.isfile( "pausejob" ):
            os.remove( "pausejob" )
    else:
        update_local_job_details( "PauseJobFlag", "pausejob" )
        f = open("pausejob", 'a')
        f.write(directive)
        f.close()
def create_job_basename( jobname, run, zf ):
    """ Creates a time stamped basename for current job, uses zfill for
        numbering convention. """
    timestamp = time.strftime( "%Y_%d%b_", time.localtime() )
    basename  = timestamp + jobname + "run_" + str( run ).zfill( zf )
    return basename
def update_local_job_details( key, status ):
    """ Updates local job details of 'local job details file'. """
    ljdf_t = read_local_job_details(".", "local_job_details.json")
    ljdf_t[ key ] = status
    with open("local_job_details.json", 'w') as outfile:
        json.dump(ljdf_t, outfile, indent=2)
    outfile.close()
def redirect_namd_output( CurrentWorkingName = "current_MD_run_files",
                          jobtype = "production"):
    """ Function to redirect NAMD output to appropriate folders."""
    ljdf_t = read_local_job_details( ".", "local_job_details.json" )
    jobname = ljdf_t[ 'JobBaseName' ]
    run     = ljdf_t[ 'CurrentRun' ]
    total   = ljdf_t[ 'TotalRuns' ]
    zfill   = len( str( total ) ) + 1
    basename = create_job_basename( jobname, run, zfill )

  # Make shorthand of current working files
    cwf_coor = CurrentWorkingName + ".coor"
    cwf_vel  = CurrentWorkingName + ".vel"
    cwf_xsc  = CurrentWorkingName + ".xsc"
    cwf_xst  = CurrentWorkingName + ".xst"
    cwf_dcd  = CurrentWorkingName + ".dcd"

  # Check that restartfiles actually exisit, if not create pausejob condition.
    if not os.path.isfile(cwf_coor) or not os.path.isfile(cwf_vel) \
            or not os.path.isfile(cwf_xsc):
        pausejob_flag( "Missing input files." )
        update_local_job_details( "JobStatus", "stopping" )
        update_local_job_details( "JobMessage", "No namd outputfiles generated" )

  # Copy CurrentWorking (restart) files to LastRestart/ directory
    shutil.copy(cwf_coor, 'LastRestart/' + cwf_coor)
    shutil.copy(cwf_vel,  'LastRestart/' + cwf_vel)
    shutil.copy(cwf_xsc,  'LastRestart/' + cwf_xsc)

  # Rename and move current working files
    os.rename( cwf_dcd,    "OutputFiles/"  + basename + ".dcd"  )
    shutil.copy( cwf_vel,  "RestartFiles/" + basename + ".vel"  )
    shutil.copy( cwf_xsc,  "RestartFiles/" + basename + ".xsc"  )
    shutil.copy( cwf_xst,  "RestartFiles/" + basename + ".xst"  )
    shutil.copy( cwf_coor, "RestartFiles/" + basename + ".coor" )
    shutil.move( "temp_working_outputfile.out", "OutputText/" + basename + ".txt" )
    shutil.move( "temp_working_errorsfile.err", "Errors/"     + basename + ".err" )
def post_jobrun_cleanup():
    """ Remove unwanted error, backup files, etc. """
    for file in glob("slurm*"):
        shutil.move(file, "JobLog/" )
    for file in glob("core*"):
        shutil.move(file, "Errors/")
    for file in glob("*.restart.*"):
        shutil.move(file, "LastRestart/")

    # reset timer / jobid flags:
    update_local_job_details( "JobStartTime", 0 )
    update_local_job_details( "JobFinishTime", 0 )
    update_local_job_details( "CurrentJobId", 0 )

    # update dcd files list:
    update_local_dcd_list()


def update_local_dcd_list():
    """ Function to create a local dcd_files_list.vmd use to load data into VMD. """
    f = open('local_dcd_files_loader.vmd', 'w')
    cwd = os.getcwd()

    f.write("set firstframe 1 \n")
    f.write("set lastframe -1 \n")
    f.write("set stepsize  1 \n\n")
    f.write("set cwd " + cwd + "\n\n")
    dcdlist = glob( "OutputFiles/*.dcd" )
    for i in dcdlist:
        line = " mol addfile %s%s type dcd first %s last %s step %s filebonds 1 autobonds 1 waitfor all\n"\
                % ( "$cwd/", i, "$firstframe", "$lastframe", "$stepsize")
        f.write( line )
    f.close()
def final_job_cleanup():
    """ Perform final cleanup once jobs are finished. """
    for file in glob("*BAK"):
        os.remove( file )
    for file in glob("*.old"):
        os.remove( file )
    for file in glob("*.restart.*"):
        os.remove( file )
    for file in glob("*.xst"):
        os.remove( file )

def log_job_timing():
    """ Log length of job in human readable format. """


## still to do
def countdown_timer():
    """ Function to adjust countdown timer """
def benchmark():
    """ Function to benchmark job """
    mcf = read_master_config_file()
    jd_opt, jd_opt_pl = read_namd_job_details(mcf["EquilibrateConfScript"])
    print(("{} Setting up jobs for benchmarking based on current job config files.".format(DEFAULT)))
def create_dcd_file_loader( first = 0, last = -1, step =1):
    """ Function to create an easyfile loader to be able to read in a
        contiguous series of dcd output files for VMD. """

    cwd = os.getcwd()
    OutputDir = cwd + "/" "OutputFiles"
    DirList = get_current_dir_list( OutputDir )

  # Create vmd line:
    line = "mol addfile %s type dcd first %s last %s step %s filebonds 1 autobonds 1 waitfor all\n"\
            .format( dcdline, first, last, step )
def clone():
    """ Function to clone directory without data, but preserving input files. """
    print("-- cloning data directory. Not implimented yet.")
