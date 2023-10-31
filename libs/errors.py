class Error:
    msg: str
    
    def __init__(self, file_name, msg):
        self.msg = f"In '{file_name}' -> {msg}"

    def err(self):
        print(self.msg)
        exit()

#

class LexError(Error):
    def __init__(self, file_name, msg):
        super().__init__(file_name, f"LexError: {msg}")

class WrongCharacterError(LexError):
    def __init__(self, file_name, char):
        super().__init__(file_name, f"WCE: Wrong char -> '{char}'")

class WrongFloatError(LexError):
    def __init__(self, file_name, flt):
        super().__init__(file_name, f"WFE: Wrong FLT declaration -> '{flt}'")

class WrongStringError(LexError):
    def __init__(self, file_name):
        super().__init__(file_name, f"WSE: Wrong STR declaration -> Missing \"")

#

class ParseError(Error):
    def __init__(self, msg):
        self.msg = f"ParseError: {msg}"

class ElseOrElseifWithoutIfError(ParseError):
    def __init__(self, elseorelseif):
        super().__init__(f"EOEWIE: '{elseorelseif}' used without if statement")

#

class RunError(Error):
    def __init__(self, file_name, msg):
        super().__init__(file_name, f"RunError: {msg}")

class NotFoundError(RunError):
    def __init__(self, file_name, notfound):
        super().__init__(file_name, f"NFE: '{notfound}' not found")

class WrongOperationOutputError(RunError):
    def __init__(self, file_name, typ):
        super().__init__(file_name, f"WOOE: '{typ}' can't be a output command")

class ConstructorFuncNotFoundError(RunError):
    def __init__(self, file_name):
        super().__init__(file_name, "NFE: Construcor not found")
        
class ModuleDontExistsError(RunError):
    def __init__(self, file_name, notfound):
        super().__init__(file_name, f"MDEE: '{notfound}' module not exists")