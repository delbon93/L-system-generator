from dataclasses import dataclass, field

@dataclass
class ASTNode:
    pass


@dataclass
class RootNode(ASTNode):
    body: list[ASTNode]


@dataclass
class EvalNode(ASTNode):
    def eval(self):
        pass


@dataclass
class NumNode(EvalNode):
    value: float

    def eval(self):
        return value


@dataclass
class IdentifierNode(EvalNode):
    ident: str


@dataclass
class DeclarationNode(ASTNode):
    pass


@dataclass
class VarDeclarationNode(DeclarationNode):
    var_name: IdentifierNode
    var_value: EvalNode