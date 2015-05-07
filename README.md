#LDRParser

A simple python (2.7+ and 3*) module for isolating and converting LDraw models into an
easily-convertable JSON or Python Dictionary-based format.

Currently does *not* support MPD files, but that may change in the future.

##Usage (Command Line)
Download `LDRParser.py` and `libldrparser.py` and place them in the same directory.

Run `python LDRParser.py` from the command line with the path to your ldraw library, the path to your .ldr file,
and any options you may like.

**Options:**

* `-s= [Comma-separated string. Values: COMMENT,SUBPART,LINE,TRI,QUAD,OPTLINE]` Line control codes to skip.
* `-m` Whether to minify the output (don't pretty-print it) or not.
* `-o=json [json|dict]` Output format: JSON or Python Dictionary.
* `-l=0 [0-5]` Logging Level. Log level 0 displays nothing other than the output, 5 is verbose.

**Full example:**
```
python LDRParser.py /home/tribex/Software/ldraw myModel.ldr -s=COMMENTS,LINE,OPTLINE -o=dict -m=true -l=5
```

Additionally, any file within (no matter what depth) the ldraw directory can be parsed simply be referencing its full name as if it was in the current directory.

##Usage (Python Module)
Download `libldrparser.py`.
From your project, import LDRParser from libldrparser (`from libldrparser import LDRParser`)

Create an instance of LDRParser, this allows the part cache to persist across multiple conversions for a model and greatly speeds up subsequent runs.
```python
parser = LDRParser("PATH/TO/LDRAW/LIBRARY", {
  # Options
  "skip": [],
  "logLevel": 0
})

# Do the actual conversion.
# Output is a python dictionary using the format described below.
output = parser.parse("PATH/TO/TARGET/MODEL")
```

##Format:
The examples below will be expressed as JSON for simplicity and readability.

The output contains all parts, sub-parts, and information necessarry for them to be fully rendered and parented. sub-parts are loaded only once, and then referenced by their parents as many times as needed, greatly reducing file size, though it can still be massive.

A basic file looks like this:
```javascript
{ // The root object is simply a part with no name and an object of all used subparts inside it as "parts".
  "parts": { // An object containing the definitions for all parts used anywhere in this file, indexed by file name.
    "stud3.dat": {
      "subparts": [
        {
          // The id of the part in the parts object.
          "partId": "4-4edge.dat"
          "color": "16", // Raw color from the LDR file.
          // Transformation martix for this sub-part.
          "matrix": [
            "4",
            "0",
            "0",
            "0",
            "0",
            "1",
            "0",
            "-4",
            "0",
            "0",
            "4",
            "0",
            0,
            0,
            0,
            1
          ],
        }
      ],
      // Defines a line from pos1 to pos2.
      "lines": [
        {
          "color": "16",
          "pos1": [
            "-1",
            "1",
            "1"
          ],
          "pos2": [
            "1",
            "1",
            "1"
          ],
        }
      ],
      // Defines a triangle. Vertices are pos1, pos2, and pos3.
      "tris": [
        {
          "color": "16",
          "pos1": [
            "-1",
            "1",
            "1"
          ],
          "pos2": [
            "1",
            "1",
            "1"
          ],
          "pos3": [
            "1",
            "1",
            "-1"
          ],
        },
      ],
      // Defines a quad. Vertices are pos1, pos2, pos3, and pos4.
      "quads": [
        {
          "color": "16",
          "pos1": [
            "-1",
            "1",
            "1"
          ],
          "pos2": [
            "1",
            "1",
            "1"
          ],
          "pos3": [
            "1",
            "1",
            "-1"
          ],
          "pos4": [
            "-1",
            "1",
            "-1"
          ]
        },
      ],
      // Defines a line which is only visible based on certain rules.
      // See http://www.ldraw.org/article/218.html,
      // line type 5. pos1 and 2 define the line vertices, ctl1 and 2 are the control points.
      "optlines": [
        {
          "color": "16",
          "pos1": [
            "-1",
            "1",
            "1"
          ],
          "pos2": [
            "1",
            "1",
            "1"
          ],
          "ctl1": [
            "1",
            "1",
            "-1"
          ],
          "ctl2": [
            "-1",
            "1",
            "-1"
          ]
        },
      ],

    },
  },
  "subparts": [
    {
      "color": "3",
      "partId": "stud3.dat",
      "matrix": [
        "4",
        "0",
        "0",
        "0",
        "0",
        "1",
        "0",
        "-4",
        "0",
        "0",
        "4",
        "0",
        0,
        0,
        0,
        1
      ]
    }
  ]
}
```

##TODO:
 * Support for mpd files.
 * Support for various encodings.
 * Support for part metas and comment processing.
 * Document the code
 * Conversion back to LDR files.
 * Flattening of format, so that the only things stored are those necessary for drawing. (Vertices, Indices, and Colors, really.) Requires decent knowledge of Linear Algebra and 4x4 Matrices.

##License:
```
The MIT License (MIT)

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
```
