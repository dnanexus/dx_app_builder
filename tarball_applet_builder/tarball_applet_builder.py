import dxpy
import os
import subprocess
import sys
import tempfile

sys.path.append('/opt/pythonlibs')
import app_builder

@dxpy.entry_point('main')
def main(input_file, extra_flags=""):

    unpack_dir = app_builder.unpack_tarball(input_file)

    applet_id = app_builder.create_applet(unpack_dir, extra_flags=extra_flags)

    return { 'output_applet': dxpy.dxlink(applet_id) }

dxpy.run()
