mcafterlife
===========

mcafterlife is a tool which allows the managment of a pool of [Minecraft](http://minecraft.net/)
servers, placing clients on the next server when they die, simulating "heaven".

Building
--------

The source is entirly python, although it is designed to be run from a python
zip archive. Running `build.py` should be enough to zip the source.

Running
-------

mcafterlife depends on python2.7. If it is available, tkinter is used to
provide a simple graphical user interface. The command line usage follows:

```
usage: mcafterlife.pyz [-h] [--motd MOTD] --java JAVA [--port PORT]
                       [--java-args JAVA_ARGS] [--last] [--jar JAR] [--colors]
                       [-n N] [--host HOST] [-v] [--keep] [--working WORKING]
                       [--nogui]

optional arguments:
  -h, --help            show this help message and exit
  --motd MOTD           motd to return with server list pings
                        default: 'An Afterlife Server'
  --java JAVA           location of java binary
  --port PORT           port to serve on
                        default: 25565
  --java-args JAVA_ARGS args to java
                        default: '-Xmx1024M -Xms1024M'
  --last                use the last valid settings
  --jar JAR             location of minecraft_server.jar
                        default: 'minecraft_server.jar'
  --colors              enable ansi terminal colors
  -n N                  max players (servers)
                        default: 10
  --host HOST           hostname to bind to
                        default: ''
  -v                    set level of verbose output
                        default: 3 (-vvv)
  --keep                keep servers after there is nobody left to play on
                        them
  --working WORKING     change working directory
  --nogui               do not try to launch a gui
```
