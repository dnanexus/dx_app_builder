Builder Apps
============

App(let) Builder Apps
---------------------

These apps take as input a reference to the source code for a DNAnexus app and
build an app or applet. These apps may be useful for developing apps if you
don't have an Ubuntu 12.04 or 14.04 machine easily accessible. (Also see the frontends
`dx build --app --remote` or `dx build --remote`, which tar up your working
directory and automatically invoke `tarball_app_builder` and
`tarball_applet_builder` respectively.)

There are four apps here, each with different I/O specs:

* `git_app_builder`: takes a string containing a git repository path; builds an
  app in an Ubuntu 14.04 environment
* `git_applet_builder`: takes a string containing a git repository path;
  returns an applet in an Ubuntu 14.04 environment
* `tarball_app_builder[_trusty]`: takes a reference to a tarball containing the code to
  be compiled; builds an app [in an Ubuntu 14.04 environment]
* `tarball_applet_builder[_trusty]`: takes a reference to a tarball containing the code
  to be compiled; returns an applet [in an Ubuntu 14.04 environment]

More info: http://wiki.dnanexus.com/Developer-Tutorials/App-Build-Process

Asset Builder Apps
------------------

These apps take as input the contents of an asset source directory and create
an asset. At a high level, an asset consists of a set of files (binaries,
libraries, or other resources) that are unpacked into an execution environment
at runtime and are available to the application code. An asset is created by
defining a build procedure to be run in a clean execution environment (which
typically downloads or creates some resources). The filesystem is snapshotted
before and after this process, and any files that were created or modified by
the build procedure are packed into the asset.

(See the frontend `dx build_asset`, which invokes these apps.)

* `create_asset_precise`: builds an asset targeting Ubuntu 12.04
* `create_asset_trusty`: builds an asset targeting Ubuntu 14.04

More info: https://wiki.dnanexus.com/Developer-Tutorials/Asset-Build-Process
