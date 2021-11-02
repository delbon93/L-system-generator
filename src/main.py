import sys
import json
import dataclasses
from lsys.parser import Parser
from lsys.interpreter import LSystemSpecification
from lsys.instance import LSystemInstance
from pprint import pprint, pformat


def read_file(file_name):
    file_string = ""
    with open(file_name) as file:
        for line in file.readlines():
            file_string += line
    return file_string


def main(argc, argv):
    file_name = argv[1]

    parser = Parser()
    print(f"Parsing file '{file_name}'...")
    ast = parser.parse(read_file(file_name))
    print("Parsing successful!")
    # print("Printing abstract syntax tree (AST):\n")
    # pprint(ast)

    spec = LSystemSpecification.create(ast)
    # print("Printing L-system specification object:\n")
    # pprint(spec)

    instance = LSystemInstance(spec)
    print(f"Axiom: {pformat(instance.l_string, compact=True)}")
    instance.iterate()
    print(f"L-String after {instance._iteration_count} iterations:")
    pprint(instance.l_string)


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)