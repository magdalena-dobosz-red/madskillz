#!/usr/bin/env python3

#The script plots:
#1) available system memory and
#2) processes memory:
# a) either sum of memory consumed by all processes,
# b) or memory comnsumed by each process

#Takes output of "printProcessMemory.sh" as input

import matplotlib.pyplot as plt
import numpy as np
import sys
import argparse
import errno

parser = argparse.ArgumentParser()

defaultFilename = "processMemoryStats.txt"
defaultMemoryLimit = 30
eachMode = "each"
sumMode = "sum"
chosenMode = ""
defaultSize = 20

parser.add_argument('--file', '-f', help="Name of the file with memory report, default is: " + defaultFilename, type=str, default=defaultFilename)
parser.add_argument('--limit', '-l', help="Limit of memory consumption: only processes that consume more memory than this value (on avarage or peak consumption) are presented, default value:  " + str(defaultMemoryLimit), type=int, default=defaultMemoryLimit)
parser.add_argument('--mode', '-m', help="Mode: \"each\" or \"sum\" - show each process memory or sum of all, default is \"each\".", type=str, default=eachMode)
parser.add_argument('--size', '-s', help="Graph width and height in inches, default is: " + str(defaultSize) + ".", type=int, default=defaultSize)

args=parser.parse_args()

reportFilename = args.file

try:
    memoryFile = open(reportFilename, mode='r')
except (OSError, IOError) as error:
    print("Error while opening file " + reportFilename)
    exit()

if args.mode == eachMode:
    chosenMode = eachMode
elif args.mode == sumMode:
    chosenMode = sumMode
else:
    print("Wrong mode chosen.")
    exit()

memAvailableLabel = "MemAvailable:"
timestampLabel = "Processes status at:"
processPidLabel = "MEMORY DATA FOR PROCESS"
processNameLabel = "Name:"
processMemoryLabel = "VmRSS:"
memAvailableData = []
processData = dict()

currentTimestamp = ""
currentProcessPid = ""
currentProcess = ""

kbytesInMBytes = 1024

for line in memoryFile:
    if timestampLabel in line:
        lineParts = line.split()
        currentTimestamp = lineParts[4] + " " + lineParts[5] + " " + lineParts[6]
        processData[currentTimestamp] = dict();
    if memAvailableLabel in line:
        lineParts = line.split()
        memAvailableData.append(int(lineParts[1])/kbytesInMBytes)
    elif processPidLabel in line:
        lineParts = line.split()
        currentProcessPid = lineParts[6]
    elif processNameLabel in line:
        lineParts = line.split()
        currentProcess = lineParts[1] + "(" + currentProcessPid + ")"
        if not currentProcess in processData[currentTimestamp]:
            processData[currentTimestamp][currentProcess] = 0;
    elif processMemoryLabel in line:
        lineParts = line.split()
        containerMemKb = lineParts[1]
        processData[currentTimestamp][currentProcess] += int(containerMemKb)/kbytesInMBytes

memoryFile.close()

processMemSumMb = []
processNames = []
dictOfProcessMemList = dict()

for key,value in processData.items():
    processMemSumMb.append(sum(value.values()))
    for key,value in value.items():
        if key not in processNames:
            processNames.append(key)
            dictOfProcessMemList[key] = []

for key,value in processData.items():
    for processName in processNames:
        if processName in list(value.keys()):
            dictOfProcessMemList[processName].append(int(value[processName]))
        else:
            dictOfProcessMemList[processName].append(int(0))

meanProcessMem = dict()
maxProcessMem = dict()
for key,value in dictOfProcessMemList.items():
    meanProcessMem[key] = int(sum(value))/int(len(value))
    maxProcessMem[key] = int(max(value))

timestamps = list(processData.keys())

memAvailableTimestampsList = list(processData.keys())
if (len(memAvailableTimestampsList) > len(memAvailableData)):
    memAvailableTimestampsList = memAvailableTimestampsList[:len(memAvailableData)]

memoryLimit = args.limit
plt.figure(figsize=(args.size, args.size))

plt.plot(memAvailableTimestampsList, memAvailableData, label = 'MemAvailable', linestyle='solid', marker='o', color='black')

if chosenMode == eachMode:
    for key, value in dictOfProcessMemList.items():
        if meanProcessMem[key] >= memoryLimit or maxProcessMem[key] >= memoryLimit:
            plt.plot(timestamps, value, label = key, linestyle='--', marker='o')
elif chosenMode == sumMode:
    plt.plot(timestamps, processMemSumMb, label = 'process memory sum', linestyle='--', marker='o')

plt.legend()
plt.ylabel("In MB")
plt.xlabel("Timestamp")
plt.xticks([timestamps[0], timestamps[-1]], visible=True, rotation="horizontal")
plt.show()

