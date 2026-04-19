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

asm_lines = ""

# for mapping stack memory and ir variables
global variables
variables = {}
global ptr_top_of_the_stack
ptr_top_of_the_stack = -8

global data
data = ""

global data_section_labels
data_section_labels = []

global param_regs
param_regs = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
global ptr_param_reg
ptr_param_reg = 0

def add_begin(module_name: str):
    return f""" 
.section .text

.global {module_name}
.type {module_name}, @function

"""

def add_double_dots(src: str) -> str:
    lines = src.split("\n")

    asm_lines = ""
    for line in lines:
        if re.match(r"^(\.L).{0,}", line) or re.match(r"^(L).{0,}", line):
            line = line + ":\n"
            asm_lines+= line
            continue
        asm_lines += f"{line}\n"
    return asm_lines

def parse_args(args: str) -> list[str]:
    new_args = []
    if args != "[]":
        args = args.replace("[", "")
        args = args.replace("]", "")
        args = args.replace("\'", "")
        args = args.split(", ")
        for _arg in args:
            if len(_arg) < 3:
                _arg = _arg + "_"
            new_args.append(_arg)
    return new_args

def translate_to_asm(ir: list[str]) -> str:
    asm = ""

    for inst in ir:
        if re.match(r"^(LoadIntConst).{0,}", inst):
            inst = inst.replace("LoadIntConst(", f"movq $").strip()
            asm += f"\t{inst[:len(inst)-1]}"
            asm += "\n"
            continue
        if re.match(r"^(LoadBoolConst).{0,}", inst):
            inst = inst.replace("LoadBoolConst(", f"movq $").strip()
            inst = inst.replace("True", "1")
            inst = inst.replace("False", "0")
            asm += f"\t{inst[:len(inst)-1]}"
            asm += "\n"
            continue
        if re.match(r"^(Copy).{0,}", inst):
            src = inst.replace("Copy(", "").split(", ")[0]
            dst = inst.replace("Copy(", "").split(", ")[1]
            asm += f"\tmovq {src}, %rax\n"
            asm += f"\tmovq %rax, {dst[:len(dst)-1]}\n"
            continue
        if re.match(r"(Call).{0,}", inst):
            operation = inst.replace("Call(", "").split(", ")[0]
            args = inst.split("[")[1].split("]")[0]
            args = f"[{args}]"
            if args != "[]":
                args = parse_args(args)
            dst = inst.split("],")[1].strip()

            if operation.strip() in ['==', '>=', '<=', '>', '<', '!=']:
                asm += f"\txor %rax, %rax\n"
                asm += f"\tmovq {args[0]}, %rdx\n"
                asm += f"\tcmpq {args[1]}, %rdx\n"

                if operation.strip() == "==": 
                    asm += f"\tsete %al\n"
                if operation.strip() == ">=": 
                    asm += f"\tsetge %al\n"
                if operation.strip() == "<=": 
                    asm += f"\tsetle %al\n"
                if operation.strip() == ">": 
                    asm += f"\tsetg %al\n"
                if operation.strip() == "<": 
                    asm += f"\tsetl %al\n"
                if operation.strip() == "!=": 
                    asm += f"\tsetne %al\n"

            elif operation.strip() in ['+', '-', '/', '*', '%']:
                asm += f"\tmovq {args[0]}, %rax\n"

                if operation.strip() == "+": 
                    asm += f"\taddq {args[1]}, %rax\n"
                if operation.strip() == "-": 
                    asm += f"\tsubq {args[1]}, %rax\n"
                if operation.strip() == "*": 
                    asm += f"\timulq {args[1]}, %rax\n"
                if operation.strip() == "/": 
                    asm += f"\tcqto\n\tidivq {args[1]}\n"
                if operation.strip() == "%": 
                    asm += f"\tcqto\n\tidivq {args[1]}\n\tmovq %rdx, %rax\n"

            elif operation.strip() == "unary_-":
                asm += f"\tmovq {args[0]}, %rax\n"
                asm += f"\tnegq %rax\n"

            else:
                # function call

                func_name = inst.replace("Call(", "").split(", [")[0].strip()
                global data

                if func_name == "Str":
                    # string declartion
                    label = f".L_STR_{len(data_section_labels)}"
                    data_section_labels.append(label)
                    data += f".globl {label}\n"
                    data += f"{label}:\n\t.string {args[0].__str__()}\n"
                    asm += f"\tleaq {label}(%rip), %rax\n"
                    asm += f"\tmovq %rax, %rdi\n"
                    asm += f"\tcallq {func_name}\n"
                elif func_name == "array":
                    # array declaration
                    label = f".L_ARRAY_{len(data_section_labels)}"
                    data_section_labels.append(label)
                    length = args[0].__str__().replace("__", "")
                    length = args[0].__str__().replace("_", "")
                    if not re.match(r'^[1-9]{1,}[0-9]{0,}$', length):
                        raise CompilerException(f"Illegal array declaration!")
                    data += f".bss\n"
                    data += f"\t.globl {label}\n"
                    data += f"\t.size {label}, {int(length)*8}\n"
                    data += f"{label}:\n\t.zero {int(length)*8}\n"
                    data += f".data\n"
                    asm += f"\tleaq {label}(%rip), %rax\n"
                    pass
                else:
                    if args.__str__() != "[]":
                    	# We have limited count of parameters. So we don't use stack for additional paramteters like System V 64 calling convention
                        global param_regs
                        regs = param_regs
                        r=0
                        for arg in args:
                            asm += f"\tmovq {arg}, {regs[r]}\n"
                            r+=1
                    asm += f"\tcallq {func_name}\n"

            # store result in the end
            asm += f"\tmovq %rax, {dst[:len(dst)-1]}\n"
            continue

        if re.match(r"(Jump).{0,}", inst):
            l_dst = inst.replace("Jump(", "").replace(")", "")
            l_dst = l_dst.strip()

            asm += f"\tjmp {l_dst}\n"
            continue

        if re.match(r"(CondJump).{0,}", inst):
            var_bool = inst.split("CondJump(")[1].split(", ")[0]
            var_bool = var_bool.strip()

            dests = inst.split("), ")[1].strip().replace(")", "")
            true_dst = dests.split(", ")[0]
            false_dst = dests.split(", ")[1]

            asm += f"\tcmpq $0, {var_bool}\n"
            asm += f"\tjne {true_dst}\n"
            asm += f"\tjmp {false_dst}\n"
            continue

        if re.match(r"(Ret).{0,}", inst):
            value = inst.replace("Ret(", "")[:-1]
            value = value.strip()

            asm += f"\tmovq {value}, %rax\n"
            asm += f"\tmovq %rbp, %rsp\n\tpopq %rbp\n\tret\n"
            continue

        asm += f"{inst}\n"
                
    return asm

