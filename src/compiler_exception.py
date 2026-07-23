class CompilerException(Exception):
    """ Custom exception for compiler's errors. """
    
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)