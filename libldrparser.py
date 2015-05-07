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

import os
import fnmatch

__all__ = ("LDRParser")


class LDRParser:
    version = ("0", "1", "0")
    ControlCodes = ("COMMENT", "SUBPART", "LINE", "TRI", "QUAD", "OPTLINE")

    options = {
        "skip": [],
        "logLevel": 0
    }

    def __init__(self, libraryLocation, options={}):
        self.libraryLocation = libraryLocation
        self.modelFile = None
        self.__parts = {}
        self.options.update(options)

    @staticmethod
    def __locate(pattern, root=os.curdir):
        for path, dirs, files in os.walk(os.path.abspath(root)):
            for filename in fnmatch.filter(files, pattern):
                yield os.path.join(path, filename)

    def log(self, string, level=0):
        """Log debug messages to the console.

        @param {String} string The message to be displayed.
        @param {Number} level Specify the message verbosity level.
                              If the specified level is less than
                              or equal to the level given in the options,
                              the message will be printed.
        """
        if self.options["logLevel"] >= level:
            print("[LDRParser] {0}".format(string))

    def parse(self, modelFile):
        # Set the model to be read
        self.modelFile = modelFile

        # Display the line types we are going to skip parsing.
        if len(self.options["skip"]) > 0:
            self.log("Skip: {0}".format(", ".join(self.options["skip"])), 5)

        # This can load any valid file on the LDraw path
        # with the specified name, not just a full path.
        filePath = self.findFile(self.modelFile)

        # The file could not be found.
        if filePath is None:
            self.log("Critical Error - File Not Found: {0}".format(
                     self.modelFile), 0)
            return None

        # Begin parsing the model and all the parts.
        self.log("Reading Initial File: {0}".format(filePath), 3)
        with open(filePath, "r") as f:
            root = self.buildPartData(f.read())
        root["parts"] = self.__parts

        self.log("Completed Parsing File: {0}".format(filePath), 3)
        return root

    def buildPartData(self, ldrString):
        definition = {}
        lines = ldrString.splitlines()

        for line in lines:
            # Determine the type of line this is.
            ctrl = int(line.lstrip()[0] if line.lstrip() else -1)

            # Ignore invalid line types
            if ctrl == -1:
                continue

            # We are not skipping this line type.
            code = self.ControlCodes[ctrl]
            if code not in self.options["skip"]:

                # Parse the comments.
                if code == "COMMENT":
                    if "comments" not in definition:
                        definition["comments"] = []
                    definition["comments"].append(self.parseComment(line))

                # Parse the subparts.
                elif code == "SUBPART":
                    if "subparts" not in definition:
                        definition["subparts"] = []
                    definition["subparts"].append(self.parsePart(line))

                # Parse the straight lines.
                elif code == "LINE":
                    if "lines" not in definition:
                        definition["lines"] = []
                    definition["lines"].append(self.parseLine(line))

                # Parse the triangles.
                elif code == "TRI":
                    if "tris" not in definition:
                        definition["tris"] = []
                    definition["tris"].append(self.parseTri(line))

                # Parse the quadrilaterals.
                elif code == "QUAD":
                    if "quads" not in definition:
                        definition["quads"] = []
                    definition["quads"].append(self.parseQuad(line))

                # Parse the optional lines.
                elif code == "OPTLINE":
                    if "optlines" not in definition:
                        definition["optlines"] = []
                    definition["optlines"].append(self.parseOptLine(line))

        return definition

    def parsePart(self, line):
        myDef = {}
        splitLine = line.split()

        myDef["color"] = splitLine[1]
        myDef["matrix"] = (
            splitLine[5],  splitLine[6],  splitLine[7],  splitLine[2],
            splitLine[8],  splitLine[9],  splitLine[10], splitLine[3],
            splitLine[11], splitLine[12], splitLine[13], splitLine[4],
            0,             0,             0,             1,
        )
        myDef["partId"] = self.formatPartName(" ".join(splitLine[14:]))

        # The part is not in the cache.
        if myDef["partId"] not in self.__parts:
            filePath = self.findFile(myDef["partId"])

            # We have a file path.
            if filePath is not None:
                self.log("Caching Part: {0}".format(filePath), 4)

                # Read and cache the part contents.
                with open(filePath, "r") as f:
                    self.__parts[myDef["partId"]] = \
                        self.buildPartData(f.read())

        return myDef

    def parseComment(self, comment):
        return comment.lstrip("0 ")

    def parseLine(self, line):
        splitLine = line.split()
        myDef = {
            "color": splitLine[1],
            "pos1": (splitLine[2], splitLine[3], splitLine[4]),
            "pos2": (splitLine[5], splitLine[6], splitLine[7]),
        }
        return myDef

    def parseTri(self, line):
        splitLine = line.split()
        myDef = {
            "color": splitLine[1],
            "pos1": (splitLine[2], splitLine[3], splitLine[4]),
            "pos2": (splitLine[5], splitLine[6], splitLine[7]),
            "pos3": (splitLine[8], splitLine[9], splitLine[10]),
        }
        return myDef

    def parseQuad(self, line):
        splitLine = line.split()
        myDef = {
            "color": splitLine[1],
            "pos1": (splitLine[2], splitLine[3], splitLine[4]),
            "pos2": (splitLine[5], splitLine[6], splitLine[7]),
            "pos3": (splitLine[8], splitLine[9], splitLine[10]),
            "pos4": (splitLine[11], splitLine[12], splitLine[13]),
        }
        return myDef

    def parseOptLine(self, line):
        splitLine = line.split()
        myDef = {
            "color": splitLine[1],
            "pos1": (splitLine[2], splitLine[3], splitLine[4]),
            "pos2": (splitLine[5], splitLine[6], splitLine[7]),
            "ctl1": (splitLine[8], splitLine[9], splitLine[10]),
            "ctl2": (splitLine[11], splitLine[12], splitLine[13]),
        }
        return myDef

    def findFile(self, partPath):
        """Locate a part in the LDraw parts installation.

        @param {String} partPath The part name that needs to be located.
        @return {String} The full file path to the given part.
        """
        locatedFile = None

        # In the order we search:
        #  * Files relative to the main file
        #  * Models folder
        #  * Unofficial parts (parts and p subfolders)
        #  * Parts folder
        #  * p folder
        paths = [
            os.path.join(os.path.dirname(os.path.abspath(self.modelFile)),
                         partPath),
            os.path.join(self.libraryLocation, "models", partPath),
            os.path.join(self.libraryLocation, "Unofficial", "parts",
                         partPath),
            os.path.join(self.libraryLocation, "Unofficial", "p", partPath),
            os.path.join(self.libraryLocation, "parts", partPath),
            os.path.join(self.libraryLocation, "p", partPath)
        ]

        # Try the current directory.
        if os.path.isfile(partPath):
            locatedFile = partPath

        # Now lets check the list of paths we built earlier.
        if not locatedFile:
            for path in paths:
                if os.path.isfile(path):
                    locatedFile = path
                    break

        # Failing that, recursively search through every directory
        # in the library folder for the file.
        if not locatedFile:
            for f in self.__locate(os.path.basename(partPath),
                                   self.libraryLocation):
                locatedFile = f
                break

        # We are totally unable to find that part.
        if not locatedFile:
            self.log("Error: File not found: {0}".format(partPath), 1)

        return locatedFile

    def formatPartName(self, partName):
        """Clean up any path seperators
        to be consistent with the platform
        and convert the file name to lowercase.

        @param {String} The part path to clean up.
        @return {String}
        """
        return partName.lower().replace("\\",
                                        os.path.sep).replace("/",
                                                             os.path.sep)
