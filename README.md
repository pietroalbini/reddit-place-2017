# Archive of Reddit's r/place

This repository contains an archive of the artwork created by Reddit's
[r/place][rplace] between April 1st, 2017 and April 3rd, 2017. The repository
contains a binary diff of all the changes (with a resolution of 5 seconds), and
a Python script to extract the frames from the diff.

> There is an empty canvas.  
> You may place a tile upon it, but you must wait to place another.  
> Individually you can create something.  
> Together you can create something more.

The script is maintained by Pietro Albini and released under the MIT license.
Huge thanks to:

* All the people who joined r/place during the three days
* [u/mncke][umncke] for collecting all the data and [making it available][data]

## Obtaining the images from the diff

The script requires Python 3 and [pillow][pillow] installed. If you use Ubuntu
or Debian you can install all the dependencies with this command:

```
$ sudo apt install python3 python3-pillow
```

Then, after you cloned the repository, you can use the script to generate the
frames you want from the binary diff contained in the repo. Also, a Makefile is
provided for the most common operations:

```
Generate the final artwork:
$ make latest

Generate the history of the canvas with a 5 seconds resolution:
$ make all

Generate the history of the canvas with a 1 hour resolution:
$ make hourly
```

All the resulting files will be located in the `build/` directory. If you need
more control over what's built you should use directly the script.

## Usage of the script

The script requires the path to the binary diff (which can be either
uncompressed or gzipped) as the first argument, and then the action you want to
do.

If you only want to get the latest frame, you need to provide the `--latest`
flag:

```
$ python3 generate.py data/diff.gz --latest
```

If you want to get an history of the canvas, you can use the `--interval
SECONDS` with the number of seconds between the snapshots:

```
$ python3 generate.py data/diff.gz --interval 5  # Every 5 seconds
$ python3 generate.py data/diff.gz --interval 100  # Every 10 minutes
$ python3 generate.py data/diff.gz --interval 3600  # Every hour
```

If you need a snapshot at a specific timestamp instead, you can use the
`--timestamp TIMESTAMP` flag (or multiple ones if you need more timestamps):

```
$ python3 generate.py data/diff.gz --timestamp 1491001598
$ python3 generate.py data/diff.gz --timestamp 1491001598 --timestamp 1491134887
```

Also, the script supports some flags to customize its behavior. If you want the
images to be stored in a different directory you can use the `--output-dir`
flag:

```
$ python3 generate.py data/diff.gz --output-dir result/ --latest
```

You can also tell the script to output the images in a different format with
the `--format` flag (you can use all the formats supported by
[pillow][pillow]):

```
$ python3 generate.py data/diff.gz --format gif --latest
```

[rplace]: https://www.reddit.com/r/place
[umncke]: https://www.reddit.com/u/mncke
[data]: https://www.reddit.com/r/place/comments/6396u5/rplace_archive_update/
[pillow]: http://pillow.readthedocs.io
