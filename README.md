paradiseo-python
================

A simple framework adding capability of using python for evaluation 
in multi-criteria evolutionary optimization of paradiseo framework.

Building
========
Building the binary was tested on Linux and Windows 7 with the help of [cygwin](http://www.cygwin.com/).

Requirements:
* make
* g++
* [paradiseo](http://paradiseo.gforge.inria.fr/) moeo and eo libraries and headers
* Python2.7 libraries and headers

Make file should be fairly self explanatory, although all the paths were hardcoded to point
to their respective locations when libraries were installed under cygwin.

Runing on windows
=================
The binary evolve.exe is included in the repository. 

To run it, installation of cygwin with working python2.7 is necessary.

Running
=======

Just running the evolve binary will load the example sch1 problem.
