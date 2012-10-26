import json
import os
import subprocess

def find_app_directories(root_dir):
    """
    Yields all directories beneath root_dir that contain a dxapp.json
    file.
    """
    for dirpath, dirnames, filenames in os.walk(root_dir, followlinks=False):
        if "dxapp.json" in filenames:
            yield dirpath

def create_app(app_dir, publish=False):

    os.chdir(app_dir)

    # Load any build deps requested by the app.
    with open('dxapp.json') as manifest:
        parsed_manifest = json.load(manifest)
        # TODO: check that manifest.buildDepends is an array of hashes
        if 'buildDepends' in parsed_manifest:
            depends = [dep['name'] for dep in parsed_manifest['buildDepends']]
            print 'Installing the following packages specified in buildDepends: ' + ', '.join(depends)
            cmd = ['sudo', 'apt-get', 'install', '--yes'] + depends
            subprocess.check_call(cmd)

    cmd = ['dx-build-app', '--no-temp-build-project']
    if publish:
        cmd.extend(['--publish'])
    cmd.extend(['.'])
    subprocess.check_call(cmd)
