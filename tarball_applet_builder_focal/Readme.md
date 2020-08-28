**This is a low-level app. Consider using "dx build --remote" instead, which calls this app internally.**

Builds your applet from a .tar.gz File object on an Ubuntu 20.04 version environment

The Applet Builder does the following:

* Unpacks the input tarball
* Builds with `./configure` and `make && make install` (optional; only run if a `./configure` file and a makefile are found, respectively)
* Uploads the resulting applet to DNAnexus
