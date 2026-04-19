import sys
sys.path.append("../")

class Token():

    def __init__(self, L: object, type: str, text: str):
        self.L = L
        self.type = type
        self.text = text
    """
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(L={self.L}, type='{self.type}', text='{self.text}')"
    """
    def __str__(self) -> str:
        return self.text
    
#########################
# CLASSES FOR AST NODES #
#########################

class Expression():
    def __init__(self): pass
    def get_type(self): return self.__class__.__name__

class Literal(Expression):
    def __init__(self, value: int | bool, line: int | None = None):
        self.value = value
        self.line = line

    def __repr__(self):
        return str(self.value)
    
class String(Expression):
    def __init__(self, value: str):
        self.value = str(value)

    def __repr__(self):
        return str(self.value)
    
class Identifier(Expression):
    def __init__(self, name: str, line: int | None = None):
        self.name = name
        self.line = line

    def __repr__(self):
        return str(self.name)
    
class BinaryOp(Expression):
    def __init__(self, left: Expression, op: str | Identifier, right: Expression, line: int = None):
        self.left = left
        self.op = op
        self.right = right
        self.line = line

    def __repr__(self):
        return f"BinaryOp(left=[{self.left}], op=[{self.op}], right=[{self.right}])"
    
class IfThenCondition(Expression):
    def __init__(self, compare: Expression, then: Expression):
        self.compare = compare
        self.then = then

    def __repr__(self):
        return f"IfThenCondition(compare=[{self.compare}], then=[{self.then}])"
    
class IfElseThenCondition(Expression):
    def __init__(self, compare: Expression, then: Expression, _else: Expression):
        self.compare = compare
        self.then = then
        self._else = _else

    def __repr__(self):
        return f"IfElseThenCondition(compare=[{self.compare}], then=[{self.then}], else=[{self._else}])"
    
class WhileLoop(Expression):
    def __init__(self, compare: BinaryOp, body: Expression):
        self.compare = compare
        self.body = body

    def __repr__(self):
        return f"WhileLoop(compare=[{self.compare}], body=[{self.body}])"
        

class Block(Expression):
    def __init__(self, expressions: list[Expression], is_unit=False):
        self.expressions = expressions
        self.is_unit = is_unit

    def __repr__(self):
        return f"Block(expressions={self.expressions})"
    
class FunctionCall(Expression):
    def __init__(self, func_name: str, params: list[Identifier | String], line = None):
        self.func_name = func_name
        self.params = params
        self.line = line

    def __repr__(self):
        return f"FunctionCall(func_name=[{self.func_name}], params={self.params})"
    
class Assignment(Expression):
    def __init__(self, left: Identifier, right: Expression):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Assignment(left=[{self.left}], right=[{self.right}])"
    
class VariableDeclaration(Expression):
    def __init__(self, name: Identifier, value: Expression, type: Identifier = None):
        self.name = name
        self.value = value
        self.type = type

    def __repr__(self):
        return f"VariableDeclaration(name=[{self.name}], value=[{self.value}], type=[{self.type}])"
    
class Break(Expression):
    def __init__(self):
        pass
    def __repr__(self):
        return f"Break()"
    
class Continue(Expression):
    def __init__(self):
        pass
    def __repr__(self):
        return f"Continue()"
    
class Return(Expression):
    def __init__(self, value: Expression):
        self.value = value
    def __repr__(self):
        return f"Return(value=[{self.value}])"

class Type():
    def __init__(self, type_name: str):
        if type_name not in ['Int', 'Bool', 'Unit', 'Str', 'String']:
            raise CompilerException(f"Illegal variable type: {type_name}")
        self.type_name = type_name

    def __str__(self):
        return f"{self.type_name}"
    
class SubProgram():
    def __init__(self, name: str, params: list[str], tokens: list[str], lineno: int = -1, ret_type: str = "Unit"):
        self.name = name
        self.params = params
        self.tokens = tokens
        self.lineno = lineno
        self.ret_type = ret_type

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"SubProgram(name={self.name}, params={self.params}, tokens={self.tokens})"
