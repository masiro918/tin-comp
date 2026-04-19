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
sys.path.append("../")

from src.compiler.compiler_exception import CompilerException

from typing import Any

from src.structs._ast import (
    Expression,
    Type
)
from src.compiler.misc import resolve_type

global userdefined_functions
userdefined_functions = []

global variables
variables = {}

global line_in_binop
line_in_binop = -1

def exists(name: Any):
    """ Checks that variable is already declared. """
    if resolve_type(name, line_in_binop).__str__() != 'Str':
        return False
    try:
        _ = variables[str(name)]
        return True
    except:
        return False
    
def must_be_int(a: Any, b: Any):
    """ 
    Checks that a and b must be type of an integer. 
    """
    
    if a.__str__() != "Int" or b.__str__() != "Int": return False
    return True

def return_int_type(a: Any, b: Any):
    global line_in_binop

    if not must_be_int(a, b):
        raise CompilerException(f"Line {line_in_binop}: Type error! {a} {b} expected Int")
    return Type("Int")

def return_bool_type(a: Any, b: Any):
    global line_in_binop

    if a.__str__() != b.__str__():
        raise CompilerException(f"Line {line_in_binop}: Type error! {a.__str__()} {b.__str__()} expected same types")
    return Type('Bool')

def typecheck(node: Expression) -> Type:
    """ Checks the a type validity of node. Node is an ast. """

    global variables
    global stdout
    global line_in_binop
    match node.__class__.__name__:
        case 'Literal':
            return resolve_type(node.value, line_in_binop)
        
        case 'Identifier':
            return resolve_type(node.name, line_in_binop)

        case 'BinaryOp':
            a = node.left
            b = node.right

            line_in_binop = node.line
            
            if exists(a):
                a = variables.get(a.__str__())
            else:
                a: Type = typecheck(a)
            if exists(b):
                b = variables.get(b.__str__())
            else:
                b: Type = typecheck(b)
                        
            if node.op == '+':
                return return_int_type(a, b)
            elif node.op == '-':
                return return_int_type(a, b)
            elif node.op == '*':
                return return_int_type(a, b)
            elif node.op == '/':
                return return_int_type(a, b)
            elif node.op == '%':
                return return_int_type(a, b)


            elif node.op == '<':
                return return_bool_type(a, b)
            elif node.op == '==':
                return return_bool_type(a, b)
            elif node.op == '!=':
                return return_bool_type(a, b)
            elif node.op == '>':
                return return_bool_type(a, b)
            elif node.op == '>=':
                return return_bool_type(a, b)
            elif node.op == '<=':
                return return_bool_type(a, b)
            elif node.op == 'or':
                return return_bool_type(a, b)
            
        case 'VariableDeclaration':
            name = node.name
            value = node.value
                        
            if typecheck(name).__str__() != 'Str': raise CompilerException(f"Line {name.line}: Type error!")
            
            if node.type != None:
                t=typecheck(value)
                _type = Type(node.type.__str__())

                if _type.__str__() == "Int":
                    pass
                else:
                    if _type.__str__() != t.__str__(): 
                        raise CompilerException(f"Line {name.line}: illegal value for {node.type.__str__()} type")

                variables[str(name)] = Type(node.type.__str__())
                return Type(node.type.__str__())
            
            t=typecheck(value)
            
            if t.__str__() == "Str":
                if exists(value.__str__()) == False:
                    raise CompilerException(f"Line {name.line}: undeclared variable {value.__str__()}")
                _type = variables.get(value.__str__())
                t = Type(_type.__str__())
            variables[str(name)] = t
            return t
        
        case 'Assignment':
            name = node.left
            value = node.right

            if typecheck(name).__str__() != 'Str':
                raise CompilerException(f"Line: {name.line}: type error! " + typecheck(name).__str__())
            
            t = typecheck(value)

            variables[str(name)] = t.__str__()
            return t

        case 'IfThenCondition':
            typecheck(node.compare)
            typecheck(node.then)
            
            return Type('Unit')
            
        case 'IfElseThenCondition':
            typecheck(node.compare)
            typecheck(node.then)
            typecheck(node._else)

            return Type('Unit')
            
        case 'FunctionCall':
            if node.func_name == "print_int": return Type('Unit')
            if node.func_name == "print_bool": return Type('Unit')
            if node.func_name == "print_str": return Type('Unit')
            if node.func_name == "print_str2": return Type('Unit')
            
            if node.func_name == "str_cat": return Type('String')
            if node.func_name == "str_cmp": return Type('Bool')
            if node.func_name == "str_len": return Type('Int')
            if node.func_name == "str_to_int": return Type('Int')
            if node.func_name == "int_to_str": return Type('String')
            if node.func_name == "get_char_from_str": return Type('String')
            if node.func_name == "input_str": return Type('String')
            if node.func_name == "create_empty_str": return Type('String')
            
            if node.func_name == "pow2": return Type('Int')

            if node.func_name == "set": return Type('Unit')
            if node.func_name == "get": return Type('Int')
            if node.func_name == "array": return Type('Unit')

            global userdefined_functions
            for fun in userdefined_functions:
                if node.func_name == fun[0]:
                    return Type(fun[1])
            
            # a special case, not a 'real' function call
            if node.func_name == "Str":
                return Type('String')
            
            raise CompilerException(f"Line {node.line}: Unknown function name: " + str(node.func_name))
            
        case 'Block':
            exprs = node.expressions
            for block in exprs:
                typecheck(block)
            return Type('Unit')
        
        case 'WhileLoop':
            typecheck(node.compare)
            typecheck(node.body)
            return Type('Unit')
        
        case 'Break':
            return Type('Unit')
        
        case 'Continue':
            return Type('Unit')
        
        case 'Return':
            return Type('Unit')