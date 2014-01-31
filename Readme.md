App(let) Builder Apps
=====================

The apps in this repository take as input a reference to the source code for a
DNAnexus app and build an app or applet. These apps may be useful for
developing apps if you don't have an Ubuntu 12.04 machine easily accessible.
(Also see the frontends ``dx build --app --remote`` or ``dx build --remote``,
which tar up your working directory and automatically invoke
``tarball_app_builder`` and ``tarball_applet_builder`` respectively.)

There are four apps here, each with different I/O specs:

* Two apps take a reference to a tarball containing the code to be compiled,
  and two apps take a string containing a git repository path (and optionally,
  a reference to a file object containing a private key to authenticate to the
  remote repository).
* Two apps produce an app as output and two apps produce an applet as output.
