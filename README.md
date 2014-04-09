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

To try the boinc integration with LABAK's boinc server you first need the [mechanize](https://pypi.python.org/pypi/mechanize/) library for python.
File boincmechanized.by contains a small library for connecting to boinc administration server, 
where you need to edit the login function to provide your credentials.
Running "evolve --pModule=ObjectiveVectorTraitsBoinc" will start the the example with boinc integration.

Command
=======

./evolve  --pModule=ObjectiveVectorTraits --pAlgo=spea2 --mutEpsilon=0.1 --popSize=10 --maxGen=10 --pMut=1 --mutProb=0.01 --pCross=0.01 --crossProb=0.5
