**This is a low-level app. Consider using \"dx build --app --remote\" instead, which calls this app internally.**

Builds your app from a .tar.gz File object.

The App Builder does the following:

* Unpacks the input tarball
* Builds with `./configure` and `make && make install` (optional; only run if a `./configure` file and a makefile are found, respectively)
* Uploads the resulting applet to DNAnexus and creates an app
