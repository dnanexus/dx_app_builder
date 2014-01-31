Builds your applet from a git repository.

The Applet Builder does the following:

* Clones your source from a git repo, optionally using credentials specified by you
* Builds with `./configure` and `make && make install` (optional; only run if a `./configure` file and a makefile are found, respectively)
* Uploads the resulting applet to DNAnexus
