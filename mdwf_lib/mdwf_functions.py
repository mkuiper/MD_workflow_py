#!/usr/bin/env python
# MD workflow functions.   mdwf 
""" mdwf functions.                    version 0.1
    Most of the mwdf functions are maintained here
"""

import os
import sys 
from collections import OrderedDict
import json
import shutil
import fileinput
import hashlib
import time 
import datetime
import glob
import re

#
#
# ansi color variables for formatting purposes: 

c0 = '\033[0m'        # default
cc1= '\033[2m'        # grey 
c1 = '\033[31;2m'     # dark red 
c2 = '\033[32;1m'     # light green
c3 = '\033[32;2m'     # dark green
c4 = '\033[33;1m'     # light yellow
c5 = '\033[38;5;154m' # spring green
c6 = '\033[34;1m'     # light blue
c7 = '\033[34;2m'     # dark blue
c8 = '\033[38;5;220m' # orange 
c9 = '\033[36;1m'     # cyan

def read_master_config_file():  
    """ Reads parameters from json file: master_config_file """  
    cwd=os.getcwd()
    if os.path.isfile('master_config_file'):
        master_json = open('master_config_file')
        try: 
            mcf = json.load(master_json,object_pairs_hook=OrderedDict)
            master_json.close()
        except:
            print "\n{}Possible json format errors of {}'master_config_file'{}\n".format(c3,c3,c0)
    else:
        print "{}Can't see {}'master_config_file'{} in directory:{} {}\n".format(c3,c4,c3,cwd,c0) 
        sys.exit()
    return mcf
        

def read_local_job_details_file(path="Setup_and_Config",ljdf_target="job_details_template.json"):  
    """ Reads parameters from json file: Setup_and_Config/job_details_template.json """  

    target=os.getcwd() + "/" + path + "/" + ljdf_target
    if os.path.isfile(target):
        local_json = open(target)
        try: 
            ljdf = json.load(local_json,object_pairs_hook=OrderedDict)
            local_json.close()
        except:
            print "\n{}Possible json format errors of {}'master_config_file'{}\n".format(c3,c3,c0)
    else:
        error = "\nCan't see '{}' in directory:{}/{}/ ".format(ljdf_target,os.getcwd(),path) 
        sys.exit(error)
    return ljdf


def read_job_details(targetfile):
    """ Extracts simulation details from given namd config file and returns a dictionary. """
#   assumes files are located in /Setup_and_Config 
    target=os.getcwd() + "/Setup_and_Config/" + targetfile
#   job-details dictionary:
    jdd = {}        
    jdpl = []     # job details parameter list. 
    if os.path.isfile(target):
        f = open(target,'r')
        for lline in f:
            line = lline[0:18]          # strip line to avoid artifacts
            if not "#" in line[0:2]:    # leave out commented lines
                if 'structure ' in line:
                    pl = lline.split()
                    jdd["psffilepath"] = pl[1]
                    nl = re.split(('\s+|/|'),lline)
                    for i in nl:
                        if '.psf' in i:
                            jdd["psffile"] = i
                            natom = estimate_dcd_frame_size(i)        
                            jdd["natom"] = natom
                if 'coordinates ' in line:
                    pl = lline.split()
                    jdd["pdbfilepath"] = pl[1]
                    nl = re.split(('\s+|/|'),lline)
                    for i in nl:
                        if '.pdb' in i:
                            jdd["pdbfile"] = i
                if 'timestep ' in line:
                    nl = lline.split()
                    jdd["timestep"] = nl[1]
                if 'NumberSteps ' in line:
                    nl = lline.split()
                    jdd["steps"] = nl[2]
                if 'dcdfreq ' in line:
                    nl = lline.split()
                    jdd["dcdfreq"] = nl[1]
                if 'run ' in line:
                    nl = lline.split()
                    jdd["runsteps"] = nl[1]
                if 'restartfreq ' in line:
                    nl = lline.split()
                    jdd["restartfreq"] = nl[1]
                if 'parameters ' in line:
                    nl = lline.split()
                    jdpl.append(nl[1])
        f.close()
    else: 
        print "{}{} file not found".format(c5,targetfile)
    return jdd, jdpl

    
