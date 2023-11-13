#!/bin/bash

DAQ_BASE_DIR="/home/pioneer/pioneer/pioneer-teststand/nearline"
DAQ_LOG_DIR="/home/pioneer/pioneer/pioneer-teststand/nearline_logs"

BASE_DIR="/home/pioneer/dqm/nearline/"
LOG_DIR="/home/pioneer/dqm/nearline_logs/"

time rsync -avh j.carlton@daq:$DAQ_BASE_DIR $BASE_DIR
time rsync -avh j.carlton@daq:$DAQ_LOG_DIR $LOG_DIR