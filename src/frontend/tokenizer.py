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
from frontend.globls import custom_types, externs
from structs._ast import Token

class Tokenizer():

    words = ['while', 'if', 'else', 'do', 'then', 'var', 'Int', 'Str']
    tok_id = 7362834

    def __init__(self, source_code: str | None = None):
        self.source_code = source_code
        self.structs = []

    def re_express_empty_string(self, source_code: str) -> str:
        return source_code.replace("\"\"", "create_empty_str()")
    
    def re_express_constant_string(self, source_code: str) -> str:
        lines = source_code.split("\n")
        regex = r"return \"(.)*\"\;"

        for line in lines:
            line = line.strip()

            if re.match(regex, line):
                occurrence = line.replace("return ", "")[:-1]
                return source_code.replace(occurrence, f"str_cat(create_empty_str(), {occurrence})")
        return source_code
    
    def re_express_strings_start_by_letter_L(self, tokens: list[Token]) -> list[Token]:
        new_tokens = []
        for token in tokens:
            if token.text.startswith("\""):
                if token.text.strip().startswith("\"L"):
                    new_text = token.text.replace("L", f"upperl{self.tok_id}", 1)
                    token.text = new_text
                    new_tokens.append(token)
                    continue
            new_tokens.append(token)

        return new_tokens
        
    def replace_sturcts_and_news(self, source_code: str) -> str:
        lines = source_code.split("\n")
        new_lines = []        

        for line in lines:
            line = line.strip()
            # syntax: define sturct [var_name] = { field_1, ... , field_N }
            if line.startswith("define") and "struct" in line:
                struct = line.split(" ")[2:]
                struct = ' '.join(struct)
                self.structs.append(struct)
                line = "// " + line
            new_lines.append(line)
        
        lines = new_lines
        new_lines = []
        for line in lines:
            if "New" in line and "(" in line and ")" in line and line.strip()[-1] == ";":
                line = line.replace("New(", "")
                line = line.replace(")", "")
                line = line.replace(";", "")

                struct_type = line.split("=")[1].strip()

                found = False
                _struct = ""
                struct_def = ""
                if len(self.structs) > 0:
                    for struct in self.structs:
                        if struct_type in struct:
                            _struct = struct_type
                            struct_def = struct
                            found = True
                    if found == False:
                        raise Exception("Unknown type " + struct_type)
                    line = line.split("=")[0]
                    line = line + f"= {_struct};"
                    s = struct_def.strip().replace(" ", "")
                    name = s.split("={")[0]
                    s = s.split("={")[1].split("};")[0]
                    fields = s.split(",")
                    
                    struct = { 'name' : name, 'fields' : fields }
                    
                    global custom_types
                    custom_types.append(struct)
                else: continue
            new_lines.append(line)
        
        source_code = '\n'.join(new_lines)
        return source_code

    def clean_comments(self, source_code: str) -> str:
        """ Cleans a single line comments. """

        new_lines = []
        lines = source_code.split("\n")
        for line in lines:
            if "#" in line :
                new_line = line.split("#")
                new_lines.append(new_line[0])
                continue
            if "//" in line :
                new_line = line.split("//")
                new_lines.append(new_line[0])
                continue
            new_lines.append(line)
        
        ret_str = ""
        for line in new_lines: ret_str += f"{line.strip()}"
        return ret_str
    
    def handle_externs(self, source_code: str) -> str:
        lines = source_code.split("\n")

        new_lines = []
        for line in lines:
            if "extern " in line.strip():
                line = line.replace(";", "")
                extern_func = line.split(" ")[1]

                global externs
                externs.append(extern_func)
                new_lines.append("")
            else:
                new_lines.append(line)
        return '\n'.join(new_lines)

    
    def tokenize(self, source_code: str = "") -> list[str]:
        """ Casts source code into tokens as string objects """

        # desugars
        source_code = self.replace_sturcts_and_news(source_code)
        source_code = self.handle_externs(source_code)
        source_code = self.clean_comments(source_code)
        source_code = self.re_express_empty_string(source_code)
        source_code = self.re_express_constant_string(source_code)

        # Replace whitespaces and tab spaces
        source_code = source_code.replace("\t", " ")  
        source_code = source_code.replace(" ", "|")
        source_code = source_code.replace("->", "^^")
        source_code = source_code.strip()

        tmp_tokens = []
        long_token = ""
        i=0
        while i < len(source_code):
            c = source_code[i]
            if c == "/" and source_code[i+1] == "*":
                tmp_tokens.append("/*")
                i=i+2
                continue
            if c == "*" and source_code[i+1] == "/":
                tmp_tokens.append("*/")
                i=i+2
                continue
            if c == '"':
                string = self.__do_string(source_code, i)
                tmp_tokens.append(string)
                i=i+len(string)
                continue
            if self.__is_one_char_cmp_word(c):
                if source_code[i+1] == "=":
                    if len(long_token) > 0:
                        tmp_tokens.append(long_token)
                        long_token = ""
                    tmp_tokens.append(f"{c}{source_code[i+1]}")
                    i=i+2
                    continue
            if c == "-" and source_code[i+1].isdigit():
                long_token += c
                i=i+1
                continue
            if self.__is_one_char_word(c):
                if len(long_token) > 0:
                    tmp_tokens.append(long_token)
                    long_token = ""
                tmp_tokens.append(c)
            else:
                if self.__is_word(long_token):
                    tmp_tokens.append(long_token)
                    long_token = ""
                else:
                    long_token += c
            i=i+1
        if len(long_token) > 0:
            tmp_tokens.append(long_token)
        tokens = []
        for t in tmp_tokens:            
            if "^^" in t:
                t = t.replace("|", "")
                tkns = t.split("^^")
                tokens.append(tkns[0])
                tokens.append("->")
                tokens.append(tkns[1])
                continue            
            if "|" in t:
                tkns = t.split("|")
                for _t in tkns:
                    if _t == "" or _t == " ":
                        continue
                    tokens.append(_t)
                continue
            if t.strip() == "" or t == " ": continue
            tokens.append(t)
        return tokens
    
    def do_tokenize(self, source: str, startpoint: int) -> dict[int, list[str]]:
        lines = source.split("\n")
        tokens_as_str = {}

        lineno=startpoint
        for line in lines:
            tokens = self.tokenize(line)
            tokens_as_str[lineno] = tokens
            lineno += 1
        return tokens_as_str
    
    def tokenize_with_lineno(self, source: str, startpoint: int) -> dict[int, list[str]]:
        return self.do_tokenize(source, startpoint)
    
    def generate_tokens(self, source_code: str | None = None, startpoint: int = 1) -> list[Token]:
        """ Generates Token obejcts by the source code. """

        if source_code == None:
            tokens_as_str_in_dict = self.do_tokenize(self.source_code, startpoint)
        else:
            tokens_as_str_in_dict = self.do_tokenize(source_code, startpoint)

        tokens_as_tokenobj = []

        for lineno, tokens_as_str in tokens_as_str_in_dict.items():
            for str_token in tokens_as_str:
                token = self.__build_token(str_token, lineno)
                tokens_as_tokenobj.append(token)

        tokens_as_tokenobj = self.re_express_strings_start_by_letter_L(tokens_as_tokenobj)
        return tokens_as_tokenobj
    
    def __is_word(self, string: str) -> bool:
        """ Checks if input is reserved 'word' like while or else. """
        
        if string in Tokenizer.words:
            return True
        return False
    
    def __is_one_char_cmp_word(self, c: str) -> bool:
        # Attention! Character '!' is not a real operator, but it is necessary to detect it,
        # beacuse of '!=' operator
        words = ['=', '<', '>', '!']

        if c in words:
            return True
        return False
    
    def __is_one_char_word(self, c: str) -> bool:
        words = ['=','>','<',';',':','*','-','+','/','%','(',')','{','}', ',']
        
        if c in words:
            return True
        return False

    def __build_token(self, token_as_str: str, lineno: int | None = None) -> Token:
        type=self.__solve_token_type(token_as_str)
        return Token(lineno, type, token_as_str)
    
    def __do_string(self, source_code: str, start_i: int) -> str:
        string = source_code[(start_i+1):]

        ret_string = "\""
        for c in string:
            if c == '|':
                ret_string += " "
                continue
            if c == '\"':
                ret_string += '\"'
                return ret_string
            ret_string += c
        raise CompilerException("Expected " + '"')
    
    def solve_type(self, token_as_str: str) -> str:
        return self.__solve_token_type(token_as_str)
    
    def __solve_token_type(self, token_as_str: str) -> str:
        regex_parentheses = r"^[(|)]$"
        regex_braces = r"^[{|}]$"
        regex_punctuations = r"^[:|;]$"
        regex_operators = r"^[+|\-|\*|\/|\%|\=]{1}|[\=\=]{1}|[\!\=]{1}|[\<]{1}|[\<\=]{1}|[\>]{1}|[\>\=]{1}$"
        regex_int_literal = r"^[0-9]{1,}$"

        if token_as_str.startswith("\""):
            return "STRING"
        if re.match(regex_parentheses, token_as_str):
            return "PARENTHESIS"        
        if re.match(regex_braces, token_as_str):
            return "BRACE"        
        if re.match(regex_punctuations, token_as_str):
            return "PUNCTUATION"        
        if re.match(regex_operators, token_as_str) or token_as_str == "or":
            if re.match(r"^\-[1-9]+[0-9]*$", token_as_str):
                return "INT_LITERAL"
            return "OPERATOR"        
        if re.match(regex_int_literal, token_as_str):
            return "INT_LITERAL"
        
        # as default return identifier
        return "IDENTIFIER"