def variable_rename(src: list[str]) -> list[str]:
    """ Renames variables of the IR code by stack pointer based. """

    global variables
    var_names = list(variables.keys())

    new_lst = []
    for line in src:
        for var in var_names:
            line = line.replace(var, variables[var])
        new_lst.append(line)
    return new_lst

def exists(vars: dict, search: str) -> bool:
    try:
        _ = vars[search]
        return True
    except:
        return False

def generate_asm(ir_instructions: list[Instruction], module_name: str):
    """ 
    Generates asm code. At first, concatenates character '_' for variables if the lenght of
    the variable is less than 3. Also if variable name does not start with 'x', adds it.
    Then maps variables by x86 stack pointer based. Then renames the variables and translate
    into x86-64 asm.  
    """

    global variables
    global ptr_top_of_the_stack

    insts_as_str = []
    for inst in ir_instructions:
        if isinstance(inst, LoadIntConst) or isinstance(inst, LoadBoolConst):
            if inst.dest[0] != "x":
                inst.dest = "x" + inst.dest
            if len(inst.dest) < 3:
                inst.dest = inst.dest + "_"
        if isinstance(inst, Copy):
            if inst.dest[0] != "x":
                inst.dest = "x" + inst.dest
            if inst.value[0:3] == "arg":
                global ptr_param_reg
                inst.value = param_regs[ptr_param_reg]
                ptr_param_reg += 1
            else:
                if inst.value[0] != "x":
                    inst.value = "x" + inst.value
            if len(inst.dest) < 3:
                inst.dest = inst.dest + "_"
            if len(inst.value) < 3:
                inst.value = inst.value + "_"
        if isinstance(inst, Ret):
            if inst.value[0] != "x":
                inst.value = "x" + inst.value
            if len(inst.value) < 3:
                inst.value = inst.value + "_"
        if isinstance(inst, Call):
            if inst.dest != None and "x" in inst.dest.__str__():
                if len(inst.dest.__str__()) < 3:
                    inst.dest = Label(inst.dest.__str__() + "_")
            
            new_args = []
            arg = inst.args
            if arg != "[]":
                new_args = parse_args(str(arg))
                inst.args = new_args

        if isinstance(inst, CondJump):
            if inst.cond != None and "x" in inst.cond.__str__():
                if len(inst.cond.__str__()) < 3:
                    inst.cond = Label(inst.cond.__str__() + "_") 


        insts_as_str.append(inst.__str__())

    # mapping variables
    for inst in insts_as_str:
        if re.match(r"^(LoadIntConst).{0,}", inst):
            var = inst.split(", ")[1].replace(")", "")
            variables[f"{var}"] = f"{ptr_top_of_the_stack}(%rbp)"
            ptr_top_of_the_stack -= 8
            continue
        if re.match(r"^(LoadBoolConst).{0,}", inst):
            var = inst.split(", ")[1].replace(")", "")
            variables[f"{var}"] = f"{ptr_top_of_the_stack}(%rbp)"
            ptr_top_of_the_stack -= 8
            continue
        if re.match(r"^(Copy).{0,}", inst):
            var1 = inst.split(", ")[0].replace("Copy(", "")
            var2 = inst.split(", ")[1].replace(")", "")

            if var1 in param_regs:
                pass
            else:
                if exists(variables, var1) == False:
                    variables["" + var1] = f"{ptr_top_of_the_stack}(%rbp)"
                    ptr_top_of_the_stack -= 8

            if exists(variables, var2) == False:
                variables["" + var2] = f"{ptr_top_of_the_stack}(%rbp)"
                ptr_top_of_the_stack -= 8
            continue
        if re.match(r"(CondJump).{0,}", inst):
            var_bool = inst.split("CondJump(")[1].split(", ")[0]
            var_bool = var_bool.strip()
            
            if exists(variables, var_bool) == False:
                raise CompilerException("Assembly generation error: undeclarated variable detected in the IR code.")
        if re.match(r"(Ret).{0,}", inst):
            value = inst.split("Ret(")[1].split(")")[0]
            value = value.strip()

            if exists(variables, value) == False:
                raise CompilerException("Assembly generation error: undeclarated variable detected in the IR code.")
        if re.match(r"(Call).{0,}", inst):
            ret_var = inst.split(", ")[-1].replace(")", "")
            if exists(variables, ret_var) == False:
                variables["" + ret_var] = f"{ptr_top_of_the_stack}(%rbp)"
                ptr_top_of_the_stack -= 8
            
            # Parameters
            params = inst.split("[")[1].split("]")[0]

            # Check if string
            if "\"" in params:
                continue

            if len(params) > 3:
                params = params.split(", ")

                for param in params:
                    if exists(variables, param) == False:
                        variables["" + param] = f"{ptr_top_of_the_stack}(%rbp)"
                        ptr_top_of_the_stack -= 8

            continue

    ptr_top_of_the_stack *= -1

    asm_lines = add_begin(module_name)

    asm_lines = asm_lines + f"{module_name}:\n"
    asm_lines = asm_lines + f"""\tpushq %rbp
\tmovq %rsp, %rbp
\tsubq $1024, %rsp
"""
    
    # do translate from ir to x86-64 assembly
    asm_lines = asm_lines + translate_to_asm(variable_rename(insts_as_str))

    # add double dots
    asm_lines = add_double_dots(asm_lines)

    asm_lines = asm_lines + """\tmovq $0, %rax
\tmovq %rbp, %rsp
\tpopq %rbp
\tret
"""

    # restore base pointer
    ptr_top_of_the_stack = -8

    # restore variables
    variables = {}

    # add data section
    asm_lines += ".section .data\n"
    asm_lines += data + ".text\n"

    # rename labels
    asm_lines = asm_lines.replace(".L", f".L_{module_name}_")
    asm_lines = asm_lines.replace("L", f"L_{module_name}_")
    ptr_param_reg = 0
    return asm_lines