def estimate_dcd_frame_size(psffile):
    """ function to estimate dcd frame size of simulation based on the numbers of atoms. """
#   assumes psf file is in /InputFiles directory. 
    target=os.getcwd() + "/InputFiles/" + psffile
    atoms = 0 
    if os.path.isfile(target):
        f = open(target,'r')
        for line in f:
            if 'NATOM' in line:     # extract number of atoms from !NATOM line
                nl = line.split()
                atoms = nl[0]
    else:
        print "{}Can't find {}{}{} in /InputFiles directory".format(c3,c4,psffile,c0)
    f.close()    
    return atoms


def check_for_pausejob():
    """checks for pausejob flag in local job details file"""
    if os.path.isfile("pausejob"):
        error = "\npausejob flag present. Stopping job.\n" 
        status = "Stopped: Pausejob flag present"
        update_local_job_status(status)
        sys.exit(error)
    return


def initialize_job_countdown(equilib = "single"):
    """intializes rounds and countdown timers of local details file based on master_config_file"""
    # equilib represents equilibration strategy:
    # "single" for one equilibration that is then passed to all other job directories. 
    # or "multiple" for each job directory starting its own unique equilibration phase.
    return
        

def check_disk_quota():
    """ function for checking that there is enough diskspace on the system before starting job"""
    return


def log_job_details(jobid):
    """logging cluster job details"""
    return


def record_start_time():
    """ to log start time in unix time to local details"""
    starttime = int(time.time())
    try:
        ljdf["JobStartTime"] = starttime
    except:
        print "\ncan't write start time to local job detail file.\n"
    return 


def record_finish_time():
    """ to log start time in unix time to local details"""
    finishtime = int(time.time())
    try:
        ljdf["JobFinishTime"] = finishtime
    except:
        print "\ncan't write finish time to local job detail file.\n"
    return 


def check_job_fail():
    """ check for job failure """
    sta = ljdf["JobStartTime"]
    fin = ljdf["JobFinishTime"]
    cutoff = mcf["JobFailTime"]
    runtime = fin - sta
    if runtime < cutoff: 
        error = "Job ran shorter than expected. Possible crash." 
        status = "Short run time: crash? Stopped Job"
        update_local_job_status(status)
        sys.exit(error) 
    return 


def log_job_timing():
    """ log length of job in human readable format """
    return


def create_job_basename():
    """ creates a time stamped basename for current job"""
    ts = time.time()
    stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y_%h_%d_%H%S_')
    basename = stamp + ljdf["JobBaseName"] + "_r_" + ljdf["CurrentJobRound"]
    return basename 


def update_local_job_status(status):
    """ updates local job status """

    ljdf["JobStatus"] = status
    return 


def redirect_optimization_output():
    """ move output of optimization phase in all the right places."""
    return


def redirect_production_output():
    """ move output of production_runs to all the right places."""
    return


def countdown_timer():
    """ function to adjust countdown timer """


def check_if_job_running(JobDir,sim):
    """ function to check if job already running in directory """ 
    dir_path = JobDir + "/" + sim
    ljdf_t = read_local_job_details_file(dir_path, "local_job_details.json") 
    cjid = ljdf_t["CurrentJobId"]
    

