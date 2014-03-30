#!/usr/bin/env python
#
# MD workflow functions.   mdwf 

def monitor_jobs():
    """ -function to monitor jobs status on the cluster """ 
    print "-- monitoring job status ---"

def initialize_job_directories():
    """ -function to setup job directories """
    print "-- initializing job directories."

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
    print "stopping all jobs"

def new_round():
    """ -function to set up a new round of simulations."""
    print "--- setting up new simulation round"

def erase_all_data():
    """ -function to erase all data for a clean start.  Use with caution!"""
    print "erasing all data!!" 


# mdwf_monitor_status()



