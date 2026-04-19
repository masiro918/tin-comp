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
sys.path.append('../')

from src.compiler.compiler_exception import CompilerException

from src.compiler.misc import var_names

from src.structs._ast import (
    Expression, 
    Literal, 
    Identifier, 
    BinaryOp, 
    IfThenCondition, 
    IfElseThenCondition, 
    Block, 
    FunctionCall,
    Assignment,
    VariableDeclaration,
    WhileLoop,
    Break,
    Continue,
    Return,
    String
)

from src.structs.ir import *

reserved_identifiers = ['true', 'false']
reserved_names = ['begin','end','str', 'int', 
                  'bool', 'array', 'set', 'while', 
                  'end', 'if', 'else', 'then', 'do', 
                  'fun', 'continue', 'break', 'return',
                  'true', 'false', 'var']

def generate_ir(root_expr: Expression, params: list[str] = None) -> list[Instruction]:
    created_var = ""

    def new_var() -> IRVar:
        var = IRVar()
        nonlocal created_var
        created_var = var.__str__()
        return var

    stack_ctx = Contexts()
    stack_ctx.push(Context())

    ins: list[Instruction] = []

    current_while = []

    i_label = 1

    def visit(expr: Expression) -> str:
        loc = None

        nonlocal i_label

        match expr:
            case Literal():
                match expr.value:
                    case int():
                        var = new_var()
                        stack_ctx.add(var)

                        if int(expr.value) < 0:
                            value_positive = int(expr.value) * (-1)
                            value_positive = str(value_positive)

                            tmp_var = new_var().__str__()

                            ins.append(
                                LoadIntConst(value_positive, tmp_var))
                            ins.append(Call("unary_-", str([tmp_var]), var.__str__()))
                        else:
                            ins.append(LoadIntConst(
                                expr.value, var.__str__()))
                # Return the variable that holds
                # the loaded value.
                return var
            
            case String():
                return expr.value

            case Identifier():
                variable = expr.name
                var = new_var()

                if variable.__str__() in reserved_identifiers:
                    var_bool = new_var()
                    if variable.__str__() == "true":
                        ins.append(LoadBoolConst(True, var_bool.__str__()))
                    else:
                        ins.append(LoadBoolConst(False, var_bool.__str__()))
                    ins.append(Copy(var_bool.__str__(), var.__str__()))
                    return var

                if stack_ctx.exists(variable) == False:
                    var_name = ""
                    if variable not in var_names.keys():
                        var_name = variable
                    else:
                        var_name = str(var_names[variable])
                    raise CompilerException(f"Line {expr.line}: variable {var_name} is out of the context!")
                ins.append(Copy(variable.__str__(), var.__str__()))
                return var
            
            case BinaryOp():
                left = expr.left
                op = expr.op
                right = expr.right

                param1 = visit(left)
                param2 = visit(right)

                if str(op) in ['+', '-', '/', '*', '%', '!=', '>', '<', '==', '<=', '>=']:
                    var = new_var().__str__()
                    ins.append(Call(op, str([param1, param2]), var))
                    return var
                if str(op) == "or":
                    true_var = new_var().__str__()
                    ins.append(LoadBoolConst("True", true_var))
                    result = new_var().__str__()

                    _true = Label(f".LOR_{i_label}")
                    i_label += 1
                    second_option = Label(f".LSECOND_OPTION_{i_label}")
                    _false = Label(f".Lfalse_{i_label}")
                    i_label += 1
                    _end = Label(f".Lend_{i_label}")
                    i_label += 1
                    ins.append(Call("==", str([param1, true_var]), result))
                    ins.append(CondJump(result, _true, second_option))
                    ins.append(second_option)
                    ins.append(Call("==", str([param2, true_var]), result))
                    ins.append(CondJump(result, _true, _false))
                    ins.append(_false)
                    ins.append(Copy('False', result))
                    ins.append(CondJump(true_var, _end, _end))
                    ins.append(_true)
                    ins.append(Copy(true_var, result))
                    ins.append(_end)

                    return result

            case FunctionCall():
                func_name = expr.func_name
                func_params = expr.params
                ret_val = new_var()

                vars = []
                for param in func_params:
                    vars.append(visit(param))
                
                if func_name == "array":
                    size = str(ins[-1])
                    size = size.split("(")[1].split(",")[0]
                    ins.pop(-1)
                    ins.append(Call(func_name, f"[{str(size)}]", ret_val.__str__()))
                    return ret_val
                ins.append(Call(func_name, str(vars), ret_val.__str__()))
                return ret_val
                                
            case VariableDeclaration():
                name = expr.name

                _var_name = str(var_names[str(name)])
                for _name in reserved_names:
                    if _name == _var_name.lower(): 
                        raise CompilerException(f"Line {expr.name.line}: illegal variable name: {_var_name.__str__()}")

                stack_ctx.add(name.__str__())
                var = visit(expr.value)
                ins.append(Copy(var.__str__(), name.__str__()))

            case Assignment():
                name = expr.left
                
                if stack_ctx.exists(name.__str__()) == False:
                    raise CompilerException(f"Line {name.line}: variable {name.__str__()} is not declared before assign.")

                value = visit(expr.right)
                ins.append(Copy(value.__str__(), name.__str__()))

            case IfThenCondition():
                compare = visit(expr.compare)
                label_then_start=Label(f"L{i_label}_IF")
                label_then_end=Label(f"L{i_label}_IF_END")
                i_label += 1
                ins.append(CondJump(compare, label_then_start, label_then_end))
                ins.append(label_then_start)

                visit(expr.then)

                ins.append(label_then_end)

            case IfElseThenCondition():
                compare = visit(expr.compare)
                label_then_start=Label(f"L{i_label}_IF")
                label_then_end=Label(f"L{i_label}_IF_END")
                label_else_start=Label(f"L{i_label}_ELSE_START")
                label_else_end=Label(f"L{i_label}_ELSE_END")
                i_label += 1
                ins.append(CondJump(compare, label_then_start, label_else_start))
                ins.append(label_then_start)

                visit(expr.then)             
                
                ins.append(label_then_end)
                ins.append(Jump(label_else_end))
                ins.append(label_else_start)
                
                visit(expr._else)

                ins.append(label_else_end)

            case WhileLoop():
                nonlocal current_while
                current_while.append(str(i_label))
                label_while_start=Label(f"L{i_label}_WHILE_START")
                label_while=Label(f"L{i_label}_WHILE")
                label_while_end=Label(f"L{i_label}_WHILE_END")
                i_label += 1

                ins.append(label_while_start)
                compare = visit(expr.compare)
                ins.append(CondJump(compare, label_while, label_while_end))
                ins.append(label_while)
                visit(expr.body)
                ins.append(Jump(label_while_start))
                ins.append(label_while_end)
                current_while.pop()

            case Break():
                label_while_end=Label(f"L{current_while[-1]}_WHILE_END")
                ins.append(Jump(label_while_end))

            case Continue():
                label_while_start=Label(f"L{current_while[-1]}_WHILE_START")
                ins.append(Jump(label_while_start))

            case Return():                
                value = visit(expr.value)
                ins.append(Ret(str(value)))

            case Block():
                statements = expr.expressions
                label_block_start=Label(f".L{i_label}")
                label_block_end=Label(f".L{i_label}_END")
                i_label += 1
                ins.append(label_block_start)
                stack_ctx.push(Context())
                for statement in statements:
                    visit(statement)
                stack_ctx.pop()
                ins.append(label_block_end)

    # Start visiting the AST from the root.

    if params != None:
        i=0
        for param in params:
            stack_ctx.add(param)
            ins.append(Copy(f"arg{i}", param))
            i=i+1
    visit(root_expr)
    
    return ins
