#!/usr/bin/env python
# MD workflow functions.   mdwf 
import os
import sys 
import json


def read_master_config_file():  #read variables from json format file  
    cwd=os.getcwd()
    if os.path.isfile('master_config_file'):
        master_json = open('master_config_file')
        try: 
            master_data = json.load(master_json)
            master_json.close()
        except:
            print "possible json format errors of 'master_config_file'"
    else:
        error = "\nCan't see 'master_config_file' in directory:" + cwd + "\n" 
        sys.exit(error)
    return master_data


def monitor_jobs():
    """ -function to monitor jobs status on the cluster """ 
    print "-- monitoring job status ---"

def initialize_job_directories():
    """ -function to setup job directories """
    print "-- initializing job directories."
    master_config_file = read_master_config_file()
    print master_config_file
#    print json.dumps(master_config_file)

def populate_job_directories():
    """ -function to populate or update job directories with job scripts """
    print "-- populating job directories."

def check_job():
    """ -function to check the input of the current job and calculate resources required."""
    print "-- checking job input" 

def benchmark():
    """ -function to benchmark job """
    print "-- benchmarking jobs."

def start_all_jobs():
    """ -function to start_all_jobs """
    print "-- starting jobs."

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
    print "-- erasing all data!!" 

def clone():
    """ -function to clone directory without data, but preseving input files."""
    print "-- cloning data directory!!" 


# mdwf_monitor_status()



