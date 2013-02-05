import dxpy
import sys

sys.path.append('/opt/pythonlibs')
import app_builder

@dxpy.entry_point('main')
def main(input_file, recurse=False, publish=False, extra_flags=""):

    unpack_dir = app_builder.unpack_tarball(input_file)

    if recurse:
        for app_dir in app_builder.find_app_directories(unpack_dir):
            app_builder.create_app(app_dir, publish=publish, extra_flags=extra_flags)
    else:
        app_builder.create_app(unpack_dir, publish=publish, extra_flags=extra_flags)

    return {}


dxpy.run()
