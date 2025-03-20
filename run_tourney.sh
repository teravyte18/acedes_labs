#!/bin/bash

STATS="system.cpu.branchPred.committed_0::DirectCond \
      system.cpu.branchPred.mispredicted_0::DirectCond"

LOGFILE=log.txt

# CLEAR LOG FILE
echo "">log.txt

for ((j=0; j<=16; j++));
do
	for ((i=6; i<=16; i++));
	do
        # print header in both stdout and logfile
        echo "#################################################################"
        echo "#################################################################" >> log.txt
        echo RUNNING LOCAL PREDICTOR WITH SIZE=$((2**i)) AND LOCAL CTRL BITS=$((2**j)) AND CHOICE PREDICTOR SIZE=$((2**j)) AND CHOICE CTRL BITS=4 AND GLOBAL PREDICTOR SIZE=$((2**j)) AND GLOBAL CTRL BITS=4 AND LOCAL HISTORY TABLE SIZE=$((2**j))
        echo RUNNING LOCAL PREDICTOR WITH SIZE=$((2**i)) AND LOCAL CTRL BITS=$((2**j)) AND CHOICE PREDICTOR SIZE=$((2**j)) AND CHOICE CTRL BITS=4 AND GLOBAL PREDICTOR SIZE=$((2**j)) AND GLOBAL CTRL BITS=4 AND LOCAL HISTORY TABLE SIZE=$((2**j)) >> log.txt

        # run gem5 and redirect output to logfile
        /home/teravyte/gem5/build/RISCV/gem5.opt ooo_core.py --localPredictorSize=$((2**i)) --localCtrBits=4 --choicePredictorSize=$((2**j)) --choiceCtrBits=4 --globalPredictorSize=$((2**j)) --globalCtrBits=4 --localHistoryTableSize=$((2**j)) /home/teravyte/gapbs/rv64_bfs &>> log.txt

        # collect the statistics and place them both on stdout and logfile
        for stat in $STATS;
        do
            fgrep $stat m5out/stats.txt
            fgrep $stat m5out/stats.txt >> log.txt
        done;
        echo ""
        echo "" >> log.txt
done

