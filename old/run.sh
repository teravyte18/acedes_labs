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
        if (( j > i )); then
            continue
        fi
        # print header in both stdout and logfile
        echo "#################################################################"
        echo "#################################################################" >> log.txt
        echo RUNNING LOCAL PREDICTOR WITH SIZE=$((2**i)) AND COUNTER=$((2**j))
		echo RUNNING LOCAL PREDICTOR WITH SIZE=$((2**i)) AND COUNTER=$((2**j)) >> log.txt

        # run gem5 and redirect output to logfile
		/home/teravyte/gem5/build/RISCV/gem5.opt ooo_core.py --localPredictorSize=$((2**i)) --localCtrBits=$((2**j)) /home/teravyte/gapbs/rv64_bfs &>> log.txt

        # collect the statistics and place them both on stdout and logfile
		for stat in $STATS;
        do
            fgrep $stat m5out/stats.txt
            fgrep $stat m5out/stats.txt >> log.txt
        done;
        echo ""
        echo "" >> log.txt
	done;
done

