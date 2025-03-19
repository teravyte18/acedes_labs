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
        for ((k=0; k<=16; k++));
        do
            for ((l=0; l<=16; l++));
            do
                for ((m=0; m<=16; m++));
                do
                    for ((n=0; n<=16; n++));
                    do
                        for ((o=0; o<=16; o++));
                        do
                            # print header in both stdout and logfile
                            echo "#################################################################"
                            echo "#################################################################" >> log.txt
                            echo RUNNING LOCAL PREDICTOR WITH SIZE=$((2**i)) AND LOCAL CTRL BITS=$((2**j)) AND CHOICE PREDICTOR SIZE=$((2**k)) AND CHOICE CTRL BITS=$((2**l)) AND GLOBAL PREDICTOR SIZE=$((2**m)) AND GLOBAL CTRL BITS=$((2**n)) AND LOCAL HISTORY TABLE SIZE=$((2**o))
                            echo RUNNING LOCAL PREDICTOR WITH SIZE=$((2**i)) AND LOCAL CTRL BITS=$((2**j)) AND CHOICE PREDICTOR SIZE=$((2**k)) AND CHOICE CTRL BITS=$((2**l)) AND GLOBAL PREDICTOR SIZE=$((2**m)) AND GLOBAL CTRL BITS=$((2**n)) AND LOCAL HISTORY TABLE SIZE=$((2**o)) >> log.txt

                            # run gem5 and redirect output to logfile
                            /home/teravyte/gem5/build/RISCV/gem5.opt ooo_core.py --localPredictorSize=$((2**i)) --localCtrBits=$((2**j)) --choicePredictorSize=$((2**k)) --choiceCtrBits=$((2**l)) --globalPredictorSize=$((2**m)) --globalCtrBits=$((2**n)) --localHistoryTableSize=$((2**o)) /home/teravyte/gapbs/rv64_bfs &>> log.txt

                            # collect the statistics and place them both on stdout and logfile
                            for stat in $STATS;
                            do
                                fgrep $stat m5out/stats.txt
                                fgrep $stat m5out/stats.txt >> log.txt
                            done;
                            echo ""
                            echo "" >> log.txt
                        done;
                    done;
                done;
            done;
        done;
    done;
done

