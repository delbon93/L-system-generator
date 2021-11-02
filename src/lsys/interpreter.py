from .ast_nodes import *
from dataclasses import dataclass, field
from functools import reduce
import pprint
import random


class LSystemSpecification:
    
    axiom_node: AxiomDeclarationNode = None
    length_node: LengthDeclarationNode = None
    iterate_node: IterateDeclarationNode = None

    transform_nodes: list[TransformDeclarationNode] = []
    rule_nodes: list[RuleDeclarationNode] = []
    var_nodes: list[VarDeclarationNode] = []


    @classmethod
    def _error(cls, msg: str):
        raise Exception(f"Interpreter Error: {msg}")


    @classmethod
    def create(cls, root: RootNode):
        spec = LSystemSpecification()
        spec._create_defaults()
        error = LSystemSpecification._error
        variable_names = []

        iterate_declared = False
        length_declared = False

        for node in root.body:
            if issubclass(type(node), AxiomDeclarationNode):
                if spec.axiom_node != None:
                    error("Axiom declared more than once")
                spec.axiom_node = node
            elif issubclass(type(node), LengthDeclarationNode):
                if length_declared:
                    error("Length declared more than once")
                spec.length_node = node
                length_declared = True
            elif issubclass(type(node), IterateDeclarationNode):
                if iterate_declared:
                    error("Iterate declared more than once")
                spec.iterate_node = node
                iterate_declared = True
            
            elif issubclass(type(node), RuleDeclarationNode):
                spec.rule_nodes.append(node)
            
            elif issubclass(type(node), TransformDeclarationNode):
                # in case of redeclaration, remove existing transform
                spec.transform_nodes = [transform for transform in spec.transform_nodes if transform.transform_name.ident != node.transform_name.ident]
                spec.transform_nodes.append(node)

            elif issubclass(type(node), VarDeclarationNode):
                if node.var_name in variable_names:
                    error(f"Redeclaration of variable '{node.var_name.ident}'")
                spec.var_nodes.append(node)
                variable_names.append(node.var_name)

        return spec
    
    def __repr__(self):
        def ___list(list):
            string = ""
            for item in list:
                string += "\n\t\t" +  pprint.pformat(item) + "\n"
            return string
        
        string = "SPEC = {\n"
        string += "\tAXIOM {\n\t\t" + pprint.pformat(self.axiom_node) + "\n\t}\n\n"
        string += "\tLENGTH {\n\t\t" + pprint.pformat(self.length_node) + "\n\t}\n\n"
        string += "\tITERATE {\n\t\t" + pprint.pformat(self.iterate_node) + "\n\t}\n\n"
        string += "\tRULES {" + ___list(self.rule_nodes) + "\t}\n\n"
        string += "\tVARIABLES {" + ___list(self.var_nodes) + "\t}\n\n"
        string += "\tTRANSFORMS {" + ___list(self.transform_nodes) + "\t}\n"
        string += "}"
        return string


    def _create_defaults(self):
        self.transform_nodes.append(RotateTransformNode(IdentifierNode("+"), NumNode(90), DegUnitNode()))
        self.transform_nodes.append(RotateTransformNode(IdentifierNode("-"), NumNode(-90), DegUnitNode()))

        self.length_node = LengthDeclarationNode(NumNode(1.0))
        self.iterate_node = IterateDeclarationNode(NumNode(1.0))


    def select_rule(self, rule_identifier: str, ctx: EvalContext) -> RuleDeclarationNode:
        rule_set = [rule for rule in self.rule_nodes if rule.rule_name.ident == rule_identifier]

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
