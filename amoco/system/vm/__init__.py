from amoco.system.core import DefineLoader,logger
from amoco.system import elf


@DefineLoader("elf", elf.EM_BPF)
def loader_bpf(p):
    from amoco.system.vm.ebpf import eBPF
    logger.info("vm/bpf task loaded")
    return eBPF(p)
