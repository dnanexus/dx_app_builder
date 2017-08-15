# Copyright (C) 2013 DNAnexus, Inc.
#
# This file is part of dx_app_builder.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may not
#   use this file except in compliance with the License. You may obtain a copy
#   of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import json
import os
import stat
import subprocess
import sys
import tempfile

import dxpy
from dxpy.scripts import dx_build_app

# === git ===

def ssh_id_filename():
    # TODO: ensure .ssh exists (currently this is done below)
    return os.path.join(os.path.expanduser("~/.ssh"), "incubator_ssh_id")

def save_credentials(credentials):
    """
    Saves credentials file to disk in a place where git/SSH will be able to
    find it.
    """
    dot_ssh = os.path.expanduser("~/.ssh")

    try:
        os.mkdir(dot_ssh)
    except:
        pass

    id_filename = ssh_id_filename()
    print "Saving credentials to %s" % (id_filename)
    dxpy.download_dxfile(credentials, id_filename)
    # Change mode to 0600, as is befitting for credentials.
    os.chmod(id_filename, stat.S_IRUSR | stat.S_IWUSR)

def clone_repository(repo_url, ref='master', credentials=None):
    """
    Clones the specified repository (including all submodules) and
    returns a string containing the location of the newly cloned repo.
    """

    # TODO: are submodules cloned recursively?
    # TODO: allow specifying multiple credentials for submodules

    print "Repo URL: %s" % (repo_url,)
    print "Ref name: %s" % (ref,)

    if credentials:
        save_credentials(credentials)

    # Clone the repo and run dx-build-app on it.

    tempdir = tempfile.mkdtemp()
    print "Working in " + tempdir

    # Make an SSH wrapper that will make SSH use the provided key (and no
    # other).
    ssh_wrapper_filename = os.path.join(tempdir, 'ssh_wrapper')
    with open(ssh_wrapper_filename, 'w') as ssh_wrapper_outfile:
        ssh_wrapper_outfile.write("#!/bin/sh\nssh")
        if credentials:
            ssh_wrapper_outfile.write(" -i" + ssh_id_filename())
        ssh_wrapper_outfile.write(" -oIdentitiesonly=yes -oStrictHostKeyChecking=no \"$@\"\n")
    os.chmod(ssh_wrapper_filename, stat.S_IRUSR | stat.S_IXUSR)
    # TODO: preload known_hosts entry for github.com and maybe others,
    # or allow user to supply host signature for additional security

    checkout_dir = os.path.join(tempdir, "clonedest")
    os.mkdir(checkout_dir)
    os.chdir(checkout_dir)
    override_env = dict(os.environ)
    override_env['GIT_SSH'] = ssh_wrapper_filename
    subprocess.check_call(['git', 'clone', repo_url, 'userapp'], env=override_env)

    os.chdir('userapp')
    subprocess.check_call(['git', 'checkout', '-q', ref])
    subprocess.check_call(['git', 'submodule', 'update', '--init'])

    return os.path.join(checkout_dir, 'userapp')

# === tarball ===

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

    subprocess.check_call(['tar', '-xzf', tarball_filename, '--no-same-owner', '-C', checkout_dir, '--warning=no-timestamp'])

    # TODO: instead of guessing the directory name to be a name that
    # generates no warnings, have the client send the directory name
    # that was used on its end.
    try:
        appname = json.load(open(os.path.join(tempdir, "unpackdest", "dxapp.json"))).get("name", "unpackdest")
        if appname != "unpackdest":
            os.rename(os.path.join(tempdir, "unpackdest"), os.path.join(tempdir, appname))
            checkout_dir = os.path.join(tempdir, appname)
    except:
        pass

    return checkout_dir

# === general app build ===

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

def install_app_depends(app_dir):

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

def create_app(app_dir, publish=False, build_options=None):
    """
    Runs dx-build-app on the specified directory.
    """
    os.chdir(app_dir)
    install_app_depends(app_dir)

    if not build_options:
        build_options = {}

    dx_build_app.build_and_upload_locally('.', mode='app', use_temp_build_project=False, publish=publish, **build_options)

def create_applet(app_dir, build_options=None):
    """
    Runs dx-build-applet on the specified directory.
    """
    os.chdir(app_dir)
    install_app_depends(app_dir)

    if not build_options:
        build_options = {}

    output = dx_build_app.build_and_upload_locally('.', mode='applet', return_object_dump=True, **build_options)
    return output['id']
