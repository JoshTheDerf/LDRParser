# LDRParser

A simple python (2.7+ and 3*) module for isolating and converting LDraw models into an
easily-convertible JSON or Python Dictionary-based format.

Currently has experimental support for MPD files.

**NOTE:** It would be great if someone could provide me some test files for MPD and BFC support, as I have a very limited set. Thanks!

## Usage (Command Line)
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

## Format:
The examples below will be expressed as JSON for simplicity and readability.

The output contains all parts, sub-parts, and information necessary for them to be fully rendered and parented. sub-parts are loaded only once, and then referenced by their parents as many times as needed, greatly reducing file size, though it can still be massive.

A basic file looks like this:
```javascript
{ // The root object is simply a part with no name and an object of all used subparts inside it as "parts".
  "parts": { // An object containing the definitions for all parts used anywhere in this file, indexed by file name.
    "stud3.dat": {
      // Any comments found in the file not deemed irrelevant.
      "comments": {
        "Stud Tube Solid",
        "Name: stud3.dat",
        "Author: James Jessiman",
        "!LDRAW_ORG Primitive UPDATE 2012-01",
        "!LICENSE Redistributable under CCAL version 2.0 : see CAreadme.txt",
        "BFC CERTIFY CCW",
        "!HISTORY 2002-04-04 [sbliss] Modified for BFC compliance",
        "!HISTORY 2002-04-25 [PTadmin] Official Update 2002-02",
        "!HISTORY 2007-06-24 [PTadmin] Header formatted for Contributor Agreement",
        "!HISTORY 2008-07-01 [PTadmin] Official Update 2008-01",
        "!HISTORY 2012-02-16 [Philo] Changed to CCW",
        "!HISTORY 2012-03-30 [PTadmin] Official Update 2012-01"
      },
      // The base winding information for this file. 0 = CCW, 1 = CW. Not present if there is no specified winding info, in which case CCW should be assumed.
      "bfc": 0,
      // The type of this part. (Primitive, Subpart, or Part)
      "partType": "Part",
      "subparts": [
        {
          // Bitmask (as Integer) representing the BFC values.
          // bit 0 = Winding. 0 if CCW, 1 if CW
          // bit 1 = Clip. 0 if clip is not specified or disabled, 1 if it is enabled.
          // bit 2 = Invertnext. 0 if invertnext is not specified, 1 if it is enabled.
          // All Together:
          // - 4 = 100 = Winding: CCW, Clip: disabled, Invertnext enabled.
          // - 3 = 011 = Winding: CW, Clip: enabled, Invertnext disabled.
          // - 1 = 001 = Winding: CW, Clip: disabled, Invertnext disabled.
          // - .. and so on. Most common values are 0, 4, and 1.
          "bfc": 0
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
          // Bitmask (as Integer) representing the BFC values.
          // bit 0 = Winding. 0 if CCW, 1 if CW
          // bit 1 = Clip. 0 if clip is not specified or disabled, 1 if it is enabled.
          // bit 2 = Invertnext. 0 if invertnext is not specified, 1 if it is enabled.
          // All Together:
          // - 4 = 100 = Winding: CCW, Clip: disabled, Invertnext enabled.
          // - 3 = 011 = Winding: CW, Clip: enabled, Invertnext disabled.
          // - 1 = 001 = Winding: CW, Clip: disabled, Invertnext disabled.
          // - .. and so on. Most common values are 0, 4, and 1.
          "bfc": 0
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
          // Bitmask (as Integer) representing the BFC values.
          // bit 0 = Winding. 0 if CCW, 1 if CW
          // bit 1 = Clip. 0 if clip is not specified or disabled, 1 if it is enabled.
          // bit 2 = Invertnext. 0 if invertnext is not specified, 1 if it is enabled.
          // All Together:
          // - 4 = 100 = Winding: CCW, Clip: disabled, Invertnext enabled.
          // - 3 = 011 = Winding: CW, Clip: enabled, Invertnext disabled.
          // - 1 = 001 = Winding: CW, Clip: disabled, Invertnext disabled.
          // - .. and so on. Most common values are 0, 4, and 1.
          "bfc": 0
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
          // Bitmask (as Integer) representing the BFC values.
          // bit 0 = Winding. 0 if CCW, 1 if CW
          // bit 1 = Clip. 0 if clip is not specified or disabled, 1 if it is enabled.
          // bit 2 = Invertnext. 0 if invertnext is not specified, 1 if it is enabled.
          // All Together:
          // - 4 = 100 = Winding: CCW, Clip: disabled, Invertnext enabled.
          // - 3 = 011 = Winding: CW, Clip: enabled, Invertnext disabled.
          // - 1 = 001 = Winding: CW, Clip: disabled, Invertnext disabled.
          // - .. and so on. Most common values are 0, 4, and 1.
          "bfc": 0
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
          // Bitmask (as Integer) representing the BFC values.
          // bit 0 = Winding. 0 if CCW, 1 if CW
          // bit 1 = Clip. 0 if clip is not specified or disabled, 1 if it is enabled.
          // bit 2 = Invertnext. 0 if invertnext is not specified, 1 if it is enabled.
          // All Together:
          // - 4 = 100 = Winding: CCW, Clip: disabled, Invertnext enabled.
          // - 3 = 011 = Winding: CW, Clip: enabled, Invertnext disabled.
          // - 1 = 001 = Winding: CW, Clip: disabled, Invertnext disabled.
          // - .. and so on. Most common values are 0, 4, and 1.
          "bfc": 0
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
      // Bitmask (as Integer) representing the BFC values.
      // bit 0 = Winding. 0 if CCW, 1 if CW
      // bit 1 = Clip. 0 if clip is not specified or disabled, 1 if it is enabled.
      // bit 2 = Invertnext. 0 if invertnext is not specified, 1 if it is enabled.
      // All Together:
      // - 4 = 100 = Winding: CCW, Clip: disabled, Invertnext enabled.
      // - 3 = 011 = Winding: CW, Clip: enabled, Invertnext disabled.
      // - 1 = 001 = Winding: CW, Clip: disabled, Invertnext disabled.
      // - .. and so on. Most common values are 0, 4, and 1.
      "bfc": 0
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

## TODO:
 * Support for part metas and comment processing.
 * Document the code
 * Conversion back to LDR files.
 * Flattening of format, so that the only things stored are those necessary for drawing. (Vertices, Indices, and Colors, really.) Requires decent knowledge of Linear Algebra and 4x4 Matrices.

## License:
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
