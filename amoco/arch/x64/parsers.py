from amoco.arch.x64.cpu_x64 import instruction_x64
from amoco.arch.x64.utils import CONDITION_CODES
from amoco.arch.x64 import env

from amoco.arch.x86.parsers import att_syntax_gen
att_syntax = att_syntax_gen(env, CONDITION_CODES, 64, instruction_x64)

