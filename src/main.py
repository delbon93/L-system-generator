import sys
import json
import dataclasses
import time
from math import floor
from lsys.parser import Parser
from lsys.interpreter import LSystemSpecification
from lsys.instance import LSystemInstance
from lsys.renderer import LSystemDebugPrintRenderer, LSystemSVGRenderer
from pprint import pprint, pformat

_start_time = None


def read_file(file_name):
    file_string = ""
    with open(file_name) as file:
        for line in file.readlines():
            file_string += line
    return file_string


def timer_start():
    global _start_time
    _start_time = time.time()


def timer_stop():
    global _start_time
    _stop_time = time.time()
    t = (_stop_time - _start_time) * 1000.0
    unit = "ms"
    if t < 1.0:
        unit = "ns"
        t *= 1000.0
    return f"{floor(t)}{unit}"


def main(argc, argv):
    file_name = argv[1]
    out_file_name = "out.svg"
    if argc > 2:
        out_file_name = argv[2]

    parser = Parser()
    print(f"Parsing source file '{file_name}'...", end="")
    timer_start()
    ast = parser.parse(read_file(file_name))
    print(f" ({timer_stop()})")
    # print("Parsing successful!")
    # print("Printing abstract syntax tree (AST):\n")
    # pprint(ast)

    print("Building L-system specification...", end="")
    timer_start()
    spec = LSystemSpecification.create(ast)
    print(f" ({timer_stop()})")
    # print("Printing L-system specification object:\n")
    # pprint(spec)

    print("Generating L-system instance...", end="")
    timer_start()
    instance = LSystemInstance(spec)
    # print(f"Axiom: {pformat(instance.l_string, compact=True)}")
    instance.iterate()
    # print(f"L-String after {instance._iteration_count} iterations:")
    # pprint(instance.l_string)
    print(f" ({timer_stop()})")

    print(f"Rendering to file '{out_file_name}'...", end="")
    timer_start()
    # renderer = LSystemDebugPrintRenderer()
    renderer = LSystemSVGRenderer(out_file_name)
    renderer.render(instance)
    print(f" ({timer_stop()})")
    print("All done.")


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)