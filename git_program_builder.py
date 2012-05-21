import dxpy
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
    credentials = None
    if job['input']['credentials']:
        credentials = json.loads(job['input']['credentials'])

    # TODO: pull build tools into worker environment

    print "Repo URL: %s" % (repo_url,)
    print "Ref name: %s" % (ref,)
    print "Program name: %s" % (program_name,)

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

    os.chdir(tempdir)
    subprocess.check_call(['dx_build_program', '--overwrite', program_name])

    shutil.rmtree(tempdir)
