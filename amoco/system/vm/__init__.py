from amoco.system.core import DefineLoader
from amoco.system import elf

@DefineLoader(elf.EM_BPF)
def loader_bpf(p):
    from amoco.system.vm.ebpf import eBPF
    return eBPF(p)
