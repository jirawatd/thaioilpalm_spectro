#!/bin/bash
version="2.0.0"
message="====Rain Project==== 
version:$version

Welcome to the project. 
Select which task you want to run. For normal process, run 1.
Or, You can provide [task] when calling this script.

Example: docker compose run --rm rain bash main.sh [task]

Task list
=========
- Download
    [1]: all process
    [0]: clean, This will clean 'temp' and 'log'

ctrl + D to exit

Select Task: "

# Check if there is $1 (argument)
if [ -z "$1" ]
then
    read -p "$message" task
else
    task=$1
fi

if [ -z "$task" ]
then
    echo "exit"
elif [ $task -eq 0 ]
then
    echo "Executing: [$task] clean"
    echo ""
    rm -r tep/*
    rm -r log/*
elif [ $task -eq 1 ] 
then
    echo "Executing: [$task] all process"
    echo ""
    python3 run_all_process_V1_0.py

else
    echo "The numer you write is invalid"
fi