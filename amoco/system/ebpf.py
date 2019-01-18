# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2017 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.raw import RawExec
from amoco.system.core import CoreExec,stub
from amoco.code import tag
from amoco.arch.eBPF import cpu

class eBPF(RawExec):
    "This class allows to analyze new (e)bpf bytecodes"

    def __init__(self,p):
        RawExec.__init__(self,p,cpu)

    def initenv(self):
        from amoco.cas.mapper import mapper
        m = mapper()
        m[cpu.r1] = cpu.reg('#ctx',64)
        m[cpu.pc] = cpu.cst(0,64)
        return m

    # load the program into virtual memory (populate the mmap dict)
    def load_binary(self):
        p = self.bin
        if p!=None:
            self.mmap.write(0,p.read())
        self.mmap.newzone(cpu.r10)
        self.mmap.newzone(cpu.reg('#ctx',64))
        self.mmap.newzone(cpu.reg('#skb',64))


    # seqhelper provides arch-dependent information to amoco.main classes
    def seqhelper(self,seq):
        for i in seq:
            if i.mnemonic == 'call':
                ref = i.operands[0].value
                i.misc['imm_ref'] = cpu.ext(bpf_cmd[ref],size=64)
        return seq

    def blockhelper(self,block):
        block._helper = block_helper_
        return CoreExec.blockhelper(self,block)

    def funchelper(self,f):
        return f


#----------------------------------------------------------------------------
# the block helper that will be called
# only when the map is computed.
def block_helper_(block,m):
    # update block.misc based on semantics:
    sta,sto = block.support

# HOOKS DEFINED HERE :
#----------------------------------------------------------------------------

@stub
def BPF_MAP_CREATE(m,**kargs):
    pass

bpf_cmd = {
 0:  "BPF_MAP_CREATE",
 1:  "BPF_MAP_LOOKUP_ELEM",
 2:  "BPF_MAP_UPDATE_ELEM",
 3:  "BPF_MAP_DELETE_ELEM",
 4:  "BPF_MAP_GET_NEXT_KEY",
 5:  "BPF_PROG_LOAD",
 6:  "BPF_OBJ_PIN",
 7:  "BPF_OBJ_GET",
 8:  "BPF_PROG_ATTACH",
 9:  "BPF_PROG_DETACH",
 10: "BPF_PROG_TEST_RUN",
}

bpf_map_type = {
 0:  "BPF_MAP_TYPE_UNSPEC",
 1:  "BPF_MAP_TYPE_HASH",
 2:  "BPF_MAP_TYPE_ARRAY",
 3:  "BPF_MAP_TYPE_PROG_ARRAY",
 4:  "BPF_MAP_TYPE_PERF_EVENT_ARRAY",
 5:  "BPF_MAP_TYPE_PERCPU_HASH",
 6:  "BPF_MAP_TYPE_PERCPU_ARRAY",
 7:  "BPF_MAP_TYPE_STACK_TRACE",
 8:  "BPF_MAP_TYPE_CGROUP_ARRAY",
 9:  "BPF_MAP_TYPE_LRU_HASH",
 10: "BPF_MAP_TYPE_LRU_PERCPU_HASH",
 11: "BPF_MAP_TYPE_LPM_TRIE",
 12: "BPF_MAP_TYPE_ARRAY_OF_MAPS",
 13: "BPF_MAP_TYPE_HASH_OF_MAPS",
}

bpf_prog_type = {
 0:  "BPF_PROG_TYPE_UNSPEC",
 1:  "BPF_PROG_TYPE_SOCKET_FILTER",
 2:  "BPF_PROG_TYPE_KPROBE",
 3:  "BPF_PROG_TYPE_SCHED_CLS",
 4:  "BPF_PROG_TYPE_SCHED_ACT",
 5:  "BPF_PROG_TYPE_TRACEPOINT",
 6:  "BPF_PROG_TYPE_XDP",
 7:  "BPF_PROG_TYPE_PERF_EVENT",
 8:  "BPF_PROG_TYPE_CGROUP_SKB",
 9:  "BPF_PROG_TYPE_CGROUP_SOCK",
 10: "BPF_PROG_TYPE_LWT_IN",
 11: "BPF_PROG_TYPE_LWT_OUT",
 12: "BPF_PROG_TYPE_LWT_XMIT",
}
