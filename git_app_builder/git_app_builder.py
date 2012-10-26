import dxpy
import os
import stat
import subprocess
import sys
import tempfile

sys.path.append('/opt/pythonlibs')
import app_builder

def ssh_id_filename():
    # TODO: ensure .ssh exists (currently this is done below)
    return os.path.join(os.path.expanduser("~/.ssh"), "incubator_ssh_id")

def save_credentials(credentials):
    """
    Saves credentials file to disk in a place where git/SSH will be able to
    find it.
    """
    # TODO: ignore keys that are not among those we explicitly recognize.
    dot_ssh = os.path.expanduser("~/.ssh")

    try:
        os.mkdir(dot_ssh)
    except:
        pass

    # TODO: preload known_hosts entry for github.com and maybe others
    with open(os.path.join(dot_ssh, "config"), "w") as outfile:
        outfile.write("StrictHostKeyChecking no")

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
        ssh_wrapper_outfile.write("#!/bin/sh\nssh -i" + ssh_id_filename() + " -oIdentitiesonly=yes \"$@\"\n")
    os.chmod(ssh_wrapper_filename, stat.S_IRUSR | stat.S_IXUSR)

    checkout_dir = os.path.join(tempdir, "clonedest")
    os.mkdir(checkout_dir)
    os.chdir(checkout_dir)
    override_env = dict(os.environ)
    if credentials:
        override_env['GIT_SSH'] = ssh_wrapper_filename
    subprocess.check_call(['git', 'clone', repo_url, 'userapp'], env=override_env)

    os.chdir('userapp')
    subprocess.check_call(['git', 'checkout', '-q', ref])
    subprocess.check_call(['git', 'submodule', 'update', '--init'])

    return os.path.join(checkout_dir, 'userapp')

@dxpy.entry_point('main')
def main(repo_url, ref='master', credentials=None, publish=False):

    clone_dir = clone_repository(repo_url, ref=ref, credentials=credentials)
    for app_dir in app_builder.find_app_directories(clone_dir):
        app_builder.create_app(app_dir, publish=publish)

    return {}


dxpy.run()
