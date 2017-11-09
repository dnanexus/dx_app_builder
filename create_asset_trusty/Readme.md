**This is a low-level app. Consider using "dx build_asset" instead, which calls this app internally.**

# Create asset libraries (DNAnexus Platform App)

This applet creates bundled libraries based on the user inputs targeted to Ubuntu 14.04. It accepts 3 inputs:

* Mandatory: A json file in the following format

```
{
  "name": "asset_library_name",
  "title": "A human readable name",
  "description": " A detailed description about the asset",
  "version": "0.0.1",
  "release": "14.04",
  "distribution": "Ubuntu",
  "instanceType": "mem2_ssd1_x4",
  "excludeResource": ["/src/mycode.cpp","/src/scripts"],
  "execDepends": [
    {"name": "samtools", "package_manager": "apt"},
    {"name": "bamtools"},
    {"name": "bio", "package_manager": "gem", "version": "1.4.3"},
    {"name": "pysam","package_manager": "pip", "version": "0.7.4"},
    {"name": "Bio::SeqIO", "package_manager": "cpan", "version": "1.006924"}
  ]
}
```

* Optional: A Makefile that will be executed from the workers home directory before packaging and producing the final asset bundle.

* Optional: A tarball (tar.gz) file containing any custom resources required by the user. The tarball will be unarchived into the root of the execution environment's file system before packaging and producing the final asset bundle.
