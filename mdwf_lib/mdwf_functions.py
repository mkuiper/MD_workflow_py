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
import hashlib
import time 
import datetime
#
#
#
#

def read_master_config_file():  
    """ Reads parameters from json file: master_config_file """  
    cwd=os.getcwd()
    if os.path.isfile('master_config_file'):
        master_json = open('master_config_file')
        try: 
            mcf = json.load(master_json,object_pairs_hook=OrderedDict)
            master_json.close()
        except:
            print "\nPossible json format errors of 'master_config_file'.\n"
    else:
        error = "\nCan't see 'master_config_file' in directory:" + cwd + "\n" 
        sys.exit(error)
    return mcf
        
def read_local_job_details_file():  
    """ Reads parameters from json file: Setup_and_Config/job_details_template.json """  

    target=os.getcwd() +"/Setup_and_Config/job_details_template.json"
    if os.path.isfile(target):
        local_json = open(target)
        try: 
            ljdf = json.load(local_json,object_pairs_hook=OrderedDict)
            local_json.close()
        except:
            print "\nPossible json format errors of 'job_details_template.json'.\n"
    else:
        error = "\nCan't see 'job_details_template.json' in directory:" + cwd + "/Setup_and_Config/\n" 
        sys.exit(error)
    return ljdf

# checks for pausejob flag. Stops job if present. 
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


def monitor_jobs():
    """ -function to monitor jobs status on the cluster """ 
    print "-- monitoring job status ---"





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
        print " Job directory /{} does not exist. Making new directory.".format(JobDir)
        try:
            os.makedirs(JobDir)
        except:
            error = "\nError making directory in /{}.".format(cwd)
            sys.exit(error) 

    # Copy directory structure from /Setup_and Config/JobTemplate
    print " Making Job directory replicates in /{}".format(JobDir)
    TemplatePath = cwd + "/Setup_and_Config/JobTemplate"
    # check existance of JobTemplate directory:
    if not os.path.exists(TemplatePath):
        error = "\nCan't see /Setup_and_Config/JobTemplate. exiting."
        sys.exit(error) 
    
    zf = len(str(Sims)) + 1    
    for i in range(1,Sims+1):
        suffix = str(i).zfill(zf)
        NewDirName = JobDir + "/" + BaseDirName + suffix          
        if os.path.exists(NewDirName):
            print " Directory {} already exists!! Skipping.".format(NewDirName) 
        else:
            try: 
                shutil.copytree(TemplatePath, NewDirName)
                print "Creating: {}".format(NewDirName)             
            except: 
                print "Error in copying directories."



def populate_job_directories():
    """ -function to populate or update job directories with job scripts """
    # copy all files from /Setup_and_Config into each job_directory
    ljdf_t = read_local_job_details_file()        # create template
    mcf    = read_master_config_file()
    try:
        JobDir      = mcf["JobDir"]
        Sims    = int(mcf["SimReplicates"])
        BaseDirName = mcf["BaseDirName"]
        Runs        = mcf["Runs"]
        Round       = mcf["Round"]
    except:
        sys.exit("\nError reading master_config_file variables.\n")

    cwd=os.getcwd()
    TargetJobDir = cwd + "/" +JobDir
    
    # create staging file from ljdf_template
    stagef = ljdf_t           

    # modify elements in staging dictionary file:
    stagef['TOP_DIR'] = cwd
    stagef['CurrentRound'] = Round
    stagef['TotalRuns'] = Runs

    zf = len(str(Sims)) + 1    
    for i in range(1,Sims+1):
        stagef = ljdf_t           # create staging file from ljdf_template
        suffix = str(i).zfill(zf)
        NewDirName = JobDir + "/" + BaseDirName + suffix          
        if not os.path.exists(NewDirName):
            print " Directory {} doesn't exists!".format(NewDirName) 
            
        else:
            # modify elements in staging dictionary file:
            stagef['JobDirName'] = BaseDirName + suffix
            
            ljdfile = NewDirName + "/local_job_details.json"
            # write copy of staging file to new directory:
            with open(ljdfile, 'w') as outfile:
                json.dump(stagef, outfile, indent=2)
            outfile.close()


def check_job():
    """ -function to check the input of the current job and calculate resources required."""
    print "-- checking job input" 

def benchmark():
    """ -function to benchmark job """
    print "-- benchmarking jobs."

def start_all_jobs():
    """ -function to start_all_jobs """
    print "-- starting all jobs."
    




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
    print "We are about to erase all data in this directory, which can be useful" 
    print "for making a clean start, but disasterous if this is the wrong folder!"
    print "\n Proceed with caution!"
    print "This operation will delete all data in the folders:"
    print " /Main_Job_Dir/                    - main job directory." 
    print " /JobLog/                          - Job logs." 
    print " /Setup_and_Config/Benchmarking/   - Benchmarking data." 
    
    str = raw_input("\nPress 'enter' to quit or type: 'erase all my data':")
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




