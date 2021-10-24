from tokenizer import Tokenizer, RawToken
from ast_nodes import *

class Parser:
    """ Recursive descent parser for L-System grammar """
    
    def __init__(self):
        self._string = ""
        self._tokenizer = Tokenizer()


    def parse(self, string):
        self._string = string
        self._tokenizer.initialize(string)

        # prime the tokenizer for predictive parsing
        self._lookahead = self._tokenizer.get_next_token()

        return self._prod_root()
    
    
    def _syntax_error(self, message, raise_as_exception=True, buffered_pos=True):
        line, col = self._tokenizer.get_pos(buffered=buffered_pos)
        printed_msg = f"[{line}:{col}] {message}\n{self._tokenizer.get_error_excerpt(use_buffered_pos=buffered_pos)}"
        if raise_as_exception:
            raise SyntaxError(printed_msg)
        else:
            print(printed_msg)


    def _consume(self, expected_token_type: str):
        token = self._lookahead
        if token == None:
            self._syntax_error(f"Unexpected end of input, expected '{self._tokenizer.get_readable(expected_token_type)}'")
        
        if token.token_type != expected_token_type:
            self._syntax_error(f"Unexpected token '{self._tokenizer.get_readable(token.token_type)}', expected '{self._tokenizer.get_readable(expected_token_type)}'")
        
        self._lookahead = self._tokenizer.get_next_token()
        return token


    def _prod_root(self):
        nodes = []
        while self._lookahead != None:
            nodes.append(self._prod_decl())
        return RootNode(nodes)
    

    def _prod_decl(self):
        decl_type = self._lookahead.token_type
        node = None
        if decl_type == "var":
            node = self._prod_var()
        elif decl_type == "rule":
            node = self._prod_rule()
        elif decl_type == "axiom":
            node = self._prod_axiom()
        elif decl_type == "length":
            node = self._prod_length()
        elif decl_type == "iterate":
            node = self._prod_iterate()
        elif decl_type == "transform":
            node = self._prod_transform()
        else:
            self._syntax_error(f"Unknown token '{self._tokenizer.get_readable(decl_type)}', expected declaration", buffered_pos=False)
        
        self._consume("eod")
        return node


    def _prod_transform(self):
        self._consume("transform")

        if self._lookahead.token_type == "+" or self._lookahead.token_type == "-":
            token_type = self._lookahead.token_type
            token = self._consume(self._lookahead.token_type)
            name_node = IdentifierNode(token_type)
        else:
            name_node = self._prod_id()


        if self._lookahead.token_type == "rotate":
            return self._prod_transform_rotate(name_node)
        elif self._lookahead.token_type == "translate":
            return self._prod_transform_translate(name_node)
        else:
            self._syntax_error(f"Unexpected token '{self._lookahead.token_type}', expected transform type", buffered_pos=False)


    def _prod_transform_rotate(self, name_node):
        self._consume("rotate")
        value_node = self._prod_eval()

        unit_node = DegUnitNode()

        if self._lookahead.token_type == "deg":
            self._consume("deg")
        elif self._lookahead.token_type == "rad":
            self._consume("rad")
            unit_node = RadUnitNode()
        
        return RotateTransformNode(name_node, value_node, unit_node)


    def _prod_transform_translate(self, name_node):
        self._consume("translate")
        x_node = self._prod_eval()
        self._consume(",")
        y_node = self._prod_eval()

        return TranslateTransformNode(name_node, x_node, y_node)


    def _prod_length(self):
        self._consume("length")
        value_node = self._prod_eval()
        return LengthDeclarationNode(value_node)


    def _prod_iterate(self):
        self._consume("iterate")
        value_node = self._prod_eval()
        return IterateDeclarationNode(value_node)


    def _prod_axiom(self):
        self._consume("axiom")
        name_node = self._prod_id()
        return AxiomDeclarationNode(name_node)


    def _prod_var(self):
        token = self._consume("var")
        name_node = self._prod_id()
        self._consume("assign")
        value_node = self._prod_eval()
        return VarDeclarationNode(name_node, value_node)
    

    def _prod_rule(self):
        token = self._consume("rule")
        name_node = self._prod_id()

        rule_elements = []
        if self._lookahead.token_type == "assign":
            self._consume("assign")
            rule_elements = self._prod_rule_string()
            if len(rule_elements) == 0:
                self._syntax_error("Empty rule string")
        
        rule_node = RuleDeclarationNode(name_node, rule_elements)

        if self._lookahead.token_type == "bias":
            self._consume("bias")
            rule_node.rule_bias = self._prod_eval()

        return rule_node


    def _prod_rule_string(self):
        rule_elements = []
        while self._lookahead.token_type != "bias" and self._lookahead.token_type != "eod":
            next_node = None
            if self._lookahead.token_type == "id":
                next_node = self._prod_id()
            elif self._lookahead.token_type == "[":
                next_node = self._prod_push()
            elif self._lookahead.token_type == "]":
                next_node = self._prod_pop()
            elif self._lookahead.token_type == "+" or self._lookahead.token_type == "-":
                token_type = self._lookahead.token_type
                token = self._consume(self._lookahead.token_type)
                next_node = IdentifierNode(token_type)
            
            if next_node == None:
                self._syntax_error(f"Unexpected token type '{self._lookahead.token_type}")
            
            rule_elements.append(next_node)
        return rule_elements


    def _prod_push(self):
        token = self._consume("[")
        return PushNode()
    

    def _prod_pop(self):
        token = self._consume("]")
        return PopNode()


    def _prod_eval(self):
        # TODO expr, group
        lookahead_type = self._lookahead.token_type
        if lookahead_type == "num":
            return self._prod_num()
        elif lookahead_type == "id":
            id_node = self._prod_id()
            if self._lookahead.token_type == "(":
                return self._prod_function(id_node)
            else:
                return id_node
        else:
            self._syntax_error(f"Unexpected token: '{self._tokenizer.get_readable(lookahead_type)}', expected number or identifier")


    def _prod_function(self, name_node):
        self._consume("(")

        param_list = []

        param_list_ends = False
        while not param_list_ends:
            # as long as we don't see closing parentheses, we expect a list of eval's
            param_list.append(self._prod_eval())

            if self._lookahead.token_type == ")":
                param_list_ends = True
                self._consume(")")
            else:
                self._consume(",")
        
        return FunctionNode(name_node, param_list)


    def _prod_num(self):
        token = self._consume("num")
        return NumNode(float(token.value))
    
    
    def _prod_id(self, token_type="id"):
        token = self._consume(token_type)
        return IdentifierNode(token.value)