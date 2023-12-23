#!/bin/bash
version="2.0.0"
message="====Spectro Project==== 
version:$version

Welcome to the Oil Palm Nutrient Predition (ThaiOilPalm project). 
Select which task you want to run. For normal process, run 1,2,3,4.
Or, You can provide [task] when calling this script.

Example: docker compose run --rm thaioilpalmspectro bash main.sh [task]

Task list
=========
- Oil Palm Nutrient Predition From Spectral data (ThaiOilPalm)
    [1]: Predict all nutrient contents (N,P,K,Mg)
    [2]: Merge result
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
    echo "Executing: [$task] Process all nutrient contents (N,P,K,Mg)"
    echo ""
    python3 run_process_v1_0.py
elif [ $task -eq 2 ] 
then
    echo "Executing: [$task]  Merge result"
    echo ""
    python3  run_process_p_V1_0.py



else
    echo "The numer you write is invalid"
fi