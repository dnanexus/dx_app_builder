import dxpy
import shutil
import subprocess
import tempfile

def main():
    repo_url = job['input']['repo_url']
    ref = job['input']['ref']
    program_name = job['input']['program_name']
    # TODO: obtain credentials too and make sure git can read them somehow

    # TODO: pull build tools into worker environment

    print "Repo URL: %s" % (repo_url,)
    print "Ref name: %s" % (ref,)
    print "Program name: %s" % (program_name,)

    # Clone the repo and run dx_build_program on it.

    tempdir = tempfile.mkdtemp()
    print "Working in " + tempdir

    # TODO: protect against directory traversal with program_name
    # TODO: here or in worker environment, bypass SSH host key prompts
    os.chdir(tempdir)
    subprocess.check_call(['git', 'clone', repo_url, program_name])

    os.chdir(program_name)
    subprocess.check_call(['git', 'checkout', '-q', ref])

    os.chdir(tempdir)
    subprocess.check_call(['dx_build_program', '--overwrite', program_name])

    shutil.rmtree(tempdir)
