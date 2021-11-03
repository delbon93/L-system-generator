from .tokenizer import *
from .ast_nodes import *

# Lookup table for operator priority
_OPERATOR_PRIORITY = {
    TokenType.PLUS: 0,
    TokenType.MINUS: 0,
    TokenType.ASTERISK: 1,
    TokenType.SLASH: 1,
}

class Parser:
    """ Recursive descent parser for L-System grammar """
    
    def __init__(self):
        self._tokenizer = Tokenizer()


    def parse(self, string):
        """ Takes a source string and parses it, returning the root node of
            the generated abstract syntax tree """
        self._tokenizer.initialize(string)
        self._lookahead = self._tokenizer.get_next_token()
        return self._prod_root()
    

    def _is_next(self, token_type: TokenType) -> bool:
        """ Checks if the current lookahead token is of a specific token type """
        return self._lookahead.token_type == token_type
    

    def _is_next_any(self, token_types: list[TokenType]) -> bool:
        """ Checks if the current lookahead token is one of the specified token types """
        return self._lookahead.token_type in token_types


    def _is_next_op(self) -> bool:
        """ Checks if the current lookahead token is an operator """
        return self._lookahead.token_type in _OPERATOR_PRIORITY.keys()
    
    def _syntax_error(self, message, raise_as_exception=True, buffered_pos=True):
        """ Raises an exception when the parser encounters a syntax error in the source """
        line, col = self._tokenizer.get_pos(buffered=buffered_pos)
        printed_msg = f"[{line}:{col}] {message}\n{self._tokenizer.get_error_excerpt(use_buffered_pos=buffered_pos)}"
        if raise_as_exception:
            raise SyntaxError(printed_msg)
        else:
            print(printed_msg)


    def _consume(self, expected_token_type: TokenType, optional=False) -> RawToken:
        """ Consumes a token of the specified token type. If another token type is encountered
            a syntax error is raised (if the optional flag is set, None is returned instead) """
        return self._consume_any([expected_token_type], optional=optional)
    

    def _consume_any(self, expected_token_types: list[TokenType], optional=False) -> RawToken:
        """ Consumes a token of one of the specified token types. If an unspecified token type is encountered
            a syntax error is raised (if the optional flag is set, None is returned instead) """
        token = self._lookahead

        if token.token_type == TokenType.EOF:
            if optional:
                return None
            else:
                self._syntax_error(f"Unexpected end of input, expected '{str(expected_token_type)}'")
        
        if token.token_type in expected_token_types:
            self._lookahead = self._tokenizer.get_next_token()
            return token
        elif optional:
            return None
        else:
            self._syntax_error(f"Unexpected token '{str(token.token_type)}', expected: '{str(expected_token_types)}'")


    def _prod_root(self):
        """ Production rule: root node """
        nodes = []
        while self._lookahead != TokenType.EOF:
            nodes.append(self._prod_decl())
        return RootNode(nodes)
    

    def _prod_decl(self):
        """ Producion rule: declaration node """
        token_type = self._lookahead.token_type
        node = None
        if token_type == TokenType.VAR:
            node = self._prod_var()
        elif token_type == TokenType.RULE:
            node = self._prod_rule()
        elif token_type == TokenType.AXIOM:
            node = self._prod_axiom()
        elif token_type == TokenType.LENGTH:
            node = self._prod_length()
        elif token_type == TokenType.WIDTH:
            node = self._prod_width()
        elif token_type == TokenType.COLOR:
            node = self._prod_color_decl()
        elif token_type == TokenType.ITERATE:
            node = self._prod_iterate()
        elif token_type == TokenType.TRANSFORM:
            node = self._prod_transform()
        else:
            self._syntax_error(f"Unknown token '{str(token_type)}', expected declaration", buffered_pos=False)
        
        self._consume(TokenType.SEMICOLON)
        return node


    def _prod_transform(self):
        """ Production rule: transform node """
        self._consume(TokenType.TRANSFORM)

        # special case for '+' or '-' as transform names, otherwise invalid identifiers
        plus_or_minus_token = self._consume_any([TokenType.PLUS, TokenType.MINUS], optional=True)
        if plus_or_minus_token != None:
            name_node = IdentifierNode(plus_or_minus_token.value)
        else:
            name_node = self._prod_id()

        if self._is_next(TokenType.ROTATE):
            return self._prod_transform_rotate(name_node)
        elif self._is_next(TokenType.TRANSLATE):
            return self._prod_transform_translate(name_node)
        else:
            self._syntax_error(f"Unexpected token '{str(self._lookahead.token_type)}', expected transform type", buffered_pos=False)


    def _prod_color_decl(self):
        self._consume(TokenType.COLOR)
        color = self._prod_color()
        return ColorDeclarationNode(color)


    def _prod_transform_rotate(self, name_node):
        """ Production rule: rotation transform node """
        self._consume(TokenType.ROTATE)
        value_node = self._prod_eval()

        # degrees is implied default unit
        unit_node = DegUnitNode()

        if self._is_next(TokenType.DEG):
            self._consume(TokenType.DEG)
        elif self._is_next(TokenType.RAD):
            self._consume(TokenType.RAD)
            unit_node = RadUnitNode()
        
        return RotateTransformNode(name_node, value_node, unit_node)


    def _prod_transform_translate(self, name_node):
        """ Production rule: translation transform node """
        self._consume(TokenType.TRANSLATE)
        x_node = self._prod_eval()
        y_node = None
        width = NumNode(1.0)
        color = ColorNode()

        # one parameter -> forward translation
        # two parameters -> absolute translation
        if self._consume(TokenType.COMMA, optional=True) != None:
            y_node = self._prod_eval()

        if self._consume(TokenType.WIDTH, optional=True) != None:
            width = self._prod_eval()

        if self._consume(TokenType.COLOR, optional=True) != None:
            color = self._prod_color()

        if y_node == None:
            return ForwardTranslateTransformNode(name_node, x_node, width, color)
        else:
            return AbsTranslateTransformNode(name_node, x_node, y_node, width, color)


    def _prod_color(self):
        red = self._prod_eval()
        if self._consume(TokenType.COMMA, optional=True) != None:
            # expecting more color values
            green = self._prod_eval()
            self._consume(TokenType.COMMA)
            blue = self._prod_eval()
            return RGBColorNode(red, green, blue)
        else:
            # only grayscale was provided
            return RGBColorNode(red, red, red)


    def _prod_length(self):
        """ Production rule: length node """
        self._consume(TokenType.LENGTH)
        value_node = self._prod_eval()
        return LengthDeclarationNode(value_node)
        

    def _prod_width(self):
        """ Production rule: width node """
        self._consume(TokenType.WIDTH)
        value_node = self._prod_eval()
        return WidthDeclarationNode(value_node)


    def _prod_iterate(self):
        """ Production rule: iterate node """
        self._consume(TokenType.ITERATE)
        value_node = self._prod_eval()
        return IterateDeclarationNode(value_node)


    def _prod_axiom(self):
        """ Production rule: axiom node """
        self._consume(TokenType.AXIOM)
        return AxiomDeclarationNode(self._prod_rule_string())


    def _prod_var(self):
        """ Production rule: variable declaration node """
        token = self._consume(TokenType.VAR)
        name_node = self._prod_id()
        self._consume(TokenType.ASSIGN)
        value_node = self._prod_eval()
        return VarDeclarationNode(name_node, value_node)
    

    def _prod_rule(self):
        """ Production rule: rule node """
        token = self._consume(TokenType.RULE)
        name_node = self._prod_id()

        rule_elements = []

        if self._consume(TokenType.ASSIGN, optional=True) != None:
            rule_elements = self._prod_rule_string()
            if len(rule_elements) == 0:
                self._syntax_error("Empty rule string")
        
        rule_node = RuleDeclarationNode(name_node, rule_elements)

        if self._consume(TokenType.BIAS, optional=True):
            rule_node.rule_bias = self._prod_eval()

        return rule_node


    def _prod_rule_string(self):
        """ Production rule: rule string """
        rule_elements = []
        while not self._is_next_any([TokenType.BIAS, TokenType.SEMICOLON]):
            next_node = None
            if self._is_next(TokenType.IDENTIFIER):
                next_node = self._prod_id()
            elif self._is_next(TokenType.OPEN_BRACKET):
                next_node = self._prod_push()
            elif self._is_next(TokenType.CLOSE_BRACKET):
                next_node = self._prod_pop()
            elif self._is_next(TokenType.PLUS) or self._is_next(TokenType.MINUS):
                next_token = self._consume_any([TokenType.PLUS, TokenType.MINUS])
                next_node = IdentifierNode(next_token.value)
            
            if next_node == None:
                self._syntax_error(f"Unexpected token type '{str(self._lookahead.token_type)}")
            
            rule_elements.append(next_node)
        return rule_elements


    def _prod_push(self):
        """ Production rule: rule string push operator """
        self._consume(TokenType.OPEN_BRACKET)
        return PushNode()
    

    def _prod_pop(self):
        """ Production rule: rule string pop operator """
        self._consume(TokenType.CLOSE_BRACKET)
        return PopNode()


    def _prod_eval(self, op_mode=False):
        """ Production rule: generic evaluated node """
        lookahead_type = self._lookahead.token_type
        node = None

        if self._is_next(TokenType.NUM): # numbers
            node = self._prod_num()
        elif self._is_next(TokenType.IDENTIFIER): # identifiers (eg. var names)
            id_node = self._prod_id()
            if self._is_next(TokenType.OPEN_PAREN): # parentheses after id -> function
                node = self._prod_function(id_node)
            else:
                node = id_node
        elif self._is_next(TokenType.OPEN_PAREN): # bracket term (aka group)
            node = self._prod_group()
        elif self._is_next(TokenType.MINUS): # negated value
            node = self._prod_neg_eval()
        
        if node == None:
            self._syntax_error(f"Unexpected token: '{str(lookahead_type)}', expected value")

        # if next token is operator, node is part of a math expression
        if not op_mode and self._is_next_op():
            node = self._prod_expr(node)
        
        return node


    def _prod_neg_eval(self):
        """ Production rule: negation eval node """
        self._consume(TokenType.MINUS)
        return NegOpNode(10, self._prod_eval())


    def _prod_expr(self, start_node):
        """ Production rule: math expression eval node """
        # start with first left sided operand
        stack = [start_node]
        
        # continue as long as we encounter further operators
        while self._is_next_op():
            # consume operator and right sided operand and put it on the stack
            op_token_type = self._lookahead.token_type
            self._consume(op_token_type)
            stack.append(op_token_type)
            stack.append(self._prod_eval(op_mode=True)) # op mode to avoid recursively calling _prod_expr()

            # if another operator is coming up, check if it has higher priority.
            # if it has not, produce operations down the stack until the operation on top
            # of the stack has equal or lower priority than the upcoming operator (or stack has
            # no more operations)
            if self._is_next_op():
                next_op_priority = _OPERATOR_PRIORITY[self._lookahead.token_type]
                while len(stack) > 2 and next_op_priority < _OPERATOR_PRIORITY[stack[-2]]:
                    right_node = stack.pop()
                    op = stack.pop()
                    left_node = stack.pop()
                    stack.append(self._make_op(op, left_node, right_node))
        
        # no more operators encountered -> produce remaining operations on stack
        while len(stack) > 1:
            right_node = stack.pop()
            op = stack.pop()
            left_node = stack.pop()
            stack.append(self._make_op(op, left_node, right_node))
        
        # stack now only has one node, with all the other operation nodes under it
        return stack[0]

    
    def _make_op(self, op_type, left_node, right_node):
        """ Creates an operator node depending on the operation type """
        if op_type == TokenType.PLUS:
            return AddOpNode(0, left_node, right_node)
        elif op_type == TokenType.MINUS:
            return SubOpNode(0, left_node, right_node)
        elif op_type == TokenType.ASTERISK:
            return MulOpNode(1, left_node, right_node)
        elif op_type == TokenType.SLASH:
            return DivOpNode(1, left_node, right_node)
        else:
            raise Exception(f"Parser: Unsupported operator '{str(op_type)}'")


    def _prod_group(self):
        """ Production rule: bracket term node """
        self._consume(TokenType.OPEN_PAREN)
        content_node = self._prod_eval()
        self._consume(TokenType.CLOSE_PAREN)
        return GroupNode(content_node)


    def _prod_function(self, name_node):
        """ Production rule: function call node """
        self._consume(TokenType.OPEN_PAREN)

        param_list = []

        param_list_ends = False
        if self._consume(TokenType.CLOSE_PAREN, optional=True) != None:
                param_list_ends = True

        while not param_list_ends:
            # as long as we don't see closing parentheses, we expect a list of eval nodes
            param_list.append(self._prod_eval())

            if self._consume(TokenType.CLOSE_PAREN, optional=True) != None:
                param_list_ends = True
            else:
                self._consume(TokenType.COMMA)
        
        return FunctionNode(name_node, param_list)


    def _prod_num(self):
        """ Production rule: number node """
        token = self._consume(TokenType.NUM)
        return NumNode(float(token.value))
    
    
    def _prod_id(self, token_type=TokenType.IDENTIFIER):
        """ Production rule: identifier node """
        token = self._consume(token_type)
        return IdentifierNode(token.value)
