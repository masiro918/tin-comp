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

def replace_if_match(string: str, old: str, new: str) -> str:
    pattern = rf"\b{re.escape(old)}\b"
    return re.sub(pattern, new, string)
        

def rename_irvar(var_name: str, new_varname: str, insts: list[Instruction]) -> list[Instruction]:
    new_insts = []

    for inst in insts:
        if isinstance(inst, Copy):
            inst.dest = replace_if_match(inst.dest, var_name, new_varname)
            inst.value = replace_if_match(inst.value, var_name, new_varname)
            new_insts.append(inst)
            continue
        if isinstance(inst, Call):
            if isinstance(inst.args, str):
                inst.args = replace_if_match(inst.args, var_name, new_varname)
                new_insts.append(inst)
                continue
        if isinstance(inst, LoadIntConst):
            inst.dest = replace_if_match(inst.dest, var_name, new_varname)
            new_insts.append(inst)
            continue
        if isinstance(inst, LoadBoolConst):
            inst.dest = replace_if_match(inst.dest, var_name, new_varname)
            new_insts.append(inst)
            continue
        if isinstance(inst, CondJump):
            if type(inst.cond) != 'str':
                inst.cond = inst.cond.__str__()
            inst.cond = replace_if_match(inst.cond, var_name, new_varname)
            new_insts.append(inst)
            continue
        new_insts.append(inst)
    return new_insts

def put_registers(insts: list[Instruction]) -> list[Instruction]:
    """ Replace bp based memory locations by r12-15 registers """

    while_label_detected = False
    
    count = 0
    i = 0
    while i < len(insts):
        inst = insts[i]
        if count < 1:
            if re.match("^(L){1}[0-9]+(\_WHILE\_START){1}$", inst.__str__()):
                while_label_detected = True
                count += 1
                i += 1
                continue
        elif while_label_detected == True:
            if "Call(" in inst.__str__():
                ins = inst.__str__()
                vars = ins.split("[")[1].split("]")[0]
                vars = vars.split(", ")
                new_insts = rename_irvar(vars[0], "r12", insts)

                if len(vars) > 1:
                    insts = rename_irvar(vars[1], "r13", new_insts)
                break
        i += 1

    while_label_detected = False
    count = 0

    while i < len(insts):
        inst = insts[i]
        if count < 1:
            if re.match("^(L){1}[0-9]+(\_WHILE\_START){1}$", inst.__str__()):
                while_label_detected = True
                count += 1
                i += 1
                continue
        elif while_label_detected == True:
            if "Call(" in inst.__str__():
                ins = inst.__str__()
                vars = ins.split("[")[1].split("]")[0]
                vars = vars.split(", ")
                new_insts = rename_irvar(vars[0], "r14", insts)

                if len(vars) > 1:
                    new_insts = rename_irvar(vars[1], "r15", new_insts)
                return new_insts
        i += 1
    return insts

    

def trim_string(string: str) -> str:
    """ Cleans all the whitespaces, tabs ... """

    return string.replace("\t", "").replace(" ", "")

def occurences(var: str, insts: list[Instruction]) -> int:
    """ Searches how many ir var occurrences in the ir code """

    count = 0
    for inst in insts:
        if var in inst.__str__():
            count += 1
    return count

def eliminate_double_copy_operations(insts: list[Instruction]) -> list[Instruction]:
    """ Copy propagation. """
    
    new_insts = []

    i=0
    while i < len(insts):
        inst = insts[i]
        if isinstance(inst, Copy):
            if isinstance(insts[i+1], Copy):
                if inst.dest == insts[i+1].value and occurences(inst.dest, insts) <= 2:
                    src = inst.value
                    dest = insts[i+1].dest
                    new_insts.append(Copy(src, dest))
                    i=i+2
                    continue
        new_insts.append(inst)
        i=i+1

    return new_insts

def eliminate_undefined_vars_in_load_insts(insts: list[Instruction]) -> list[Instruction]:
    """ 
    This is ir level optimize. Without this we reserve one unused ir var in
    case of value load.
    """

    new_insts = []

    i=0
    while i < len(insts):
        inst = insts[i]
        if isinstance(inst, LoadIntConst):
            if isinstance(insts[i+1], Copy):
                if inst.dest == insts[i+1].value:
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

def do_optimize(asm_code: str) -> str:
    """ Replace irrelevat memory operations by nop. """

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