def monitor_jobs():
    """ -function to monitor jobs status on the cluster """ 
    mcf = read_master_config_file()
    JobDir  = mcf["JobDir"]
    Account = mcf["Account"]

    jobdirlist = get_current_joblist(JobDir)
    
    print "JobDirName:   |Progress: |JobId:    |Status:   |Cores:  |Walltime: |Job_messages:"
    print "--------------|----------|----------|----------|--------|----------|------------------ "

    for i in jobdirlist: 
        dir_path = JobDir + "/" + i  
        ljdf_t = read_local_job_details_file(dir_path, "local_job_details.json") 
        jdn  = ljdf_t["JobDirName"]
        qs   = ljdf_t["QueueStatus"]
        js   = ljdf_t["JobStatus"]
        cores= ljdf_t["Cores"]
        wt   = ljdf_t["WallTime"]
        cjid = str(ljdf_t["CurrentJobId"])
        prog = str(ljdf_t["CurrentJobRound"] + ": " + ljdf_t["RunCountDown"] + "/" + ljdf_t["TotalRuns"]) 


        print "{}%-16s {}%8s {}%10s {}%10s {}%8s {}%10s {}%s".format(c1,c2,c3,c4,c5,c6,c7) % (jdn[0:11],prog,cjid,qs[0:10],cores,wt,js) 




def md5sum(filename, blocksize=65536):
    """function for returning md5 checksum"""
    hash = hashlib.md5()
    with open(filename, "r+b") as f:
        for block in iter(lambda: f.read(blocksize), ""):
            hash.update(block)
        f.close()
    return hash.hexdigest()


def getfilesize(filename):
    size = os.path.getsize(filename)
    return size


def initialize_job_directories():
    """ -function to setup job directories """
    mcf = read_master_config_file()
    try:
        JobDir      = mcf["JobDir"]
        Sims    = int(mcf["SimReplicates"]) 
        BaseDirName = mcf["BaseDirName"]     
    except: 
        sys.exit("\nError reading master_config_file variables.\n")

    cwd=os.getcwd()
    TargetJobDir = cwd + "/" +JobDir
    if not os.path.exists(TargetJobDir):
        print "{} Job directory /{} does not exist. Making new directory.{}".format(c3,JobDir,c0)
        try:
            os.makedirs(JobDir)
        except:
            error = "\n{}Error making directory in /{}.{}".format(c3,cwd,c0)
            sys.exit(error) 

    # Copy directory structure from /Setup_and Config/JobTemplate
    print "{}Making Job directory replicates in /{}\n".format(c0,JobDir)

    TemplatePath = cwd + "/Setup_and_Config/JobTemplate"
    # check existance of JobTemplate directory:
    if not os.path.exists(TemplatePath):
        print "\n{} Can't see /Setup_and_Config/JobTemplate. exiting.{}".format(c4,c0)
        sys.exit() 
    
    zf = len(str(Sims)) + 1    
    for i in range(1,Sims+1):
        suffix = str(i).zfill(zf)
        NewDirName = JobDir + "/" + BaseDirName + suffix          
        if os.path.exists(NewDirName):
            print "{}Directory {} already exists! -Skipping.{}".format(c5,NewDirName,c0) 
        else:
            try: 
                shutil.copytree(TemplatePath, NewDirName)
                print "{}Creating:{}{}".format(c5,c0,NewDirName)             
            except: 
                print "{}Error in copying directories.{}".format(c4,c0)
    print c0


def populate_job_directories():
    """ -function to populate or update job directories with job scripts """

# reading information from master_config_file and local job details template
    ljdf_t = read_local_job_details_file()
    mcf    = read_master_config_file()

    try:
        JobDir      = mcf["JobDir"]
        Sims        = int(mcf["SimReplicates"])
        BaseDirName = mcf["BaseDirName"]
        Runs        = mcf["Runs"]
        Round       = mcf["Round"]
        JobBaseName = mcf["JobBaseName"]
        Account     = mcf["Account"]
        Nodes       = mcf["nodes"]
        Ntpn        = mcf["ntpn"]
        Ppn         = mcf["ppn"]
        OptScript   = mcf["OptimizeConfScript"]
        ProdScript  = mcf["ProdConfScript"]
        ModuleFile  = mcf["ModuleFile"]
        Walltime    = mcf["Walltime"]
        sbstart     = mcf["SbatchStartScript"]
        sbprod      = mcf["SbatchProdScript"]

    except:
        print "\n{}Error reading master_config_file variables.{}\n".format(c4,c0)
        sys.exit()

    cwd=os.getcwd()
    TargetJobDir = cwd + "/" +JobDir
    
