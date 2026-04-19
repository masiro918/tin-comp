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
import re

sys.path.append("../")

from src.compiler.compiler_exception import CompilerException

from src.structs._ast import Token

class Tokenizer():

    def __init__(self, source_code: str = None):
        self.source_code = source_code

    def clean_comments(self, source_code: str) -> str:
        """ Cleans single line comments. """

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
    
    def tokenize(self, source_code: str = None) -> list[str]:
        """ Casts source code into tokens as string objects """

        # desugars
        source_code = self.clean_comments(source_code)

        # Replace whitespaces and tab spaces
        source_code = source_code.replace("\t", " ")       
        source_code = source_code.replace(" ", "|")
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
    
    def __do_tokenize(self, source_code: str, startpoint: int) -> dict[int, list[str]]:
        lines = source_code.split("\n")

        tokens_as_str = {}

        lineno=startpoint
        for line in lines:
            tokens = self.tokenize(line)
            tokens_as_str[lineno] = tokens
            lineno += 1
        
        return tokens_as_str
    
    def tokenize_with_lineno(self, source_code: str, startpoint: int) -> dict[int, list[str]]:
        return self.__do_tokenize(source_code, startpoint)
    
    def generate_tokens(self, source_code: str = None, startpoint: int = 1) -> list[Token]:
        """ Generates Token obejcts by the source code. """

        if source_code == None:
            tokens_as_str_in_dict = self.__do_tokenize(self.source_code, startpoint)
        else:
            tokens_as_str_in_dict = self.__do_tokenize(source_code, startpoint)

        tokens_as_tokenobj = []

        for lineno, tokens_as_str in tokens_as_str_in_dict.items():
            for str_token in tokens_as_str:
                token = self.__build_token(str_token, lineno)
                tokens_as_tokenobj.append(token)

        return tokens_as_tokenobj

    
    def __is_word(self, string: str) -> bool:
        """ Checks if input is reserved 'word' like while or else. """

        words = ['while', 'if', 'else', 'do', 'then', 'var', 'Int']

        if string in words:
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
        type=self.__resolve_token_type(token_as_str)
        return Token(lineno, type, token_as_str)
    
    def __do_string(self, source_code: str, start_i: int) -> str:
        string = source_code[(start_i+1):]

        ret_string = '"'
        for c in string:
            if c == '|':
                ret_string += " "
                continue
            if c == '\"':
                ret_string += '\"'
                return ret_string
            ret_string += c
        raise CompilerException("Expected " + '"')
    
    def resolve_type(self, token_as_str: str) -> str:
        return self.__resolve_token_type(token_as_str)
    
    def __resolve_token_type(self, token_as_str: str) -> str:
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
