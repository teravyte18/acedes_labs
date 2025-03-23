# Copyright (c) 2015 Jason Power
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" This file creates a single CPU and a two-level cache system.
This script takes a single parameter which specifies a binary to execute.
If none is provided it executes 'hello' by default (mostly used for testing)

See Part 1, Chapter 3: Adding cache to the configuration script in the
learning_gem5 book for more information about this script.
This file exports options for the L1 I/D and L2 cache sizes.

IMPORTANT: If you modify this file, it's likely that the Learning gem5 book
           also needs to be updated. For now, email Jason <power.jg@gmail.com>

"""

# import the m5 (gem5) library created when gem5 is built
import m5

# import all of the SimObjects
from m5.objects import *

#######################################################################################
# corrrect the paths (if necessary)
#######################################################################################
# Add the common scripts to our path
m5.util.addToPath("/home/gem5/")
m5.util.addToPath("/home/gem5/configs/")
#######################################################################################

# import the caches which we made
#from caches import *

# import the SimpleOpts module
from common import SimpleOpts

class L1Cache(Cache):
    """Simple L1 Cache with default values"""

    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

    def __init__(self, options=None):
        super().__init__()
        pass

    def connectBus(self, bus):
        """Connect this cache to a memory-side bus"""
        self.mem_side = bus.cpu_side_ports

    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU-side port
        This must be defined in a subclass"""
        raise NotImplementedError


class L1ICache(L1Cache):
    """Simple L1 instruction cache with default values"""

    # Set the default size
    size = "16KiB"

    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU icache port"""
        self.cpu_side = cpu.icache_port


class L1DCache(L1Cache):
    """Simple L1 data cache with default values"""

    # Set the default size
    size = "64KiB"

    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU dcache port"""
        self.cpu_side = cpu.dcache_port


class L2Cache(Cache):
    """Simple L2 Cache with default values"""

    # Default parameters
    size = "256KiB"
    assoc = 8
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12

    def __init__(self, opts=None):
        super().__init__()

    def connectCPUSideBus(self, bus):
        self.cpu_side = bus.mem_side_ports

    def connectMemSideBus(self, bus):
        self.mem_side = bus.cpu_side_ports


# Default to running 'hello', use the compiled ISA to find the binary
# grab the specific path to the binary
thispath = os.path.dirname(os.path.realpath(__file__))
default_binary = os.path.join(
    thispath,
    "hello",
)

# Binary to execute
SimpleOpts.add_option("binary", nargs="?", default=default_binary)

# Finalize the arguments and grab the args so we can pass it on to our objects
# create the system we are going to simulate
system = System()

# Set the clock frequency of the system (and all of its children)
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "2GHz"
system.clk_domain.voltage_domain = VoltageDomain()

# Set up the system
system.mem_mode = "timing"  # Use timing accesses
system.mem_ranges = [AddrRange("512MiB")]  # Create an address range

# Create a simple CPU
system.cpu = O3CPU()

#######################################################################################
# DEFINE EXTRA OPTIONS BEFORE THE ARGS COMMAND
# this example illustrates the procedure to create optional arguments to be passed
# from the command line
#######################################################################################

choicePredictorSize = 2048
SimpleOpts.add_option("--choicePredictorSize", help=f"Size of the choice predictor. Default: {choicePredictorSize}")

choiceCtrBits = 2
SimpleOpts.add_option("--choiceCtrBits", help=f"Choice predictor control bits for BPB saturating counter. Default: {choiceCtrBits}")

globalPredictorSize = 4096
SimpleOpts.add_option("--globalPredictorSize", help=f"Global BP size. Default: {globalPredictorSize}")

globalCtrBits = 2
SimpleOpts.add_option("--globalCtrBits", help=f"Global BP control bits for BPB saturating counter. Default: {globalCtrBits}")

localCtrBits = 2
SimpleOpts.add_option("--localCtrBits", help=f"Local BP control bits for BPB saturating counter. Default: {localCtrBits}")

localPredictorSize = 2048
SimpleOpts.add_option("--localPredictorSize", help=f"Local BP size. Default: {localPredictorSize}")

localHistoryTableSize = 8
SimpleOpts.add_option("--localHistoryTableSize", help=f"Local history table size. Default: {localHistoryTableSize}")

