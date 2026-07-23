import re

def trim_string(string: str) -> str:
    """ Cleans all the whitespaces, tabs ... """

    return string.replace("\t", "").replace(" ", "")

def detect_irrelevat_reg_mem_operation(line1: str, line2: str) -> bool:
    """ 
    If the asm code consists 
       mov rax, {d}(%rbp) 
    and the next instruction is
       mov {d}(%rbp), rax
    this detects it.
    """
    
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

def parse_2nd_operand(line: str) -> str:
    line = trim_string(line)
    return line.split(",")[-1]

def parse_1nd_operand(line: str) -> str:
    line = trim_string(line)
    if "movq" in line:
        line = line.replace("movq", "")
        return line.split(",")[0]
    line = line.replace("cmpq", "")
    return line.split(",")[0]

def detect_irrelevat_reg_mem_operation2(line1: str, line2: str) -> bool:
    """ 
    If the asm code consists 
       mov rax, {d}(%rbp) 
    and the next instruction is
       mov {d}(%rbp), {register}
    this detects it.
    """
    
    line1 = trim_string(line1)
    line2 = trim_string(line2)

    if ("," in line1 and "movq" in line1) and ("," in line2 and "movq" in line2):
        line1_mem = line1.split(",")[1]
        line2_mem = line2.split(",")[0].split("movq")[1]

        if re.match("^(movq%rax,){1}[\-0123456789\(\%rbp\)]+$", line1):
            if re.match("^(movq){1}[\-0123456789\(\%rbp\)]+(,%[a-z0-9]{3}){1}$", line2):
                if line1_mem == line2_mem:
                    return True
    return False

def detect_irrelevat_reg_mem_operation3(line1: str, line2: str) -> bool:
    """ 
    If the asm code consists 
       mov {d}(%rbp), rax 
    and the next instruction is
       mov rax, {register}
    this detects it.
    """
    
    line1 = trim_string(line1)
    line2 = trim_string(line2)

    if ("," in line1 and "movq" in line1) and ("," in line2 and "movq" in line2):
        line1_mem = line1.split(",")[1]
        line2_mem = line2.split(",")[0].split("movq")[1]

        if re.match("^(movq){1}[\-0123456789\(\%rbp\)]+(,%rax)$", line1):
            if re.match("^(movq%rax,){1}(%[a-z0-9]{3}){1}$", line2):
                if line1_mem == line2_mem:
                    return True
    return False

def detect_irrelevat_reg_mem_operation4(line1: str, line2: str) -> bool:
    """ 
    If the asm code consists 
       mov rax, {d}(%rbp)
    and the next instruction is
       cmpq {constant}, {d}(%rbp)
    this detects it.
    """
    
    line1 = trim_string(line1)
    line2 = trim_string(line2)

    if ("movq" in line1) and ("cmpq" in line2):
        line1_mem = line1.split(",")[1]
        line2_mem = line2.split(",")[1]

        if re.match("^(movq%rax){1},[\-0123456789\(\%rbp\)]+$", line1):
            if re.match("^(cmpq){1}(\$){1}[\-0123456789]+,[\-0123456789\(\%rbp\)]+$", line2):
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


def unused_memory_allocations(lines: list[str]) -> list[str]:
    """ Picks up all the memory allocations """
    
    lines_in_str = '\n'.join(lines)
    mem_allocs = []
    unused_allocs = []

    for line in lines:
        if "nop" in line:
            continue
        if line.strip().startswith("movq %") and "(%rbp)" in line.strip():
            mem_allocs.append(parse_2nd_operand(line))

    # print unused mem allocs
    for mem_alloc in mem_allocs:
        if lines_in_str.count(mem_alloc) > 1:
            continue
        unused_allocs.append(mem_alloc)
    return unused_allocs


def do_propagation_param_registers(insts: list[str], register_dst: str, register_src: str) -> list[str]:
    if (f", %{register_dst}" in ' '.join(insts)) == False:
        i=0
        while i < len(insts):
            inst = insts[i]

            if f"movq %{register_src}, " in inst.__str__():
                dest = inst.__str__().strip().split(f"movq %{register_src}, ")[1]
                
                for j in range(len(insts)):
                    if dest in insts[j]:
                        insts[j] = insts[j].replace(dest, f"%{register_dst}")

                return insts
            insts[i] = inst
            i=i+1
    return insts

def propagation_param_registers(insts: list[str]) -> list[str]:
    insts = do_propagation_param_registers(insts, "r15", "rdi")
    insts = do_propagation_param_registers(insts, "r14", "rsi")
    return insts

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
            if detect_irrelevat_reg_mem_operation2(line, lines[i+1]):
                line = f"\tmovq %rax, {parse_2nd_operand(lines[i+1])}"
                lines[i+1] = "\tnop"
            if detect_irrelevat_reg_mem_operation3(line, lines[i+1]):
                line = f"\tmovq {parse_1nd_operand(line)}, {parse_2nd_operand(lines[i+1])}"
                lines[i+1] = "\tnop"

        new_lines.append(line)
    i=0
    for line in new_lines:
        if i+1 == len(new_lines):
            break
        if detect_irrelevat_reg_mem_operation4(line, new_lines[i+1]):
            line = f"\tcmpq {parse_1nd_operand(new_lines[i+1])}, %rax"
            new_lines[i] = line
            new_lines[i+1] = "\tnop"
        i=i+1

    unused_allocs = unused_memory_allocations(new_lines)

    i=0
    while i < len(new_lines):
        for alloc in unused_allocs:
            if alloc in new_lines[i]:
                new_lines[i] = "\tnop"
                break
        i=i+1

    new_lines = propagation_param_registers(new_lines)

    return clean_nop(new_lines)