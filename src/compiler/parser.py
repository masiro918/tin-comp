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

from src.compiler.misc import (
    add_toplevel_context, 
    add_compare_operator, 
    add_semidots, 
    is_left_associative_binary_operator, 
    is_binaryop, 
    is_identifier, 
    is_int_literal,
    rename_variables,
    var_names
)

from src.structs._ast import (
    Token, 
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


class Parser():

    pointer = 0

    def parse(tokens: list[Token]) -> Expression:
        """ Returns ast by given tokens. """
        
        pos = 0

        # desugaring top level braces
        tokens = add_toplevel_context(tokens)

        # desugaring missing semidots
        tokens = add_semidots(tokens)

        # desugaring equal binary operators
        tokens = add_compare_operator(tokens)

        # desugar for renaming variables
        tokens = rename_variables(tokens)

        def peek(p: int = 0) -> Token:
            """ Gets the next token but doesn't affects the pointer. """

            if (pos + p) < len(tokens):
                return tokens[pos + p]
            else:
                return Token(None, "END", "")
        
        def consume(expected: str | None = None) -> Token:
            """ 
            Peeks the next token and moves the pointer 'pos' by one ahead. 
            The parameter is optional. If the parameter is set, this function
            also checks that we are expecting actually 'expected' token.
            """

            nonlocal pos

            token = peek()
            if isinstance(expected, str) and token.text != expected:
                raise CompilerException(f"Syntax error in line {token.L} with token {token}, expected {expected}")
            pos += 1
            Parser.pointer = pos
            return token
        
        def parse_factor() -> Expression:
            """ 
            Binary operation has two 'factors' both side of the operator.
            This function is used to parse a factor and if the factor is
            illegal, raises an exception.

            The term factor references expressions that don't need to be
            casted around with { }. For example variable declaration must
            be expressed insided braces.
            """

            if peek().type == 'IDENTIFIER' and peek(1).text == '(':
                return parse_function_call()
            if peek().text == '(':
                return parse_parenthesized()
            if peek().type == 'INT_LITERAL':
                return parse_int_literal()
            elif peek().type == 'IDENTIFIER':
                return parse_identifier()
            else:
                raise CompilerException(f'Line {peek().L}: {peek().text} must be a literal or an identifier, not {peek().type}')

        def parse_parenthesized() -> Expression:
            consume('(')
            expr = parse_expression()
            consume(')')
            return expr
        
        def parse_int_literal() -> Literal:
            token = consume()

            if is_int_literal(token) == False: 
                raise CompilerException(f"Line: {token.L}: illegal integer")
            return Literal(int(token.text))
        
        def parse_identifier() -> Identifier:
            token = consume()

            if is_identifier(token) == False: 
                raise CompilerException(f"Line: {token.L}: illegal identifier")
            return Identifier(str(token.text), token.L)
        
        def parse_if_statement() -> IfThenCondition | IfElseThenCondition:
            consume('if')
            compare = parse_expression()
            consume('then')

            if peek().text == "{":
                then = parse_block()
            else:
                raise CompilerException(f"Line {peek().L}: parsing error after if statement.")

            if peek().text == "else":
                # If there is also else part, parse it
                consume('else')
                
                if peek().text == "{":
                    _else = parse_block()
                else:
                    raise CompilerException(f"Line {peek().L}: parsing error after else statement.")
                return IfElseThenCondition(compare, then, _else)
            return IfThenCondition(compare, then)
        
        def parse_block(in_loop=False) -> Block:
            expressions = list() # type of instances is Stmt
            consume("{")

            while True:
                token = peek()

                if token.text == "}":
                    consume("}")
                    consume(";")
                    break

                expr = parse_expression()
                if expr.__class__.__name__ in ['Break', 'Block', 'IfElseThenCondition', 'IfThenCondition', 'WhileLoop']:
                    expressions.append(expr)
                    continue
                expressions.append(expr)
                
                if peek().text == ";": 
                    consume(";")
                    continue
                else:
                    
                    if peek().text == "}":
                        continue
                    
                    raise CompilerException(f"Line {peek().L}: expecting ; or " + "}" + f" but it was {peek().text}")
                
            return Block(expressions)
        
        def parse_term() -> Expression:
            """ 
            Parses privileged binary operation. For example in case: 1 + 2 * 3, 
            2 * 3 must calulated at first after that add by one.
            """

            left = parse_factor()

            while peek().text in ['*', '/', '%']:
                operator_token = consume()
                operator = operator_token.text
                right = parse_factor()
                left = BinaryOp(
                    left,
                    operator,
                    right
                )
            return left
        
        def parse_binaryop() -> Expression:
            lineno = peek().L
            left = parse_term()
            
            while is_left_associative_binary_operator(peek().text):
                operator_token = consume()
                operator = operator_token.text

                right = parse_term()

                left = BinaryOp(
                    left,
                    operator,
                    right,
                    lineno
                )

            return left

        def parse_function_call() -> FunctionCall:
            func_name = peek().text
            lineno = peek().L
            consume(func_name)

            params = []

            # "skip '(' token"
            consume("(")

            while peek().text != ")":
                if peek().text == ",":
                    consume(",")
                param = parse_expression()
                params.append(param)
            consume(")")
            
            return FunctionCall(func_name, params, lineno)
        
        def parse_assignment() -> Assignment:
            """ Assignments are right associative! """

            left = peek()
            consume(left.text)

            # the operator
            consume("=")
            right = parse_expression()

            return Assignment(Identifier(left, left.L), right)
        
        def parse_while() -> Expression:
            consume("while")
            compare = parse_binaryop()
            consume("do")

            body = None
            
            if peek().text == "{":
                body = parse_block(True)
            else:
                raise CompilerException(f"Line {peek().L}: parsing error after while statement")

            return WhileLoop(compare, body)
        
        def parse_variable_declaration() -> Expression:
            nonlocal pos
            consume("var")

            name = Identifier(peek().text, peek().L)
            pos += 1

            type = None

            if peek().text != ":":
                consume("=")
                value = parse_expression()
                return VariableDeclaration(name, value, type)

            consume(":")
            type = peek()
            pos += 1
            consume("=")
            value = parse_expression()
            return VariableDeclaration(name, value, type)
        
        def parse_break() -> Break:
            consume("break")
            if peek().text == ";":
                consume(";")

            return Break()
        
        def parse_continue() -> Continue:
            consume("continue")
            
            if peek().text == ";":
                consume(";")
            
            return Continue()
        
        def parse_return() -> Return:
            consume("return")
            value = parse_expression()
            
            if peek().text != "{":
                consume(";")
            
            return Return(value) 
        
        def parse_string() -> FunctionCall:
            nonlocal pos
            node_string = String(peek().text)
            pos += 1

            return FunctionCall('Str', [node_string])

        def parse_expression() -> Expression:
            """ 
            The default function that builds abstract syntax tree by recursively.
            Recognize the type of the expression by one or two tokens at the beginning
            and parses the recognized expression in special functions defined above.
            """

            nonlocal pos
            
            token1 = peek()
            token2 = peek(1)

            token1_type = token1.type

            if token1.text.startswith("\""):
                return parse_string()
            
            if token1.text == "return":
                return parse_return()

            if token1.text == "break":
                return parse_break()
            
            if token1.text == "continue":
                return parse_continue()
            
            if token1.text == "if":
                return parse_if_statement()
            
            if token1.text == "{":
                return parse_block()
            
            if token1.text == "var":
                return parse_variable_declaration()
            
            if token1.text == "while":
                return parse_while()
                        
            if is_binaryop(tokens[pos:]):
                return parse_binaryop()
            
            if ((token1_type == "IDENTIFIER") and token2.text == "("):
                return parse_function_call()
            
            if ((token1_type == "IDENTIFIER") and token2.text == "="):
                return parse_assignment()
            
            if token1_type == "INT_LITERAL":
                return parse_int_literal()
            
            if token1_type == "IDENTIFIER":
                return parse_identifier()
            
            raise CompilerException(f"Illegal expression in line {token1.L}")

        return parse_expression()
