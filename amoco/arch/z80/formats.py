from amoco.arch.core import Formatter

def mnemo(i):
    return '{:<8}'.format(i.mnemonic.replace('cc','').lower())

def opers(i):
    ops = []
    for op in i.operands:
        if not isinstance(op,str) and op._is_mem:
            op = op.a
            if op.base._is_eqn:
                s = str(op)[1:-1]
                ops.append(s)
                continue
        ops.append('%s'%op)
    return ', '.join(ops)

default_format = [mnemo, opers]

Mostek_full_formats = {
    'mostek_ld'        : default_format,
    'mostek_arithmetic': default_format,
    'mostek_gpa_cpuc'  : [mnemo],
    'mostek_rotshift'  : default_format,
    'mostek_bitset'    : default_format,
    'mostek_jump'      : default_format,
    'mostek_call'      : default_format,
    'mostek_ret'       : default_format,
    'mostek_rst'       : default_format,
    'mostek_io'        : default_format,
}

Mostek_full = Formatter(Mostek_full_formats)

Mostek_full.default = default_format

GB_full = Mostek_full
