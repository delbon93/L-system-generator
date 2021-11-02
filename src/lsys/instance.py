from .interpreter import *
from .ast_nodes import *
import math

class LSystemInstance:

    def __init__(self, spec: LSystemSpecification):
        self.spec: LSystemSpecification = spec
        self.l_string: list[ASTNode] = spec.axiom_node.axiom
        self.ctx: EvalContext = EvalContext()
        self._iteration_count: int = 0
    

    def iterate(self):
        self._iteration_count = 0
        max_iterations = math.floor(self.spec.iterate_node.iterations.eval(self.ctx))
        for _ in range(max_iterations):
            if not self._do_iteration():
                break
            else:
                self._iteration_count += 1
    

    def _do_iteration(self) -> bool:
        new_l_string = []
        some_rule_matched = False
        for node in self.l_string:
            if issubclass(type(node), IdentifierNode):
                rule_name = node.ident
                chosen_rule = self.spec.select_rule(rule_name, self.ctx)
                if chosen_rule != None:
                    some_rule_matched = True
                    new_l_string += chosen_rule.rule_elements
                else:
                    new_l_string.append(node)
            else:
                new_l_string.append(node)
        self.l_string = new_l_string
        return some_rule_matched
