from dataclasses import dataclass, field
from .runtime_context import TurtleState, EvalContext
import math


def _zerorize(value: float) -> float:
    """ forces values close to zero to be exactly zero """
    return 0.0 if abs(value) < 1e-10 else value


@dataclass
class ASTNode:
    pass


@dataclass
class RootNode(ASTNode):
    body: list[ASTNode]


@dataclass
class EvalNode(ASTNode):
    def eval(self, ctx: EvalContext):
        raise NotImplementedError("Eval on abstract class should not be called!")


@dataclass
class NumNode(EvalNode):
    value: float

    def eval(self, ctx: EvalContext):
        return self.value


@dataclass
class IdentifierNode(EvalNode):
    ident: str

    def eval(self, ctx: EvalContext):
        if self.ident in ctx.vars.keys():
            return ctx.vars[self.ident].eval(ctx)
        raise ValueError(f"No variable with name '{self.ident}' exists")


@dataclass
class FunctionNode(EvalNode):
    name: IdentifierNode
    param_list: list[EvalNode]

    def eval(self, ctx: EvalContext):
        if self.name.ident in ctx.funcs.keys():
            return ctx.funcs[self.name.ident]([param.eval(ctx) for param in self.param_list])
        raise ValueError(f"No function with name '{self.name} exists")


@dataclass
class GroupNode(EvalNode):
    content: EvalNode

    def eval(self, ctx):
        return self.content.eval(ctx)


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
        return self.node.eval(ctx) * (-1)


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

    def apply(self, turtle_state: TurtleState) -> TurtleState:
        raise NotImplementedError()


@dataclass
class UnitNode(ASTNode):
    pass


@dataclass
class DegUnitNode(UnitNode):
    def convert(self, value):
        return _zerorize((value / 360.0) * 2.0 * math.pi)


@dataclass
class RadUnitNode(UnitNode):
    def convert(self, value):
        return value


@dataclass
class RotateTransformNode(TransformDeclarationNode):
    angle: EvalNode
    unit: UnitNode

    def apply(self, turtle_state: TurtleState, ctx: EvalContext) -> TurtleState:
        angle = self.unit.convert(self.angle.eval(ctx))
        return TurtleState(turtle_state.x, turtle_state.y, _zerorize(turtle_state.heading + angle))


@dataclass
class AbsTranslateTransformNode(TransformDeclarationNode):
    x: EvalNode
    y: EvalNode

    def apply(self, turtle_state: TurtleState, ctx: EvalContext) -> TurtleState:
        x = _zerorize(turtle_state.x + self.x.eval(ctx))
        y = _zerorize(turtle_state.y + self.y.eval(ctx))
        return TurtleState(x, y, turtle_state.heading)


@dataclass
class ForwardTranslateTransformNode(TransformDeclarationNode):
    dist: EvalNode

    def apply(self, turtle_state: TurtleState, ctx: EvalContext) -> TurtleState:
        d = self.dist.eval(ctx)
        dx = d * math.cos(turtle_state.heading)
        dy = d * math.sin(turtle_state.heading)
        x = _zerorize(turtle_state.x + dx)
        y = _zerorize(turtle_state.y + dy)
        return TurtleState(x, y, turtle_state.heading)
