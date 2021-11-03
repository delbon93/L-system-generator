from dataclasses import dataclass
import math
import random


def _param_count_error(name: str, expected: str, given: int):
    raise Exception(f"Function '{name}' takes {expected} parameter(s), but {given} were given")


def _ctx_random(params):
    if len(params) == 0:
        return random.random()
    elif len(params) == 1:
        return random.random() * params[0]
    elif len(params) == 2:
        return random.random() * (params[1] - params[0]) + params[0]
    _param_count_error("random", "up to two", len(params))


def _ctx_min(params):
    if len(params) > 0:
        return min(params)
    _param_count_error("min", "at least one", len(params))


def _ctx_max(params):
    if len(params) > 0:
        return max(params)
    _param_count_error("max", "at least one", len(params))


class EvalContext:
    vars: dict
    funcs: dict

    @classmethod
    def create(cls):
        ctx = EvalContext()

        ctx.funcs = {
            "random": _ctx_random,
            "min": _ctx_min,
            "max": _ctx_max,
        }

        return ctx
    

    @classmethod
    def create_from(cls, ctx):
        cpy = EvalContext()
        cpy.vars = dict(ctx.vars)
        cpy.funcs = dict(ctx.funcs)
        return cpy


@dataclass
class TurtleState:
    x: float
    y: float
    heading: float


    def clone(self):
        return TurtleState(self.x, self.y, self.heading)