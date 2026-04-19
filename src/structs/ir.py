class IRVar():
    global __counter
    __counter = 1

    def __init__(self, name: str = None):
        if name == None:
            global __counter
            self.name = f"x{__counter}"
            __counter += 1
            return
        self.name = name

    def __repr__(self):
        return self.__str__()

    def __str__(self) -> str:
        return self.name
    
class Context():
    def __init__(self):
        self.__variables: list[IRVar] = []

    def add_var(self, var: IRVar):
        for _var in self.__variables:
            if _var.__str__() == var.__str__(): return
        self.__variables.append(var)

    def exists(self, var: IRVar | str) -> bool:
        if isinstance(var, str):
            var = IRVar(var)
        for _var in self.__variables:
            if _var.__str__() == var.__str__():
                return True
        return False
        
class Contexts():
    def __init__(self):
        """ 
        In the language's specification, we can reach to the variable if it exists in the
        same context or in the parent context(s). But it if the variable is located in the
        different context, it is uncharted.
        """

        self.__contexts: list[Context] = []

    def push(self, context: Context):
        self.__contexts.append(context)

    def pop(self):
        self.__contexts.pop()

    def add(self, var: IRVar | str):
        """ Adds variable into current context. """
        
        cxt = self.__contexts[-1]

        if isinstance(var, str):
            var = IRVar(var)
        cxt.add_var(var)

    def exists(self, var: IRVar | str):
        """ Checks if variable exists in the current contexts. """

        for context in self.__contexts:
            if context.exists(var): 
                return True
        return False
    


################################
"""
BELOW ARE IR LANG INSTRUCTIONS
"""
################################



class Instruction():
    def __init__(self): pass

    def __repr__(self): return self.__str__()
    def __str__(self) -> str:
        ret_str = "("
        for _, val in self.__dict__.items():
            if type(val) != "list":
                ret_str = ret_str + f"{val}, "
                continue
        ret_str = ret_str[:len(ret_str)-2]
        ret_str += ")"
        
        return f'{type(self).__name__}{ret_str}'
    

class LoadBoolConst(Instruction):
    def __init__(self, value: bool, dest: str):
        self.value = value
        self.dest = dest

class LoadIntConst(Instruction):
    def __init__(self, value: int, dest: str):
        self.value = value
        self.dest = dest

class Copy(Instruction):
    def __init__(self, source: str, dest: str):
        self.value = source
        self.dest = dest

class Label(Instruction):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

class Call(Instruction):
    def __init__(self, fun: str, args: list[str], dest: Label | str):
        self.fun = fun
        self.args = args
        self.dest = dest

    def __str__(self):
        args = str(self.args).replace('\'', '')
        if self.dest == None: raise CompilerException("IR generation error: dest cannot be undefined")
        return f"Call({self.fun}, {args}, {self.dest})"

class Jump(Instruction):
    def __init__(self, label: Label):
        self.label = label

    def __str__(self):
        return f"Jump({self.label})"

class CondJump(Instruction):
    def __init__(self, cond: str, then_label: Label, else_label: Label):
        self.cond = cond
        self.then_label = then_label
        self.else_label= else_label

    def __str__(self):
        return f"CondJump({self.cond}, {self.then_label}, {self.else_label})"

class Ret(Instruction):
    def __init__(self, value: str):
        self.value = value
    
    def __str__(self):
        return f"Ret({self.value})"