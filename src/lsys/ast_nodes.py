from dataclasses import dataclass, field

class EvalContext:
    vars: dict
    funcs: dict


@dataclass
class ASTNode:
    pass


@dataclass
class RootNode(ASTNode):
    body: list[ASTNode]


@dataclass
class EvalNode(ASTNode):
    def eval(self, ctx: EvalContext):
        raise NotImplemented("Eval on abstract class should not be called!")


@dataclass
class NumNode(EvalNode):
    value: float

    def eval(self, ctx: EvalContext):
        return value


@dataclass
class IdentifierNode(EvalNode):
    ident: str

    def eval(self, ctx: EvalContext):
        if self.ident in ctx.vars.keys():
            return ctx.vars[self.ident]
        raise ValueError(f"No variable with name '{self.ident}' exists")


@dataclass
class FunctionNode(EvalNode):
    name: IdentifierNode
    param_list: list[EvalNode]

    def eval(self, ctx: EvalContext):
        if self.name in ctx.funcs.keys():
            return ctx.funcs[self.name](self.param_list)
        raise ValueError(f"No function with name '{self.name} exists")


@dataclass
class GroupNode(EvalNode):
    content: EvalNode

    def eval(self, ctx):
        return content.eval(ctx)


@dataclass
class OpNode(EvalNode):
    priority: int


@dataclass
class AddOpNode(OpNode):
    left_node: EvalNode
    right_node: EvalNode

    def eval(self, ctx):
        return self.left_node.eval(ctx) + self.right_node.eval(ctx)


@dataclass
class SubOpNode(OpNode):
    left_node: EvalNode
    right_node: EvalNode

    def eval(self, ctx):
        return self.left_node.eval(ctx) - self.right_node.eval(ctx)


@dataclass
class MulOpNode(OpNode):
    left_node: EvalNode
    right_node: EvalNode

    def eval(self, ctx):
        return self.left_node.eval(ctx) * self.right_node.eval(ctx)


@dataclass
class DivOpNode(OpNode):
    left_node: EvalNode
    right_node: EvalNode

    def eval(self, ctx):
        return self.left_node.eval(ctx) / self.right_node.eval(ctx)


@dataclass
class NegOpNode(OpNode):
    node: EvalNode

    def eval(self, ctx):
        return self.node.eval() * (-1)


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
    axiom: list[ASTNode]


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
