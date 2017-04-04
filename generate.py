#!/usr/bin/env python3
# Copyright (c) 2017  Pietro Albini <pietro@pietroalbini.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import gzip
import os
import struct

from PIL import Image, ImageDraw


def hexify(color):
    """Return a PIL color tuple from an hex color"""
    return tuple(int(color[i:i+2], base=16) for i in (0, 2, 4))


COLORS = {
    0:  hexify("ffffff"),
    1:  hexify("e4e4e4"),
    2:  hexify("888888"),
    3:  hexify("222222"),
    4:  hexify("ffa7d1"),
    5:  hexify("e50000"),
    6:  hexify("e59500"),
    7:  hexify("a06a42"),
    8:  hexify("e5d900"),
    9:  hexify("94e044"),
    10: hexify("02be01"),
    11: hexify("00d3dd"),
    12: hexify("0083c7"),
    13: hexify("0000ea"),
    14: hexify("cf6ee4"),
    15: hexify("820080"),
}


BLACKLISTED_TIMESTAMPS = [
    # This is the first frame, which is just blank
    1490986860,
]


class BaseCanvas:
    """Code shared by both FastLoadCanvas and FastSaveCanvas"""

    def __init__(self):
        self._pixels = [[0 for i in range(1000)] for i in range(1000)]

    def set(self, x, y, color):
        """Set a new pixel"""
        self._pixels[x][y] = color


class FastLoadCanvas(BaseCanvas):
    """Canvas optimized for only a few saves"""

    def save(self, dest):
        """Convert the canvas to a .png file"""
        img = Image.new("RGB", (1000, 1000))

        for x, pixels in enumerate(self._pixels):
            for y, color in enumerate(pixels):
                img.putpixel((x, y), COLORS[color])

        img.save(dest)


class FastSaveCanvas(BaseCanvas):
    """Canvas optimized for saving every frame"""

    def __init__(self):
        super().__init__()

        self._image = Image.new("RGB", (1000, 1000))

        draw = ImageDraw.Draw(self._image)
        draw.rectangle([(0, 0), (999, 999)], fill=COLORS[0])
        del draw

    def set(self, x, y, color):
        """Set a pixel"""
        super().set(x, y, color)

        self._image.putpixel((x, y), COLORS[color])

    def save(self, dest):
        """Convert the canvas to a .png file"""
        self._image.save(dest)


def load_diff(path, canvas):
    """An iterator which loads the diff and yields every timestamp"""
    if path.endswith(".gz"):
        f = gzip.open(path, "rb")
    else:
        f = open(path, "rb")

    latest_timestamp = None
    while True:
        bytes = f.read(16)
        if bytes == b"":
            break

        timestamp, x, y, color = struct.unpack("<IIII", bytes)
        canvas.set(x, y, color)

        if timestamp in BLACKLISTED_TIMESTAMPS:
            continue

        if timestamp != latest_timestamp:
            latest_timestamp = timestamp
            yield latest_timestamp


def main():
    """CLI entry point for the program"""
    parser = argparse.ArgumentParser()
    parser.add_argument("diff", help="The binary diff from abra.me")
    parser.add_argument("-o", "--output-dir", default=".", dest="output",
                        help="The directory to place the output to "
                             "(defaults to .)")
    parser.add_argument("-f", "--format", default="png",
                        help="The image format you want to use"
                             "(defaults to PNG)")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--interval", type=int,
                       help="The interval of the frames to save")
    group.add_argument("--timestamp", action="append", type=int,
                       dest="timestamps",
                       help="The timestamp you want to save")
    group.add_argument("--latest", action="store_true",
                       help="Return only the latest frame")

    args = parser.parse_args()

    # Make sure the output directory exists
    os.makedirs(args.output, exist_ok=True)

    if args.latest:
        canvas = FastLoadCanvas()

        for timestamp in load_diff(args.diff, canvas):
            continue

        path = "%s/latest.%s" % (args.output, args.format)
        print("Storing %s" % path)
        canvas.save(path)

    if args.timestamps is not None:
        canvas = FastLoadCanvas()

        missing_timestamps = args.timestamps[:]
        for timestamp in load_diff(args.diff, canvas):
            # Filter out unwanted frames
            if timestamp not in missing_timestamps:
                continue
            missing_timestamps.remove(timestamp)

            path = "%s/%s.%s" % (args.output, timestamp, args.format)
            print("Storing %s" % path)
            canvas.save(path)

            # Got all the needed frames
            if not missing_timestamps:
                break

        for timestamp in missing_timestamps:
            print("Timestamp not found: %s" % timestamp)

    if args.interval is not None:
        canvas = FastSaveCanvas()

        latest_timestamp = -args.interval
        for timestamp in load_diff(args.diff, canvas):
            # Filter out unwanted frames
            if timestamp < (latest_timestamp + args.interval):
                continue
            latest_timestamp = timestamp

            path = "%s/%s.%s" % (args.output, timestamp, args.format)
            print("Storing %s" % path)
            canvas.save(path)


if __name__ == "__main__":
    main()
