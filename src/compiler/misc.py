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
sys.path.append("../")

from src.compiler.compiler_exception import CompilerException

from src.structs._ast import Token, Type, SubProgram
from src.compiler.tokenizer import Tokenizer

binary_operators = [
    'or', '==', '!=', '<', '<=', '>', '>=',
    '+', '-', '*', '/', '%',
]

global var_names
var_names = {}

global reserved_func_names
reserved_func_names = ['print_int', 'print_bool', 'print_str', 'print_str',
                       'print_str2', 'str_cat', 'str_len', 'str_cmp',
                       'str_to_int', 'int_to_str', 'get_char_from_str',
                       'input_str', 'create_empty_str', 'pow2', 'set',
                       'array', 'get']

def rename_str_type(source_code: str) -> str:
    """ Replaces type 'Str' to 'String'. """
    
    return source_code.replace(": Str", ": String")


def check_func_name_validity(name: str):
    if name in reserved_func_names:
        raise CompilerException("You cannot define function as name " + str(name))

def remove_comments(tokens: list[Token]) -> list[Token]:
    """ Removes multiline comments. """
    
    new_tokens = []

    comment_detected = False
    for token in tokens:
        if comment_detected == True:
            if token.text == "*/":
                comment_detected = False
                continue
            continue

        if token.text == "/*":
            comment_detected = True
            continue

        new_tokens.append(token)
    return new_tokens


def rename_variables(tokens: list[Token]) -> list[Token]:
    i=0
    j=0

    while i < len(tokens):
        if tokens[i].text == "var":
            name = tokens[i+1].text
            new_name = f"t{i}mp"
            var_names[new_name] = name
            tokens[i+1].text = new_name

            j=i+2
            names = []
            while j < len(tokens):
                if tokens[j].text == "}":
                    names = []
                if tokens[j].text == name:
                    if tokens[j-1].text == "var" and (name in names):
                        raise CompilerException(f"Line {tokens[j].L}: you cannot redeclarate variable {name}")
                        j=j+1
                    names.append(name)
                    tokens[j].text = new_name
                j=j+1
        i=i+1

    return tokens

def pickup_functions(source: str) -> list[list[SubProgram], int]:
    """ 
    Picks up subprograms (=custom function) into list as SubProgram data structures. 
    This function has also parsing properties.
    """

    tokens = Tokenizer(source).tokenize_with_lineno(source, 1)
        
    new_tokens = []
    for key, value in tokens.items():
        last_key = 0
        for token in value:
            new_tokens.append(Token(key, Tokenizer().resolve_type(token), token.strip()))
            last_key = key
        new_tokens.append(Token(last_key+1, None, "None"))
    tokens = new_tokens
    tokens = remove_comments(tokens)

    functions = []

    main_function = SubProgram("main", [], [])
    main_function_startpoint = -1

    ret_type = "Unit"

    i=0
    while i < len(tokens):
        if tokens[i].text == "fun":
            lineno = tokens[i].L
            i=i+1
            name = tokens[i].text
            check_func_name_validity(str(name))
            i=i+1

            if tokens[i].text != "(":
                raise CompilerException(f"Line {tokens[i].L}: syntax error in defining function. Expecting ( but it was {tokens[i].text}")
            i=i+1
            params = []
            
            j=i
            while tokens[j].text != ")":
                if tokens[j].text == ",":
                    j=j+1
                    continue
                params.append(tokens[j].text)               
                j=j+1
            i=j+1

            if tokens[i].text == ":":
                i=i+1
                ret_type = tokens[i].text
                i=i+1

            stack = []
            if tokens[i].text != "{":
                raise CompilerException(f"Line {tokens[i].L}: syntax error in defining function.")
            
            ret_tokens = []
            stack.append("{")
            ret_tokens.append("{")
            i=i+1
            
            try:
                while len(stack) > 0:
                    if tokens[i].text == "{":
                        stack.append("{")
                    if tokens[i].text == "}":
                        stack.pop()
                    ret_tokens.append(tokens[i].text)
                    i=i+1
            except Exception as e:
                raise CompilerException("Unmatch braces in defining function.")
            
            functions.append(SubProgram(name, params, ret_tokens, lineno, ret_type))
        else:
            if main_function_startpoint == -1:
                if tokens[i].text != "None":
                    main_function_startpoint = tokens[i].L
                    main_function.tokens.append(tokens[i].text)
            else:
                main_function.tokens.append(tokens[i].text)
            i=i+1
    functions.append(main_function)

    return functions, main_function_startpoint

