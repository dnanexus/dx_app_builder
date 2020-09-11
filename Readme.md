Builder Apps
============

App(let) Builder Apps
---------------------

These apps take as input a reference to the source code for a DNAnexus app and
build an app or applet. These apps may be useful for developing apps if you
don't have an Ubuntu 14.04, or 16.04 machine easily accessible. (Also see the frontends
`dx build --app --remote` or `dx build --remote`, which tar up your working
directory and automatically invoke `tarball_app_builder` and
`tarball_applet_builder` respectively.)

There are four apps here, each with different I/O specs:

* `git_app_builder`: takes a string containing a git repository path; builds an
  app in an Ubuntu 14.04 environment
* `git_applet_builder`: takes a string containing a git repository path;
  returns an applet in an Ubuntu 14.04 environment
* `tarball_app_builder[_trusty or _xenial or _xenial_v1 or _focal]`: takes a reference to a tarball containing the code to
  be compiled; builds an app [in an Ubuntu 14.04, 16.04 version "0" or "1", or 20.04 environment]
* `tarball_applet_builder[_trusty or _xenial or _xenial_1 or _focal]`: takes a reference to a tarball containing the code
  to be compiled; returns an applet [in an Ubuntu 14.04, 16.04 version "0" or "1", or 20.04 environment]

More info: https://documentation.dnanexus.com/developer/apps

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

* `create_asset_precise`: builds an asset targeting Ubuntu 12.04 (deprecated)
* `create_asset_trusty`: builds an asset targeting Ubuntu 14.04
* `create_asset_xenial`: builds an asset targeting Ubuntu 16.04
* `create_asset_xenial_v1`: builds an asset targeting Ubuntu 16.04 version "1"
* `create_asset_focal`: builds an asset targeting Ubuntu 20.04

More info: https://documentation.dnanexus.com/developer/apps/dependency-management/asset-build-process
