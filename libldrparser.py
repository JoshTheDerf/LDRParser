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
        self.options.update(options)
        self.libraryLocation = libraryLocation
        self.modelFile = None
        self.__parts = {}
        self.__searchPaths = None

    @staticmethod
    def __locate(pattern, root=os.curdir):
        for path, dirs, files in os.walk(os.path.abspath(root)):
            for filename in fnmatch.filter(files, pattern):
                yield os.path.join(path, filename)

    @staticmethod
    def __convert(vals):
        for i in range(0, len(vals)):
            line = vals[i]
            # Floats
            if "." in line and "dat" not in line.lower():
                vals[i] = float(line)
            else:
                try:
                    # Integers
                    vals[i] = int(line)
                # Strings
                except ValueError:
                    pass
        return vals

    def __getSearchPaths(self):
        """Generate the search path for traversing the LDraw library.

        @return {List} A spec-compliant search path.
        """
        # Proper search order when looking for parts
        #  * Files relative to the main file
        #  * Models folder
        #  * Unofficial/parts
        #  * Unofficial/p/48 or Unofficial/p/8 (optional)
        #  * Unofficial/p
        #  * Parts folder
        #  * p/48 or p/8 folder (optional)
        #  * p folder
        paths = [
            os.path.join(os.path.dirname(os.path.abspath(self.modelFile))),
            os.path.join(self.libraryLocation, "models"),
            os.path.join(self.libraryLocation, "Unofficial", "parts"),
            os.path.join(self.libraryLocation, "Unofficial", "p"),
            os.path.join(self.libraryLocation, "parts"),
            os.path.join(self.libraryLocation, "p")
        ]

        return paths

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

        # Set the search paths if they have not already been set.
        if self.__searchPaths is None:
            self.__searchPaths = self.__getSearchPaths()

        # Display the line types we are going to skip parsing.
        if len(self.options["skip"]) > 0:
            self.log("Skip line type(s): {0}".format(
                     ", ".join(self.options["skip"])), 5)

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
        with open(filePath, "rt") as f:
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

            # Determine the control code
            code = self.ControlCodes[ctrl]

            # Always parse comments so we can get the part type
            comment = self.parseComment(line)
            if comment is not None and comment.startswith("!LDRAW_ORG"):
                definition["partType"] = self.getPartType(comment)

            # We are not skipping this line type.
            if code not in self.options["skip"]:

                # Include the comments.
                if code == "COMMENT":
                    if "comments" not in definition:
                        definition["comments"] = []

                    # Make sure there is a comment to add
                    if comment is not None:
                        definition["comments"].append(comment)

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

    def getPartType(self, line):
        return line.split()[1]

    def parsePart(self, line):
        myDef = {}
        splitLine = self.__convert(line.split())

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
                with open(filePath, "rt") as f:
                    self.__parts[myDef["partId"]] = \
                        self.buildPartData(f.read())

        return myDef

    def parseComment(self, comment):
        """Perform basic comment processing, including
        minor filtering and cleanup.

        @param {String} comment The comment to process.
        @return {!String} The cleaned comment, or None if it was filtered.
        """
        # Strip the prefix
        comment = comment.strip().lstrip("0 ")

        # Filter out META commands, blank lines, and comments
        # See http://www.ldraw.org/article/218/#meta
        lineFilter = ("", "STEP", "WRITE", "PRINT", "CLEAR", "PAUSE", "SAVE")
        if comment in lineFilter or comment.startswith("//"):
            return None
        return comment

    def parseLine(self, line):
        splitLine = self.__convert(line.split())
        myDef = {
            "color": splitLine[1],
            "pos1": (splitLine[2], splitLine[3], splitLine[4]),
            "pos2": (splitLine[5], splitLine[6], splitLine[7]),
        }
        return myDef

    def parseTri(self, line):
        splitLine = self.__convert(line.split())
        myDef = {
            "color": splitLine[1],
            "pos1": (splitLine[2], splitLine[3], splitLine[4]),
            "pos2": (splitLine[5], splitLine[6], splitLine[7]),
            "pos3": (splitLine[8], splitLine[9], splitLine[10]),
        }
        return myDef

    def parseQuad(self, line):
        splitLine = self.__convert(line.split())
        myDef = {
            "color": splitLine[1],
            "pos1": (splitLine[2], splitLine[3], splitLine[4]),
            "pos2": (splitLine[5], splitLine[6], splitLine[7]),
            "pos3": (splitLine[8], splitLine[9], splitLine[10]),
            "pos4": (splitLine[11], splitLine[12], splitLine[13]),
        }
        return myDef

    def parseOptLine(self, line):
        splitLine = self.__convert(line.split())
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

        # Try the current directory.
        if os.path.isfile(partPath):
            locatedFile = partPath

        # Revise the search path just a little bit
        # to append the current part name.
        paths = [os.path.join(path, partPath) for path in self.__searchPaths]

        # Now check the search path for the file.
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
