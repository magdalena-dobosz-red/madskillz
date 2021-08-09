#!/bin/sh
# The script collects statistcs about proccess memory usage and system available memory
# and saves them to file
# Default output directory is /media/mass_storage
# it can be customized by passing as the script parameter

PROC_DIR="/proc"
MASS_STORAGE="/media/mass_storage"
FILENAME="${MASS_STORAGE}/processMemoryStats.txt"

if [ "$#" -eq 1 ]; then
    CUSTOM_DIR=$1
    if [ -w ${CUSTOM_DIR} ]; then
        FILENAME="${CUSTOM_DIR}/processMemoryStats.txt"
        echo "Using custom output directory: ${CUSTOM_DIR}"
    else
        echo "Custom directory ${CUSTOM_DIR} does not exist or not writable, using default."
    fi
fi

mount -o remount,rw,exec ${MASS_STORAGE}

if [ -f ${FILENAME} ]; then
    rm ${FILENAME}
fi

echo "Saving process memory stats to ${FILENAME}"

while [ 1 ]; do
    NOW=`date`
    echo Processes status at: $NOW >> ${FILENAME}
    echo =========================================================================================== >> ${FILENAME}

    for PID in $(ls ${PROC_DIR}); do
        PID_STATUS_FILE="${PROC_DIR}/${PID}/status"
        if [ -f "${PID_STATUS_FILE}" ]; then
            printf "MEMORY DATA FOR PROCESS WITH PID: ${PID} ${PID_STATUS_FILE}\n" >> ${FILENAME}
            echo ===== >> ${FILENAME}
            cat ${PID_STATUS_FILE} | grep "Name:" >> ${FILENAME}
            cat ${PID_STATUS_FILE} | grep "VmRSS:" >> ${FILENAME}
            echo ===== >> ${FILENAME}
        fi
    done

    echo ""
    echo Meminfo: >> ${FILENAME}
    cat /proc/meminfo | grep Mem >> ${FILENAME}
    echo =========================================================================================== >> ${FILENAME}
    echo "" >> ${FILENAME}
    echo "Saved memory data, next iteration in 10 seconds..."
    sleep 10

done
