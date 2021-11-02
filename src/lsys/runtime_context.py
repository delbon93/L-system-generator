from dataclasses import dataclass
from .ast_nodes import *
import math

class EvalContext:
    vars: dict
    funcs: dict

    @classmethod
    def create(cls):
        ctx = EvalContext()
        ctx.vars = {
            "pi": NumNode(math.pi),
            "e": NumNode(math.e)
        }
        ctx.funcs = {
            
        }
        return ctx


@dataclass
class TurtleState:
    x: float
    y: float
    heading: float