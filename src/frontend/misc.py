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

from compiler_exception import CompilerException

from frontend.tokenizer import Tokenizer
from frontend.globls import var_names, custom_types

from structs._ast import Token, Type, SubProgram

binary_operators = [
    'or', '==', '!=', '<', '<=', '>', '>=',
    '+', '-', '*', '/', '%',
]

global reserved_func_names
reserved_func_names = ['print_int', 'print_bool', 'print_str', 'print_str',
                       'print_str2', 'str_cat', 'str_len', 'str_cmp',
                       'str_to_int', 'int_to_str', 'get_char_from_str',
                       'input_str', 'create_empty_str', 'pow2', 'set',
                       'array', 'get']

def replace_struct_inits(tokens: list[Token]) -> list[Token]:
    new_tokens = []

    i=0
    added=False
    while i < len(tokens):
        type = tokens[i].text.strip()
        for struct in custom_types:
            if struct["name"] == type and tokens[i-1].text == "=" and tokens[i+1].text == ";":
                field_count = len(struct["fields"])
                new_tokens.pop()
                new_tokens.append(Token(None, "OPERATOR", "="))
                new_tokens.append(Token(None, "IDENTIFIER", "_malloc"))
                new_tokens.append(Token(None, "PARENTHESIS", "("))
                new_tokens.append(Token(None, "INT_LITERAL", f"{field_count}"))
                new_tokens.append(Token(None, "IDENTIFIER", ")"))
                added=True
                break
        if not added:
            new_tokens.append(tokens[i])
        else:
            added=False
        i=i+1

    return new_tokens

def replace_struct_refereces_by_the_index(tokens: list[Token]) -> list[Token]:
    new_tokens = []

    i=0
    while i < len(tokens):
        if tokens[i].text == "->":
            type = tokens[i-1].text.strip()
            field = tokens[i+1].text.strip()
            for struct in custom_types:
                if struct["name"] == type:
                    field_idx = struct["fields"].index(field)
                    new_tokens.pop()
                    new_tokens.append(Token(None, "INT_LITERAL", f"{field_idx}".strip()))
                    i=i+1
                    break
        else:
            new_tokens.append(tokens[i])
        i=i+1

    return new_tokens

def handle_braces_in_function_definitions(source: str) -> str:
    """ 
    If function definition line does not consists {, this function adds it
    and remove { at the next token occurrence.
    """
    
    try:
        new_lines = []
        lines = source.split("\n")

        brece_added = False
        for line in lines:
            if brece_added == True:
                if line.strip() == "":
                    new_lines.append("// comment")
                    continue
                if line.strip()[0] == "{":
                    brece_added = False
                    line = line[1:]
                else:
                    raise Exception
            if line.strip()[0:3] == "fun" and line.strip()[-1] != "{":
                brece_added = True
                line = line + "{"
            new_lines.append(line)

        return '\n'.join(new_lines)
    except Exception:
        return source

def rename_str_type(source_code: str) -> str:
    """ Replaces type 'Str' to 'String'. """
    
    return source_code.replace(": Str", ": String")

def do_rename_variable_words(word: str, replacement: str, source_code: str) -> str:
    blocks = source_code.split("\n")
    for block in blocks:
        block = block.strip()

        if block.startswith(word):
            var_name = block.replace(word, "")
            new_var_name = replacement + var_name.split(" ")[0]
            occurence = f"{block.split(' ')[1]} {block.split(' ')[2]} "
            source_code = source_code.replace(occurence, new_var_name)

    return source_code

def rename_variable_words(source_code: str) -> str:
    source_code = do_rename_variable_words("var var ", "v_ar", source_code)
    source_code = do_rename_variable_words("var while ", "w_hile", source_code)
    return source_code

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
            level = 0
            while j < len(tokens):
                if tokens[j].text == "{":
                    level += 1
                if tokens[j].text == "}":
                    level -= 1
                    if level < 0:
                        names = []
                if tokens[j].text == name:
                    if tokens[j-1].text == "var" and (name in names):
                        raise CompilerException(f"Line {tokens[j].L}: you cannot redeclarate variable {name}")
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

    # handle if reserved words in functions
    for word in Tokenizer.words:
        source = source.replace(f"{word}_", f"f{word}_")
    
    tokens = Tokenizer().tokenize_with_lineno(source, 1)
        
    new_tokens = []
    for key, value in tokens.items():
        last_key = 0
        for token in value:
            new_tokens.append(Token(key, Tokenizer().solve_type(token), token.strip()))
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

def is_custom_type(_type: str) -> bool:
    """ check if custom type """

    global custom_types
    for type in custom_types:
        if type.__str__() == str(_type):
            return True
    return False

def solve_type(token: Token | str | int | bool, lineno: int = None) -> Type:
    """ Solve token's type. """

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
    """ Add the top contexts for source code """

    brace_begin = Token(None, "BRACE", "{")
    brace_end = Token(None, "BRACE", "}")

    new_tkn_list = []

    new_tkn_list.append(brace_begin)
    for token in tokens:
        new_tkn_list.append(token)
    new_tkn_list.append(brace_end)

    return new_tkn_list

def add_compare_operator(tokens: list[Token]) -> list[Token]:
    """ 
    Adds a compare operator in case of such as

    if is_prsedident(trump) then { ..... }

    =>

    if is_prsedident(trump) == true then { ..... }
    
    """
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