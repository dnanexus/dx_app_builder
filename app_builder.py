import json
import os
import shlex
import subprocess

def find_app_directories(root_dir):
    """
    Yields all directories beneath root_dir that contain a dxapp.json
    file.
    """
    for dirpath, dirnames, filenames in os.walk(root_dir, followlinks=False):
        if "dxapp.json" in filenames:
            yield dirpath

def package_atom(package_hash):
    if 'version' in package_hash:
        return package_hash['name'] + '=' + package_hash['version']
    else:
        return package_hash['name']

def create_app(app_dir, publish=False, extra_flags=""):

    os.chdir(app_dir)

    # Load any build deps requested by the app.
    with open('dxapp.json') as manifest:
        parsed_manifest = json.load(manifest)
        # TODO: check that manifest.buildDepends is an array of hashes

        # TODO: Remove support for dxapp.buildDepends, left here for
        # temporary compatibility
        if 'buildDepends' in parsed_manifest:
            parsed_manifest['runSpec'] = parsed_manifest.get('runSpec', {})
            if 'buildDepends' not in parsed_manifest['runSpec']:
                print >> sys.stderr, "* buildDepends is deprecated, please set runSpec.buildDepends instead."
                parsed_manifest['runSpec']['buildDepends'] = parsed_manifest['buildDepends']

        if 'runSpec' in parsed_manifest and 'buildDepends' in parsed_manifest['runSpec']:
            depends = [package_atom(dep) for dep in parsed_manifest['runSpec']['buildDepends']]
            print 'Installing the following packages specified in buildDepends: ' + ', '.join(depends)
            cmd = ['sudo', 'apt-get', 'install', '--yes'] + depends
            subprocess.check_call(cmd)

    cmd = ['dx-build-app', '--no-temp-build-project']
    if publish:
        cmd.extend(['--publish'])
    cmd.extend(shlex.split(extra_flags))
    cmd.extend(['.'])
    subprocess.check_call(cmd)