# create staging file from ljdf_template
    stagef = ljdf_t           

# modify elements in staging dictionary file:
    stagef['TOP_DIR']      = cwd
    stagef['CurrentRound'] = Round
    stagef['TotalRuns']    = Runs
    stagef['JobBaseName']  = JobBaseName

# check to see if there actually are any job directories to fill:
    jobdirlist = get_current_joblist(JobDir)
    if not jobdirlist: 
        print "{}No job directories found in {}/{}.{} Have you initialized?".format(c4,cc1,JobDir,c0)

# create and modify temporary sbatch scripts:
    sb_start_template = "Setup_and_Config/" + sbstart + ".template"
    if not os.path.exists(sb_start_template):
        print "{}Can't find {}{}{}.".format(c4,c3,sb_start_template,c0)
        sys.exit()
    sb_prod_template = "Setup_and_Config/" + sbprod + ".template"
    if not os.path.exists(sb_prod_template):
        print "{}Can't find {}{}{}.".format(c4,c3,sb_prod_template,c0)
        sys.exit()
  # new lines:
    nnodes   = "#SBATCH --nodes="   + Nodes
    ntime    = "#SBATCH --time="    + Walltime
    naccount = "#SBATCH --account=" + Account
    nntpn    = "ntpn=" + Ntpn
    nppn     = "ppn="  + Ppn
    nmodule  = "module load " + ModuleFile
    nopt     = "optimize_script=" + OptScript
    nprod    = "production_script=" + ProdScript

# make temporary copies of sbatch templates:     
    shutil.copy(sb_start_template,'sb_start_temp')
    shutil.copy(sb_prod_template,'sb_prod_temp')
# make substitutions:
    for f in ["sb_start_temp","sb_prod_temp"]:
        for line in fileinput.FileInput(f,inplace=True):
            line = line.replace('#SBATCH --nodes=X', nnodes)   
            line = line.replace('#SBATCH --time=X', ntime)   
            line = line.replace('#SBATCH --account=X', naccount)   
            line = line.replace('ntpn=X', nntpn)   
            line = line.replace('ppn=X',  nppn)   
            line = line.replace('module load X', nmodule)   
            line = line.replace('optimize_script=X', nopt)   
            line = line.replace('production_script=X', nprod)   
            sys.stdout.write(line)   


    for i in jobdirlist:
        print "{}populating: {}{}/{}".format(c4,c0,JobDir,i)
        stagef['JobDirName'] = i
        ljdfile = JobDir + "/" + i +"/local_job_details.json"
        with open(ljdfile, 'w') as outfile:
            json.dump(stagef, outfile, indent=2)
        outfile.close()

# copy across python scripts from /Setup_and_Config:
        jobdir   = JobDir + "/" + i + "/"
        sbs_path = jobdir + "/sbatch_start"
        sbp_path = jobdir + "/sbatch_production"

        shutil.copy('sb_start_temp',sbs_path)
        shutil.copy('sb_prod_temp',sbp_path)

        for pyfile in glob.glob(r'Setup_and_Config/*.py'):
            try:
                shutil.copy2(pyfile, jobdir)
                print "   {}copying:{}{} {} ".format(c2,c0,cc1, pyfile)
            except:
                print "{}Can't copy python scripts from /Setup_and_Config/{} ".format(c4, c0)  

        for conffile in glob.glob(r'Setup_and_Config/*.conf'):
            try:
                shutil.copy2(conffile, jobdir)
                print "   {}copying:{}{} {} ".format(c2,c0,cc1, conffile)
            except:
                print "{}Can't copy .conf scripts from /Setup_and_Config/{} ".format(c4, c0)  




