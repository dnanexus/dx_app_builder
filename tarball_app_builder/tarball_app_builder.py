import dxpy
import os
import subprocess
import sys
import tempfile

sys.path.append('/opt/pythonlibs')
import app_builder

def unpack_tarball(input_tarball):
    """
    Unpacks the tarball with the specified file ID and returns a string
    containing the directory where it was unpacked.
    """

    tempdir = tempfile.mkdtemp()
    print "Working in " + tempdir

    tarball_filename = os.path.join(tempdir, "input.tar.gz")

    dxpy.download_dxfile(input_tarball, tarball_filename)

    checkout_dir = os.path.join(tempdir, "unpackdest")
    os.mkdir(checkout_dir)

    subprocess.check_call(['tar', '-xzf', tarball_filename, '-C', checkout_dir])

    return checkout_dir

@dxpy.entry_point('main')
def main(input_file, publish=False):

    unpack_dir = unpack_tarball(input_file)

    for app_dir in app_builder.find_app_directories(unpack_dir):
        app_builder.create_app(app_dir, publish=publish)

    return {}


dxpy.run()
