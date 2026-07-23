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

from compiler_exception import CompilerException
from frontend.misc import solve_type, is_custom_type
from frontend.globls import externs

from typing import Any

from structs._ast import (
    Expression,
    Type
)

global userdefined_functions
userdefined_functions = []

global variables
variables = {}

global line_in_binop
line_in_binop = -1

def exists(name: Any):
    """ Checks if variable is already declared. """

    if solve_type(name, line_in_binop).__str__() != 'Str':
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
    
    if a.__str__() != "Int" or b.__str__() != "Int": 
        if a.__str__() == "Any" and b.__str__() == "Int":
            return True
        if a.__str__() == "Int" and b.__str__() == "Any":
            return True
        return False
    return True

def return_int_type(a: Any, b: Any):
    global line_in_binop

    if not must_be_int(a, b):
        raise CompilerException(f"Line {line_in_binop}: Type error! {a} {b} expected Int")
    return Type("Int")

def return_bool_type(a: Any, b: Any):
    global line_in_binop

    if a.__str__() != b.__str__():
        if a.__str__() == "Any" or b.__str__() == "Any":
            print("Warning: you are comparing value of type is any in line")
            return Type('Bool')
        raise CompilerException(f"Line {line_in_binop}: Type error! {a.__str__()} {b.__str__()} expected same types")
    return Type('Bool')

def typecheck(node: Expression) -> Type | Any:
    """ Checks the a type validity of node. Node is an ast. """

    global variables
    global stdout
    global line_in_binop
    match node.__class__.__name__:
        case 'Literal':
            return solve_type(node.value, line_in_binop)
        
        case 'Identifier':
            return solve_type(node.name, line_in_binop)

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
                if is_custom_type(str(node.type)):
                    return Type(str(node.type), True)
                t=typecheck(value)
                _type = Type(node.type.__str__())

                if _type.__str__() == "Int":
                    pass
                else:
                    if _type.__str__() == "Any":
                        variables[str(name)] = Type("Any")
                        return Type("Any")
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
            if node.func_name == "print_int": 
                node.func_type = 'Unit'
                return Type('Unit')
            if node.func_name == "print_bool": 
                node.func_type = 'Unit'
                return Type('Unit')
            if node.func_name == "print_str": 
                node.func_type = 'Unit'
                return Type('Unit')
            if node.func_name == "print_str2": 
                node.func_type = 'Unit'
                return Type('Unit')
            
            if node.func_name == "str_cat": 
                node.func_type = 'String'
                return Type('String')
            if node.func_name == "str_cmp": 
                node.func_type = 'Bool'
                return Type('Bool')
            if node.func_name == "str_len": 
                node.func_type = 'Int'
                return Type('Int')
            if node.func_name == "str_to_int": 
                node.func_type = 'Int'
                return Type('Int')
            if node.func_name == "int_to_str": 
                node.func_type = 'String'
                return Type('String')
            if node.func_name == "get_char_from_str":
                node.func_type = 'String' 
                return Type('String')
            if node.func_name == "input_str": 
                node.func_type = 'String'
                return Type('String')
            if node.func_name == "create_empty_str": 
                node.func_type = 'String'
                return Type('String')
            if node.func_name == "str_clone":
                node.func_type = 'String'
                return Type('String')
            
            if node.func_name == "pow2": 
                node.func_type = 'Int'
                return Type('Int')

            if node.func_name == "set": 
                node.func_type = 'Unit'
                return Type('Unit')
            if node.func_name == "get": 
                node.func_type = 'Int'
                return Type('Int')
            if node.func_name == "array": 
                node.func_type = 'Int'
                return Type('Int')
            if node.func_name == "_malloc": 
                node.func_type = 'Int'
                return Type('Int')
            if node.func_name == "write_long": 
                node.func_type = 'Int'
                return Type('Unit')
            if node.func_name == "read_long": 
                node.func_type = 'Int'
                return Type('Int')

            global userdefined_functions
            for fun in userdefined_functions:
                if node.func_name == fun[0]:
                    node.func_type = fun[1]

                    if is_custom_type(str(node.func_type)):
                        return Type(str(node.func_type), True)
                    return Type(fun[1])
            
            # a special case, not a 'real' function call
            if node.func_name == "Str":
                return Type('String')
            
            global externs
            if node.func_name in externs:
                return Type('Int')
                        
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