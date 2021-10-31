from .ast_nodes import *
from dataclasses import dataclass, field
from functools import reduce
import pprint
import random


class LSystemSpecification:
    
    axiom: AxiomDeclarationNode = None
    length: LengthDeclarationNode = None
    iterate: IterateDeclarationNode = None

    transforms: list[TransformDeclarationNode] = []
    rules: list[RuleDeclarationNode] = []
    variables: list[VarDeclarationNode] = []


    @classmethod
    def _error(cls, msg: str):
        raise Exception(f"Interpreter Error: {msg}")


    @classmethod
    def create(cls, root: RootNode):
        spec = LSystemSpecification()
        error = LSystemSpecification._error
        transform_names = []
        variable_names = []

        for node in root.body:
            if issubclass(type(node), AxiomDeclarationNode):
                if spec.axiom != None:
                    error("Axiom declared more than once")
                spec.axiom = node
            elif issubclass(type(node), LengthDeclarationNode):
                if spec.length != None:
                    error("Length declared more than once")
                spec.length = node
            elif issubclass(type(node), IterateDeclarationNode):
                if spec.iterate != None:
                    error("Iterate declared more than once")
                spec.iterate = node
            
            elif issubclass(type(node), RuleDeclarationNode):
                spec.rules.append(node)
            
            elif issubclass(type(node), TransformDeclarationNode):
                if node.transform_name in transform_names:
                    error(f"Redeclaration of transform '{node.transform_name.ident}'")
                spec.transforms.append(node)
                transform_names.append(node.transform_name)
            elif issubclass(type(node), VarDeclarationNode):
                if node.var_name in variable_names:
                    error(f"Redeclaration of variable '{node.var_name.ident}'")
                spec.variables.append(node)
                variable_names.append(node.var_name)

        return spec
    
    def __repr__(self):
        string = ""
        string += "[AXIOM] " + pprint.pformat(self.axiom) + "\n"
        string += "[LENGTH] " + pprint.pformat(self.length) + "\n"
        string += "[ITERATE] " + pprint.pformat(self.iterate) + "\n"
        string += "[RULES] " + pprint.pformat(self.rules) + "\n"
        string += "[VARIABLES] " + pprint.pformat(self.variables) + "\n"
        string += "[TRANSFORMS] " + pprint.pformat(self.transforms) + "\n"
        return string



    def select_rule(self, rule_identifier: str, ctx: EvalContext) -> RuleDeclarationNode:
        rule_set = [rule for rule in self.rules if rule.rule_name.ident == rule_identifier]

        if len(rule_set) == 0:
            return None
        if len(rule_set) == 1:
            return rule_set[0]
        
        total_weight = reduce((lambda total, rule: total + rule.rule_bias.eval(ctx)), rule_set, 0.0)

        rng = random.random() * total_weight

        while rng > 0:
            last_rule = rule_set.pop(0)
            rng -= last_rule.rule_bias.eval(ctx)
            
        return last_rule
