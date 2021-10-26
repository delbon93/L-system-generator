import sys
import json
import dataclasses
from lsys.parser import Parser
from pprint import pprint

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

    print("Parsing successful! Printing abstract syntax tree (AST):\n")
    pprint(ast)
    # print(json.dumps(dataclasses.asdict(ast), indent="  "))


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)