args = SimpleOpts.parse_args() # do not change this line

if args.choicePredictorSize:
    choicePredictorSize=args.choicePredictorSize

if args.choiceCtrBits:
    choiceCtrBits=args.choiceCtrBits

if args.globalPredictorSize:
    globalPredictorSize=args.globalPredictorSize

if args.globalCtrBits:
    globalCtrBits=args.globalCtrBits

if args.localCtrBits:
    localCtrBits=args.localCtrBits

if args.localPredictorSize:
    localPredictorSize=args.localPredictorSize

if args.localHistoryTableSize:
    localHistoryTableSize=args.localHistoryTableSize

#######################################################################################
# DEFINE THE BRANCH PREDICTOR AND PARAMETERS
# first select the predictor. Run once to observe the config options in file
# m5out/config.ini under section [system.cpu.branchPred]
#######################################################################################

#-------------------------------------
# Activate the Local Branch Predictor
#-------------------------------------
# local branch predictor is a table of size localPredictorSize x localCtrBits
# system.cpu.branchPred = LocalBP()
# system.cpu.branchPred.localCtrBits = localCtrBits
# system.cpu.branchPred.localPredictorSize = localPredictorSize

#-------------------------------------
# Activate the Tournament Predictor
#-------------------------------------
# size of the tournament predictor is the sum of bits from the following tables:
# - choice table: size choicePredictorSize x choiceCtrBits
# - globalhistory table: size globalPredictorSize x globalCtrBits
# - localhistory table: size localHistoryTableSize x log2(localPredictorSize)
# - localpredictor table: size localPredictorSize x localCtrBits

system.cpu.branchPred = TournamentBP()
system.cpu.branchPred.choiceCtrBits=choiceCtrBits 
system.cpu.branchPred.choicePredictorSize=choicePredictorSize # Default: 16
system.cpu.branchPred.globalCtrBits=globalCtrBits # Default: 2
system.cpu.branchPred.globalPredictorSize=globalPredictorSize # Default: 16
system.cpu.branchPred.localCtrBits=localCtrBits # Default: 2
system.cpu.branchPred.localPredictorSize=localPredictorSize # Default: 16
system.cpu.branchPred.localHistoryTableSize=localHistoryTableSize # Default: 8

#-------------------------------------
# Activate the LTAGE Predictor
#-------------------------------------
#system.cpu.branchPred = LTAGE()

#-------------------------------------
# Change the parameters of the BTB
#-------------------------------------
# system.cpu.branchPred.btb.associativity = 1 # BTB (cache) associativity (default: 1)
# system.cpu.branchPred.btb.numEntries = 4096 # number of entries (default: 4096)

#-------------------------------------
# Change the parameters of the RAS
#-------------------------------------
#system.cpu.branchPred.ras.numEntries = 16 # number of RAS entries (default: 16; minimum supported value is 1)

#######################################################################################

# Create an L1 instruction and data cache
system.cpu.icache = L1ICache(args)
system.cpu.dcache = L1DCache(args)

# Connect the instruction and data caches to the CPU
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

# Create a memory bus, a coherent crossbar, in this case
system.l2bus = L2XBar()

# Hook the CPU ports up to the l2bus
system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

# Create an L2 cache and connect it to the l2bus
system.l2cache = L2Cache(args)
system.l2cache.connectCPUSideBus(system.l2bus)

# Create a memory bus
system.membus = SystemXBar()

# Connect the L2 cache to the membus
system.l2cache.connectMemSideBus(system.membus)

# create the interrupt controller for the CPU
system.cpu.createInterruptController()

# Connect the system up to the membus
system.system_port = system.membus.cpu_side_ports

# Create a DDR3 memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
#system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

system.workload = SEWorkload.init_compatible(args.binary)

# Create a process for a simple "Hello World" application
process = Process()
# Set the command
# cmd is a list which begins with the executable (like argv)
#######################################################################################
# Define the parameters of the executable
#######################################################################################
process.cmd = [args.binary]
#######################################################################################
# Set the cpu to use the process as its workload and create thread contexts
system.cpu.workload = process
system.cpu.createThreads()

# set up the root SimObject and start the simulation
root = Root(full_system=False, system=system)
# instantiate all of the objects we've created above
m5.instantiate()

print(f"Beginning simulation!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
