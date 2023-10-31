from t_types import *
from libs import errors

values = (IDN, INT, FLT, STR, LST, KYW, BOL)

class Parser:
    def __init__(self, tokens, f_name):
        self.tokens = tokens
        self.current_index = 0
        self.f_name = f_name

    def peek(self):
        if self.current_index < len(self.tokens):
            return self.tokens[self.current_index]
        else:
            return None

    def advance(self):
        if self.current_index < len(self.tokens):
            self.current_index += 1

    def eat(self, token_type):
        current_token = self.peek()
        if current_token and current_token["type"] == token_type:
            self.advance()
        else:
            raise SyntaxError(f"Expected {token_type}, but got {current_token['type']}")

    def factor(self):
        current_token = self.peek()
        if current_token["type"] in values:
            self.advance()
            return current_token
        elif current_token["type"] == "(":
            self.eat("(")
            expression_result = self.expression()
            expression_result = expression_result[0] if len(expression_result) == 1 else {"type": PRM, "value": expression_result}
            self.eat(")")
            return expression_result
        elif current_token["type"] == "{":
            self.eat("{")
            expression_result = {"type": RUN, "value": self.expression()}
            self.eat("}")
            return expression_result
        elif current_token["type"] == "[":
            self.eat("[")
            expression_result = {"type": LST, "value": self.expression()}
            self.eat("]")
            return expression_result
    
    def dots(self):
        left = self.factor()
        current_token = self.peek()
        while current_token and current_token["type"] == ".":
            self.advance()
            right = self.factor()
            left = {"type": IDN, "value": left["value"] + right["value"]}
            current_token = self.peek()
        return left

    def term(self):
        left = self.dots()
        current_token = self.peek()
        while current_token and current_token["type"] in ("*", "/", "%"):
            operator = current_token["value"]
            self.advance()
            right = self.dots()
            left = {"type": operator, "left": left, "right": right}
            current_token = self.peek()
        return left

    def pm(self):
        left = self.term()
        current_token = self.peek()
        while current_token and current_token["type"] in ("+", "-"):
            operator = current_token["value"]
            self.advance()
            right = self.term()
            left = {"type": operator, "left": left, "right": right}
            current_token = self.peek()
        return left
    
    def bs(self):
        left = self.pm()
        current_token = self.peek()
        while current_token and (current_token["type"] in ("<", ">") or (current_token["type"] == KYW and current_token["value"] in ("is", "isnot"))):
            operator = current_token["value"]
            self.advance()
            right = self.pm()
            left = {"type": operator, "left": left, "right": right}
            current_token = self.peek()
        return left
    
    def ao(self):
        left = self.bs()
        current_token = self.peek()
        while current_token and current_token["type"] == KYW and current_token["value"] in ("and", "or"):
            operator = current_token["value"]
            self.advance()
            right = self.bs()
            left = {"type": operator, "left": left, "right": right}
            current_token = self.peek()
        return left
    
    def fc(self):
        left = self.ao()
        current_token = self.peek()
        while current_token and left["type"] == IDN and current_token["type"] == "(":
            right = self.ao()
            left = {"type": "funccall", "name": left, "param": right if right["type"] == PRM else {"type": PRM, "value": [right]}}
            current_token = self.peek()
        return left
    
    def define(self):
        left = self.fc()
        current_token = self.peek()
        while current_token and current_token["type"] == "=":
            self.advance()
            right = self.fc()
            left = {"type": "vardef", "name": left, "value": right}
            current_token = self.peek()
        return left
    
    def expression(self):
        ast = []
        while True:
            if self.peek() in [None, {"type": "}", "value": "}"}, {"type": ")", "value": ")"}, {"type": "]", "value": "]"}]:
                return [{"type": PRM, "value": []}]
            left = self.define()
            current_token = self.peek()
            while current_token and left["type"] == KYW:
                if left["value"] == "import" and current_token["type"] == STR:
                    right = self.define()
                    left = {"type": "import", "module": right}
                elif left["value"] == "return":
                    right = self.define()
                    left = {"type": "return", "value": right}
                    current_token = self.peek()
                elif left["value"] == "delete":
                    right = self.define()
                    left = {"type": "delete", "var": right}
                    current_token = self.peek()
                elif left["value"] == "func":
                    name = current_token
                    self.eat(IDN)
                    params = self.define()
                    params = {"type": PRM, "value": [params]} if params["type"] != PRM else params
                    module = self.define()
                    left = {"type": "funcdef", "name": name, "param": params, "body": module}
                    current_token = self.peek()
                elif left["value"] == "if":
                    statement = self.define()
                    module = self.define()
                    left = {"type": "if", "statement": statement, "body": module, "elseifs": [], "else": None}
                    current_token = self.peek()
                    while current_token != None:
                        if current_token["type"] == KYW and current_token["value"] == "elseif":
                            self.eat(KYW)
                            statement = self.define()
                            module = self.define()
                            left["elseifs"].append({"statement": statement, "body": module})
                            current_token = self.peek()
                        else:
                            break
                    if current_token != None:
                        if current_token["type"] == KYW and current_token["value"] == "else":
                            self.eat(KYW)
                            module = self.define()
                            left["else"] = {"body": module}
                    current_token = self.peek()
                elif left["value"] == "while":
                    statement = self.define()
                    module = self.define()
                    left = {"type": "while", "statement": statement, "body": module}
                    current_token = self.peek()
                elif left["value"] == "for":
                    defin = self.define()
                    sttmnt = self.define()
                    increase = self.define()
                    module = self.define()
                    left = {"type": "for", "defin": defin, "statement": sttmnt, "increase": increase, "body": module}
                    current_token = self.peek()
                elif left["value"] in ("elseif", "else"):
                    errors.ElseOrElseifWithoutIfError(self.f_name, left["value"]).err()
            ast.append(left)
            if current_token in [None, {"type": "}", "value": "}"}, {"type": ")", "value": ")"}, {"type": "]", "value": "]"}]:
                break
        return ast