def is_left_associative_binary_operator(op: str) -> bool:
    for _op in binary_operators:
        if op == _op:
            return True
    return False

def is_binaryop(tokens: list[Token]) -> int:
    """ 
    Checks if there is a binary operator before new branch begins or current statement closes. 
    If there is a binary operator, returns the index of the binary operator, otherwise returns 0.
    """
    
    i=0
    for token in tokens:
        # If we encouter '=', we interpretthe expression as assignemnt NOT as binary operation
        if token.text == "=":
            return 0

        if token.type == "OPERATOR":
            return i
        
        if token.text == "{" or token.text == ";":
            return 0
        i=i+1
    return 0

def is_identifier(token: Token | str) -> bool:
    """ Checks that token is a correct identifier. """

    regex = r'^[0-9]+'

    input = token.text

    if re.match(regex, input): return False
    return True

def is_int_literal(token: Token):
    """ Checks that token is a correct integer. """

    regex = r'^\-{0,}[0-9]+$'

    input = token.text

    if re.match(regex, input): return True
    return False

def is_bool(token: Token):
    if token.text == "true" or token.text == "false":
        return True
    return False

def add_semidots(tokens: list[Token]) -> list[Token]:
    """ 
    If there is ending brace in token list and the next token 
    after brace IS NOT a semidot, this function adds it.
    """

    new_tkn_list = []

    for i in range(len(tokens)):
        if i == len(tokens)-1:
            if tokens[i].text == "}":
                new_tkn_list.append(tokens[i])
                new_tkn_list.append(Token(tokens[i].L, "PARENTHESIS", ";"))
                break
        if tokens[i].text == "}" and tokens[i+1].text != ";":
            new_tkn_list.append(tokens[i])
            new_tkn_list.append(Token(tokens[i].L, "PARENTHESIS", ";"))
            continue
        new_tkn_list.append(tokens[i])
    return new_tkn_list

def resolve_type(token: Token | str | int | bool, lineno: int = None) -> Type:
    if type(token) != Token:
        #Create mock token
        token = Token(lineno, None, str(token).lower())
    if is_int_literal(token): return Type('Int')
    if is_bool(token): return Type('Bool')
    if is_identifier(token): return Type('Str')
    return Type('Unit')

def not_contains_equal_operator(tokens: list[Token]) -> bool:
    """ Returns true if list of tokens NOT contains == operator. """
    
    if tokens[0].text == "if" or tokens[0].text == "while":
        i=1
        while i < len(tokens):
            if tokens[i].text == "then" or tokens[i].text == "do":
                return True
            
            if tokens[i].type not in ["IDENTIFIER", "PARENTHESIS", "INT_LITERAL"]:
                return False

            i=i+1
    return False

def add_toplevel_context(tokens: list[Token]) -> list[Token]:
    brace_begin = Token(None, "BRACE", "{")
    brace_end = Token(None, "BRACE", "}")

    new_tkn_list = []

    new_tkn_list.append(brace_begin)
    for token in tokens:
        new_tkn_list.append(token)
    new_tkn_list.append(brace_end)

    return new_tkn_list

def add_compare_operator(tokens: list[Token]) -> list[Token]:
    new_tkn_list = []

    i=0
    while i < len(tokens):
        if i+1 > len(tokens): return new_tkn_list

        if not_contains_equal_operator(tokens[i:]):
            new_tkn_list.append(tokens[i])
            
            i=i+1
            while i < len(tokens):
                if tokens[i].text == "then":
                    new_tkn_list.append(Token(tokens[i].L, "OPERATOR", "=="))
                    new_tkn_list.append(Token(tokens[i].L, "IDENTIFIER", "true"))
                    break
                if tokens[i].text == "do":
                    new_tkn_list.append(Token(tokens[i].L, "OPERATOR", "=="))
                    new_tkn_list.append(Token(tokens[i].L, "IDENTIFIER", "true"))
                    break

                new_tkn_list.append(tokens[i])
                i=i+1
        new_tkn_list.append(tokens[i])
        i=i+1
    
    return new_tkn_list
