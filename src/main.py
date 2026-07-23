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

import sys
import os

from compiler_exception import CompilerException

from frontend.tokenizer import Tokenizer
from frontend.parser import Parser
from frontend.type_checker import typecheck, userdefined_functions, variables
from frontend.ir_generator import generate_ir
from frontend.misc import (
    pickup_functions, 
    rename_str_type, 
    handle_braces_in_function_definitions,
    rename_variable_words
)
from backend.asm_generator import generate_asm, data
from backend.backend_optimizer import do_optimize

from structs._ast import SubProgram

def compile_module(module: SubProgram, startpoint, is_main_fun = False, optimizations = True) -> str:
    """ Compiles a single 'module' (actually function). Return asm. """

    tokenizer=Tokenizer()
    fun = module.tokens
    tokens = ' '.join(fun)
    tokens = tokens.replace("None", "\n")
    tokens = rename_variable_words(tokens)
    tokens = tokenizer.generate_tokens(tokens, startpoint)
    ast = Parser.parse(tokens)

    # Let's resovle type of the module's parameters
    i=0
    while i < len(module.params):
        if module.params[i] == ":":
            variables[module.params[i-1]] = module.params[i+1]
            i+=1
        else:
            variables[module.params[i]] = "Int"
        i+=1
    
    typecheck(ast)
    ir = generate_ir(ast, module.params, optimizations)

    if is_main_fun == False:
        global userdefined_functions
        userdefined_functions.append([module.name, module.ret_type])
        if not optimizations:
            return generate_asm(ir, module.name).replace("upperl" + str(Tokenizer.tok_id), "L")
        return do_optimize(generate_asm(ir, module.name).replace("upperl" + str(Tokenizer.tok_id), "L"))
    if not optimizations: 
        return generate_asm(ir, "main").replace("upperl" + str(Tokenizer.tok_id), "L")
    return do_optimize(generate_asm(ir, "main").replace("upperl" + str(Tokenizer.tok_id), "L"))

def compile_modules(source: str, optimizations = True):
    """ 
    Compiles the functions one by one. Finally compiles the main function
    which is interpreted the code that is not covered in any custom function.
    """
    
    # handle function definitions
    source = handle_braces_in_function_definitions(source)

    # rename str type
    source = rename_str_type(source)

    # startpoint is the line number where main function starts
    modules, startpoint = pickup_functions(source)

    asm_file = ""
    
    # user-defined functions
    for module in modules[:-1]:
        asm_file = asm_file + compile_module(module, module.lineno, False, optimizations)
    
    # and the main function
    asm_file = asm_file + compile_module(modules[-1], startpoint, True, optimizations)    
    return asm_file

def main(source_file: str, target_file = "a.out", base_dir = "", asm_output_file = False, optimizations = True):
    try:
        source = ""
        with open(source_file) as f:
            source = f.read()
        
        asm_output = compile_modules(source, optimizations)    

        # links the stdlib (not libc!)
        lib = ""
        if asm_output_file == False:
            f=None
            if base_dir == None: f=open("stdlib.s")
            else:
                f=open(base_dir + "stdlib.s")
            lib=lib+f.read()
            f.close()
        f=open("tmp.s", "w")
        f.write(f"{asm_output}\n{lib}")
        f.close()

        if asm_output_file: os.system(f"mv tmp.s {target_file}")
        else:
            os.system(f"c99 -no-pie -mcmodel=large -o {target_file} tmp.s")
            os.remove("tmp.s")
    except Exception as e:
        raise e

if __name__ == '__main__':
    try:
        if len(sys.argv) > 2:
            if len(sys.argv) > 3 and sys.argv[3] == "-S":
                main(sys.argv[1], sys.argv[2], None, True)
            else: main(sys.argv[1], sys.argv[2], None)
        else: main(sys.argv[1])
    except CompilerException as e:
        print(str(e))
        sys.exit(1)
    except Exception as e:
        print("Internal error!")
        sys.exit(1)
