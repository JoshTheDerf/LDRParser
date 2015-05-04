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

import os
import fnmatch


class LDRParser:
    version = ("0", "1", "0")
    ControlCodes = ("COMMENT", "SUBPART", "LINE", "TRI", "QUAD", "OPTLINE")

    def getCode(self, num):
        print(self.ControlCodes)

    libraryLocation = ""
    startFile = ""

    options = {
        "skip": [],
        "logLevel": 0
    }

    _parts = {}

    def __init__(self, libraryLocation, startFile, options={}):
        self.libraryLocation = libraryLocation
        self.startFile = startFile
        self.options.update(options)

    def fromLDR(self):
        if len(self.options["skip"]) > 0:
            self.log("Skip: {0}".format(", ".join(self.options["skip"])), 5)

        # This can load any valid file on the LDraw path
        # with the specified name, not just a full path.
        filePath = self.findFile(self.startFile)

        if filePath is None:
            self.log("Critical Error - File Not Found: {0}".format(filePath), 0)
            return None

        self.log("Reading Initial File: {0}".format(filePath), 3)
        f = open(filePath, 'r')
        root = self.buildPartData(f.read())
        root["parts"] = self._parts

        self.log("Completed Parsing File: {0}".format(filePath), 3)
        return root

    def buildPartData(self, ldrString):
        definition = {}
        lines = ldrString.splitlines()

        for line in lines:
            ctrl = int(line.lstrip()[0] if line.lstrip() else -1)
            if ctrl == -1:
                continue

            code = self.ControlCodes[int(ctrl)]

            if code not in self.options["skip"]:
                if code == "COMMENT":
                    if "comments" not in definition:
                        definition["comments"] = []
                    definition["comments"].append(self.parseComment(line))

                elif code == "SUBPART":
                    if "subparts" not in definition:
                        definition["subparts"] = []
                    definition["subparts"].append(self.parsePart(line))

                elif code == "LINE":
                    if "lines" not in definition:
                        definition["lines"] = []
                    definition["lines"].append(self.parseLine(line))

                elif code == "TRI":
                    if "tris" not in definition:
                        definition["tris"] = []
                    definition["tris"].append(self.parseTri(line))

                elif code == "QUAD":
                    if "quads" not in definition:
                        definition["quads"] = []
                    definition["quads"].append(self.parseQuad(line))

                elif code == "OPTLINE":
                    if "optlines" not in definition:
                        definition["optlines"] = []
                    definition["optlines"].append(self.parseQuad(line))

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

        if myDef["partId"] not in self._parts:
            filePath = self.findFile(myDef["partId"])

            if filePath is not None:
                self.log("Caching Part: "+self.findFile(myDef["partId"]), 4)
                f = open(filePath, 'r')
                self._parts[myDef["partId"]] = self.buildPartData(f.read())

        return myDef

    def parseComment(self, comment):
        return comment

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
        #   * Files relative to the main file
        #   * Models folder
        #   * Unofficial parts (parts and p subfolders)
        #   * Parts folder
        #   * p folder
        paths = [
            os.path.join(os.path.dirname(os.path.abspath(self.startFile)),
                         partPath),
            os.path.join(self.libraryLocation, "models", partPath),
            os.path.join(self.libraryLocation, "Unofficial", "parts",
                         partPath),
            os.path.join(self.libraryLocation, "Unofficial", "p", partPath),
            os.path.join(self.libraryLocation, "parts", partPath),
            os.path.join(self.libraryLocation, "p", partPath)
        ]

        for path in paths:
            if os.path.isfile(path):
                locatedFile = path
                break

        # Failing that, recursively search through every directory
        # in the library folder for the file.
        if not locatedFile:
            for file in locate(os.path.basename(partPath),
                               self.libraryLocation):
                locatedFile = file
                break

        # Try the current directory.
        if not locatedFile:
            if os.path.isfile(partPath):
                locatedFile = partPath

        if not locatedFile:
            self.log("Error: File not found: {0}".format(partPath), 1)

        return locatedFile

    def formatPartName(self, partName):
        return partName.lower().replace("\\", os.path.sep).replace("/", os.path.sep)

    def log(self, string, level=0):
        if self.options["logLevel"] >= level:
            print("[LDRParser] {0}".format(string))


def locate(pattern, root=os.curdir):
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)
