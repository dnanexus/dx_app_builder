import dxpy
import json
import os
import shutil
import stat
import subprocess
import tempfile

def save_credentials(credentials):
    """
    Saves CREDENTIALS to disk in a place where git/SSH will be able to find it.

    CREDENTIALS may be a dictionary with any of the following keys: "id_rsa",
    "id_dsa", "id_ecdsa". If any are specified, the corresponding value should
    be a string. Its value will be written to the corresponding file under
    ~/.ssh.
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

    for id_type in ("id_rsa", "id_dsa", "id_ecdsa"):
        if id_type in credentials:
            id_filename = os.path.join(dot_ssh, id_type)
            print "Saving credentials %s => %s" % (id_type, id_filename)
            with open(id_filename, "w") as outfile:
                outfile.write(credentials[id_type].encode("utf8"))
            # Change mode to 0600, as is befitting for credentials.
            os.chmod(id_filename, stat.S_IRUSR | stat.S_IWUSR)


def main():
    repo_url = job['input']['repo_url']
    ref = job['input']['ref']
    program_name = job['input']['program_name']
    dest_project = None
    if 'destination_project' in job['input']:
        dest_project = job['input']['destination_project']
    credentials = None
    if 'credentials' in job['input']:
        credentials = json.loads(job['input']['credentials'])
    target_apiserver_host = None
    if 'target_apiserver_host' in job['input']:
        target_apiserver_host = job['input']['target_apiserver_host']
    target_apiserver_port = None
    if 'target_apiserver_port' in job['input']:
        target_apiserver_port = job['input']['target_apiserver_port']

    print "Repo URL: %s" % (repo_url,)
    print "Ref name: %s" % (ref,)
    print "Program name: %s" % (program_name,)
    print "Destination project: %s" % (dest_project,)
    if target_apiserver_host:
        print "Overriding API server host: %s" % (target_apiserver_host,)
    if target_apiserver_port:
        print "Overriding API server port: %d" % (target_apiserver_port,)

    if credentials:
        save_credentials(credentials)

    # Clone the repo and run dx_build_program on it.

    tempdir = tempfile.mkdtemp()
    print "Working in " + tempdir

    # TODO: protect against directory traversal with program_name
    os.chdir(tempdir)
    subprocess.check_call(['git', 'clone', repo_url, program_name])

    os.chdir(program_name)
    subprocess.check_call(['git', 'checkout', '-q', ref])

    # Load any build deps requested by the app.
    try:
        manifest = open('dxprogram')
    except IOError:
        manifest = open('dxprogram.json')
    try:
        parsed_manifest = json.load(manifest)
        # TODO: check that manifest.buildDepends is an array of hashes
        if 'buildDepends' in parsed_manifest:
            depends = [dep['name'] for dep in parsed_manifest['buildDepends']]
            print 'Installing the following packages specified in buildDepends: ' + ', '.join(depends)
            cmd = ['sudo', 'apt-get', 'install', '--yes'] + depends
            subprocess.check_call(cmd)
    finally:
        manifest.close()

    # Override the API server host and port if requested.
    env = dict(os.environ)
    if target_apiserver_host:
        env['DX_APISERVER_HOST'] = target_apiserver_host
    if target_apiserver_port:
        env['DX_APISERVER_PORT'] = target_apiserver_port

    os.chdir(tempdir)
    cmd = ['dx_build_program']
    if dest_project:
        cmd.extend(['-p', dest_project])
    cmd.extend(['--overwrite', program_name])
    subprocess.check_call(cmd, env=env)

    shutil.rmtree(tempdir)