# remove tempfiles. 
    os.remove('sb_start_temp')
    os.remove('sb_prod_temp')



def check_job():
    """ -function to check the input of the current job and calculate resources required."""
    mcf = read_master_config_file()
    jd_opt,  jd_opt_pl  = read_job_details(mcf["OptimizeConfScript"])    
    jd_prod, jd_prod_pl = read_job_details(mcf["ProdConfScript"])    
      
    print "{}\nJob check summary: ".format(c5)
    print "{}--------------------------------------------------------------------------------".format(c5)
    print "{} Main Job Directory:          {}{}".format(c6,c0,mcf["JobDir"])
    print "{} Simulation basename:         {}{}".format(c6,c0,mcf["BaseDirName"])
    print "{} Sbatch start template:       {}{}.template".format(c6,c0,mcf["SbatchStartScript"])
    print "{} Sbatch prouction template:   {}{}.template".format(c6,c0,mcf["SbatchProdScript"])
    print "{} Optimization script:         {}{}".format(c6,c0,mcf["OptimizeConfScript"])
    print "{} Production script:           {}{}".format(c6,c0,mcf["ProdConfScript"])
    print "{} Namd modulefile:             {}{}".format(c6,c0,mcf["ModuleFile"])

# calculating some numbers:
    sr  = mcf["SimReplicates"]                          # no. of job replicates]
    run = mcf["Runs"]                                   # no. of runs in each replicate
    spr = jd_prod["steps"]                              # steps per run
    dcd = jd_prod["dcdfreq"]                            # dcd write frequency
    dfs = int(jd_prod["natom"])*12.0/(1024.0*1024.0)    # dcd frame size (based on number of atoms from psf)
    tdf = int(spr)/int(dcd)*int(run)*int(sr)            # total dcd frames 
    tpd = tdf*dfs/(1024)                                # total production data 
    tst = (int(sr)*int(run)*int(jd_prod["timestep"])*int(spr))/1000000.0  # total simulated time


    print "{}\nEstimation of data to be generated from the production run of this simulation:{}".format(c5,c0)
    print "{}--------------------------------------------------------------------------------".format(c5)
    print "{} Simulation directories:   {}%-8s      {}Runs per directory:   {}%s".format(c6,c0,c6,c0) % (sr,run)
    print "{} Steps per run:            {}%-8s      {}Dcdfreq in run:       {}%s".format(c6,c0,c6,c0) % (spr,dcd)
    print "{} Dcd frame size(MB)        {}%-8.3f      {}Total dcd frames:     {}%s".format(c6,c0,c6,c0) % (dfs,tdf)

    print " {}   Total simulated time:{}  %12.2f {}nanoseconds".format(c8,c0,cc1) %(tst)
    print " {}   Total production data:{} %12.2f {}GB".format(c8,c0,cc1) %(tpd) 

    print "{}\nNode configuration:{}".format(c5,c0)
    print "{}--------------------------------------------------------------------------------".format(c5)
    print "{}Sbatch Scripts:     {} %s , %s".format(c6,c5) % (mcf["SbatchStartScript"], mcf["SbatchProdScript"])      
    print "{}nodes:              {} %-12s    ".format(c6,c0) % (mcf["nodes"])
    print "{}walltime:           {} %-12s    ".format(c6,c0) % (mcf["Walltime"])
    print "{}no. tasks per node: {} %-12s    ".format(c6,c0) % (mcf["ntpn"])
    print "{}processes per node: {} %-12s    ".format(c6,c0) % (mcf["ppn"])
    print "{}account:            {} %-12s    ".format(c6,c0) % (mcf["Account"])

    print "{}\nChecking configuration input files:{}".format(c5,c0)
    print "{}--------------------------------------------------------------------------------".format(c5)

