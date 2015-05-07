#!/usr/bin/python

"""Simple LDraw Model Parser.

Copyright (c) 2015 Tribex

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

from __future__ import print_function

import sys
import json
import pprint

from libldrparser import LDRParser

if __name__ == '__main__':

    def printHelp():
        print("""\n[LDRParser {0}]
Usage: ldrparser.py PATH/TO/LDRAW/LIBRARY PATH/TO/FILE/FOR/PARSING [options]"""
              .format(".".join(LDRParser.version)))
        print("\nOptions:")
        print("""  -s= [Comma-separated string. Values:
       {0}] Line control codes to skip.""".format(
              ",".join(LDRParser.ControlCodes)))
        print("  -l=0 [0-5] Log Level")
        print("  -o=dict [dict, json] Format to output")
        print("  -m Minify output")
        print("  -h, --help Show this help text.")

    if len(sys.argv) < 3:
        printHelp()
        sys.exit(0)

    options = {
        "skip": [],
        "logLevel": 0,
        "output": "json",
        "minify": False,
    }

    for arg in sys.argv:
        if "-s=" in arg:
            options["skip"] = arg[3:].upper().split(",")
        elif "-l=" in arg:
            options["logLevel"] = int(arg[3:])
        elif "-o=" in arg:
            options["output"] = arg[3:].lower()
        elif "-m" in arg:
            options["minify"] = True
        elif "-h" in arg or "--help" in arg:
            printHelp()
            sys.exit(0)

    parser = LDRParser(sys.argv[1], options)
    out = parser.parse(sys.argv[2])

    if options["output"] == "dict":
        if options["minify"]:
            print(out)
        else:
            pp = pprint.PrettyPrinter(indent=2)
            pp.pprint(out)
    else:
        if options["minify"]:
            print(json.dumps(out))
        else:
            print(json.dumps(out, sort_keys=True, indent=2))
