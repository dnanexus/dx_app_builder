import dxpy

sys.path.append('/opt/pythonlibs')
import app_builder

@dxpy.entry_point('main')
def main(repo_url, ref='master', credentials=None, extra_flags=""):

    clone_dir = app_builder.clone_repository(repo_url, ref=ref, credentials=credentials)

    applet_id = app_builder.create_applet(clone_dir, extra_flags=extra_flags)

    return { 'output_applet': dxpy.dxlink(applet_id) }


dxpy.run()