# checking if files in configuration exist where they are supposed to be. 
    print "{}{}:{}".format(c5,mcf["OptimizeConfScript"],c0)
    check_file_exists(jd_opt["psffilepath"])
    check_file_exists(jd_opt["pdbfilepath"])
    for i in jd_opt_pl:
        check_file_exists(i)

    print "{}{}:{}".format(c5,mcf["ProdConfScript"],c0)
    check_file_exists(jd_prod["psffilepath"])
    check_file_exists(jd_prod["pdbfilepath"])
    for i in jd_prod_pl:
        check_file_exists(i)


def check_file_exists(target):
    mesg1 = "{} found {} -ok!{}".format(c6,c5,c0)
    mesg2 = "{} found {} -ok!{} -example file?{}".format(c6,c5,c4,c0)
    mesg3 = "{} not found.{} -Check config file.{}".format(c1,c8,c0) 

    ntarget = target[6:]        # strip off ../../
    if not "../../" in target[0:6]:
        print "{}unexpected path structure to input files:{}".format(c4,c0)
 
    if os.path.exists(ntarget):
        if "example" in target:
            print "{} %-50s {}".format(cc1,mesg2) %(ntarget)    
        else:
            print "{} %-50s {}".format(cc1,mesg1) %(ntarget)
    else:
        print "{} %-46s {}".format(cc1,mesg3) %(ntarget)
    
    return

def benchmark():
    """ -function to benchmark job """
    print "-- benchmarking jobs."


def get_current_joblist(JobDir):
    """ -function to return current, sorted, joblist in /JobDir """
    if os.path.exists(JobDir):
        jobdirlist = os.walk(JobDir).next()[1]
    jobdirlist.sort()
    return jobdirlist


def start_all_jobs():
    """ -function to start_all_jobs """
    print "-- starting all jobs."
    mcf = read_master_config_file()
    JobDir  = mcf["JobDir"]

    jobdirlist = get_current_joblist(JobDir)

    for i in jobdirlist:    
        # check current job status
        cjs = check_if_job_running(JobDir,i)
        if cjs == "running":
            print "Job already running in JobDir/{} ".format(i)
        else:
            print "submit"            


def restart_all_production_jobs():
    """ -function to restart_all_production_jobs """
    print "-- restarting production jobs."


def recover_all_jobs():
    """ -function to recover and restore crashed jobs """
    print "-- recovering crashed jobs."


def stop_jobs():
    """ -function to stop all jobs, -either immediately or gently."""
    print "-- stopping all jobs"


def new_round():
    """ -function to set up a new round of simulations."""
    print "-- setting up new simulation round"

def erase_all_data():
    """ -function to erase all data for a clean start.  Use with caution!"""
    mcf = read_master_config_file()
    cwd = os.getcwd()
    print "\nWe are about to erase all data in this directory, which can be useful" 
    print "for making a clean start, but disasterous if this is the wrong folder!"
    print "{}Proceed with caution!{}".format(c4,c0)
    print "This operation will delete all data in the folders:\n"
    print "{}/Main_Job_Dir/                   {}- main job directory.{}".format(c2,cc1,c0) 
    print "{}/JobLog/                         {}- Job logs.{}".format(c2,cc1,c0) 
    print "{}/Setup_and_Config/Benchmarking/  {}- Benchmarking data.{}".format(c2,cc1,c0) 
    
    print("\nPress 'enter' to quit or type: '{}erase all my data{}':").format(c1,c0)
    str = raw_input("")
    if str == "erase all my data": 
        print "Ok, well if you say so...."
        for j in ["/Main_Job_Dir/","/JobLog/","/Setup_and_Config/Benchmarking/"]:
	    DIR = cwd + j 
            print "erasing all files in:{}".format(DIR)
            DIR_list = os.listdir(DIR)
            for i in DIR_list:
                DIRx = DIR + i
                shutil.rmtree(DIRx)
        print "\nOh the humanity. I sure hope that wasn't anything important."
    else: 
        print "Phew! Nothing erased."


def clone():
    """ -function to clone directory without data, but preseving input files."""
    print "-- cloning data directory!!" 




