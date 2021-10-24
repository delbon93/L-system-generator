from dataclasses import dataclass, field

@dataclass
class ASTNode:
    pass


@dataclass
class RootNode(ASTNode):
    body: list[ASTNode]


@dataclass
class EvalNode(ASTNode):
    def eval(self, ctx):
        return None


@dataclass
class NumNode(EvalNode):
    value: float

    def eval(self, ctx):
        return value


@dataclass
class IdentifierNode(EvalNode):
    ident: str


@dataclass
class FunctionNode(EvalNode):
    name: IdentifierNode
    param_list: list[EvalNode]


@dataclass
class GroupNode(EvalNode):
    content: EvalNode


@dataclass
class DeclarationNode(ASTNode):
    pass


@dataclass
class VarDeclarationNode(DeclarationNode):
    var_name: IdentifierNode
    var_value: EvalNode


@dataclass
class RuleDeclarationNode(DeclarationNode):
    rule_name: IdentifierNode
    rule_elements: list[ASTNode]
    rule_bias: EvalNode = field(default=NumNode(1.0), init=False)


@dataclass
class PushNode(ASTNode):
    pass


@dataclass
class PopNode(ASTNode):
    pass


@dataclass
class AxiomDeclarationNode(DeclarationNode):
    axiom_name: IdentifierNode


@dataclass
class LengthDeclarationNode(DeclarationNode):
    length: EvalNode


@dataclass
class IterateDeclarationNode(DeclarationNode):
    iterations: EvalNode


@dataclass
class TransformDeclarationNode(DeclarationNode):
    transform_name: IdentifierNode


@dataclass
class UnitNode(ASTNode):
    pass


@dataclass
class DegUnitNode(UnitNode):
    pass


@dataclass
class RadUnitNode(UnitNode):
    pass


@dataclass
class RotateTransformNode(TransformDeclarationNode):
    angle: EvalNode
    unit: UnitNode

@dataclass
class TranslateTransformNode(TransformDeclarationNode):
    x: EvalNode
    y: EvalNode

