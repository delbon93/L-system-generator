from .instance import LSystemInstance
from .ast_nodes import *
from .runtime_context import *
import svgwrite
import math


class LSystemRenderer:

    _turtle_stack: list[TurtleState]
    _ctx: EvalContext
    _depth: int


    def _push(self):
        self._turtle_stack.append(self._turtle_stack[-1].clone())
        self._depth += 1
        self._set_state_vars()
    

    def _pop(self):
        # TODO validate: stack must always have at least one state remaining
        self._turtle_stack.pop()
        self._depth -= 1
        self._set_state_vars()
    

    def _update(self, turtle_state: TurtleState):
        self._turtle_stack[-1] = turtle_state
        self._set_state_vars()
    

    def _state(self) -> TurtleState:
        return self._turtle_stack[-1]
    

    def _set_state_vars(self):
        self._ctx.vars["x"] = NumNode(self._state().x)
        self._ctx.vars["y"] = NumNode(self._state().y)
        self._ctx.vars["heading"] = NumNode(self._state().heading)
        self._ctx.vars["depth"] = NumNode(self._depth)

    
    def _apply_transform(self, transform_node: TransformDeclarationNode):
        self._complexity_rating += self._depth
        prev_state = self._state()
        self._update(transform_node.apply(prev_state, self._ctx))
        if issubclass(type(transform_node), ForwardTranslateTransformNode | AbsTranslateTransformNode):
            self._line(prev_state.x, prev_state.y, self._state().x, self._state().y)
            self._line_count += 1


    def render(self, instance: LSystemInstance):
        self._turtle_stack: list[TurtleState] = [TurtleState(0.0, 0.0, math.pi / 2.0)]
        self._ctx = EvalContext.create_from(instance.ctx)
        self._depth = 0
        self._complexity_rating = 0
        self._line_count = 0
        self._default_transform = ForwardTranslateTransformNode("?", instance.spec.length_node.length)
        self._set_state_vars()
        self._reset()

        for node in instance.l_string:
            if type(node) == PushNode:
                self._push()
            elif type(node) == PopNode:
                self._pop()
            elif type(node) == IdentifierNode:
                transform = instance.spec.get_transform(node.ident)
                if transform != None:
                    self._apply_transform(transform)
                else:
                    self._apply_transform(self._default_transform)
        
        self._finalize()

    ####################
    # Template Methods #
    ####################
    
    def _reset(self):
        pass

    
    def _line(self, x1, y1, x2, y2):
        raise Exception(f"Method '_line_' in class '{type(self).__name__}' must be overridden")

    
    def _finalize(self):
        pass


class LSystemDebugPrintRenderer(LSystemRenderer):

    def _line(self, x1, y1, x2, y2):
        print(f"({x1}, {y1}) --> ({x2}, {y2})")


class LSystemSVGRenderer(LSystemRenderer):
    
    def __init__(self, file_name: str):
        self._file_name = file_name


    def _reset(self):
        self._bounds = [0, 0, 0, 0]
        self._lines = []


    def _line(self, x1, y1, x2, y2):
        self._lines.append([x1, -y1, x2, -y2])
        self._bounds = [
            min(self._bounds[0], x1, x2), # lowest x value
            min(self._bounds[1], -y1, -y2), # lowest y value
            max(self._bounds[2], x1, x2), # highest x value
            max(self._bounds[3], -y1, -y2), # highest y value
        ]


    def _finalize(self):
        scale = 50
        line_width_factor = 40.0

        width = (self._bounds[2] - self._bounds[0]) * scale
        height = (self._bounds[3] - self._bounds[1]) * scale
        svg: svgwrite.Drawing = svgwrite.Drawing(self._file_name, size=(width, height))

        offset = (-self._bounds[0], -self._bounds[1])
        for line in self._lines:
            svg.add(
                svg.line(
                    ((line[0] + offset[0]) * scale, (line[1] + offset[1]) * scale), 
                    ((line[2] + offset[0]) * scale, (line[3] + offset[1]) * scale),
                    stroke=svgwrite.rgb(0, 0, 0),
                    stroke_width=scale/line_width_factor
                )
            )

        svg.save()

