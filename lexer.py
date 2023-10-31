import string
from t_types import *
from libs import errors

kyws = ["is", "isnot", "or", "and", "import", "delete", "func", "if", "elseif", "else", "while", "for", "return"]

def isletter(let):
    return let in list(string.ascii_lowercase) + list(string.ascii_uppercase)

def isdigit(let):
    return let in [*"0123456789"]

class Lexer:
    def __init__(self, text, f_name):
        self.text = text
        self.ind = -1
        self.current_char = ""
        self.f_name = f_name
        self.next()

    def next(self):
        self.ind += 1
        if self.ind == len(self.text): self.current_char = None
        else: self.current_char = self.text[self.ind]
    
    def get_identifier(self):
        c = self.current_char
        self.next()

        while isletter(self.current_char) and self.current_char is not None:
            c += self.current_char
            self.next()
        
        if c in kyws: return {"type": KYW, "value": c}
        elif c in ["true", "false"]: return {"type": BOL, "value": True if c == "true" else False}
        else: return {"type": IDN, "value": [c]}

    def get_string(self):
        self.next()
        c = ""
        while self.current_char != '"' and self.current_char != None:
            c += self.current_char
            self.next()
        
        if self.current_char == None:
            errors.WrongStringError(self.f_name).err()
        
        self.next()
        return {"type": STR, "value": c}

    def get_number(self):
        c = self.current_char
        self.next()

        while (isdigit(self.current_char) or self.current_char == ".") and self.current_char is not None:
            c += self.current_char
            self.next()
        
        if c.count(".") == 0:
            return {"type": INT, "value": int(c)}
        elif c.count(".") == 1:
            return {"type": FLT, "value": float(c)}
        else:
            errors.WrongFloatError(self.f_name, c).err()

    def lex(self):
        t = []
        while self.current_char != None:
            if isletter(self.current_char):
                t.append(self.get_identifier())
            elif self.current_char == '"':
                t.append(self.get_string())
            elif isdigit(self.current_char):
                t.append(self.get_number())
            elif self.current_char in "()+-*/%=:.><}{[]":
                t.append({"type": self.current_char, "value": self.current_char})
                self.next()
            elif self.current_char == " ":
                self.next()
            else:
                errors.WrongCharacterError(self.f_name, self.current_char).err()

        return t
