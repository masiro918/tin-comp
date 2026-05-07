"""
Copyright 2026 Matias Siro

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import re
import sys
sys.path.append('../')

from src.structs.ir import *
from src.compiler.compiler_exception import CompilerException

def trim_string(string: str) -> str:
    """ Cleans all the whitespaces, tabs ... """

    return string.replace("\t", "").replace(" ", "")

def eliminate_undefined_vars_in_load_insts(insts: list[Instruction]) -> list[Instruction]:
    """ 
    This is ir level optimize. Without this we reserve one unused ir var in
    case of value load.

    E.g.
    We never use x4
    	LoadIntConst(0, x4)
		Copy(x4, t10mp)

    Insted we use t10mp.

    So we can simplify to
        LoadIntConst(0, t10mp)
    """

    new_insts = []

    i=0
    while i < len(insts):
        inst = insts[i]
        if isinstance(inst, LoadIntConst):
            if isinstance(insts[i+1], Copy):
                if inst.dest == inst[i+1].value:
                    src = inst.value
                    dest = insts[i+1].dest
                    new_insts.append(LoadIntConst(src, dest))
                    i=i+2
                    continue
        new_insts.append(inst)
        i=i+1

    return new_insts
   

def detect_irrelevat_reg_mem_operation(line1: str, line2: str) -> str:
    line1 = trim_string(line1)
    line2 = trim_string(line2)

    if ("," in line1 and "movq" in line1) and ("," in line2 and "movq" in line2):
        line1_mem = line1.split(",")[1]
        line2_mem = line2.split(",")[0].split("movq")[1]

        if re.match("^(movq%rax,){1}[\-0123456789\(\%rbp\)]+$", line1):
            if re.match("^(movq){1}[\-0123456789\(\%rbp\)]+(,%rax){1}$", line2):
                if line1_mem == line2_mem:
                    return True
    return False

def clean_nop(lines: list[str]) -> str:
    """ Removes no-opearations """
    
    new_lines = []

    for i in range(len(lines)):
        line = lines[i]
        if i+1 != len(lines):
            if line == "\tnop":
                continue

        new_lines.append(line)
    return '\n'.join(new_lines)

def detect_unused_stack_mem_allocations(lines: list[str]) -> list[str]:
    """ 
    If there are unnecessary memory allocations, e.g. the compiler want to 
    allocate -64(%rbp), but -64(%rbp) is never used, this detects those.

    Return the uneccessary memory allocations (e.g. -16(%rbp))
    """

    pass

def do_optimize(asm_code: str) -> str:
    """ Optimzes the assembly code. """

    new_lines = []
    lines = asm_code.split("\n")

    for i in range(len(lines)):
        line = lines[i]
        if i+1 != len(lines):

            # If there are unneccessry mem -> reg operation
            if detect_irrelevat_reg_mem_operation(line, lines[i+1]):
                lines[i+1] = "\tnop"

        new_lines.append(line)


    return clean_nop(new_lines)