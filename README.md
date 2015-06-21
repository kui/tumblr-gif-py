tumblr-gif-py
================

GIF generator for the tumblr spec.


Requirement
-------------

* Python 2.7
* `avconv` : included on [libav][]
* `covert` : included on [ImageMagick][]

[ImageMagick]: http://www.imagemagick.org/
[libav]: http://libav.org/

On Ubuntu:

~~~~~~~~~~~~~~~~~~~~~~~~~sh
apt-get install libav-tools imagemagick
~~~~~~~~~~~~~~~~~~~~~~~~~


Usage
-----------

In terminal:

~~~~~~~~~~~~~~~~~~~~~~~~~sh
$ ./tumblr-gif frames /path/to/video.mp4 0:10:4 11 /tmp/a
# generate frame images from '0:10:4' for 11 secounds in /tmp/a
$ ./tumblr-gif gif /tmp/a/* a.gif
# generate /tmp/a.gif with frame images in /tmp/a
~~~~~~~~~~~~~~~~~~~~~~~~~
