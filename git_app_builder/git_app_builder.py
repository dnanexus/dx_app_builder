import dxpy

sys.path.append('/opt/pythonlibs')
import app_builder

@dxpy.entry_point('main')
def main(repo_url, ref='master', credentials=None, recurse=False, publish=False, extra_flags=""):

    clone_dir = app_builder.clone_repository(repo_url, ref=ref, credentials=credentials)

    if recurse:
        for app_dir in app_builder.find_app_directories(clone_dir):
            app_builder.create_app(app_dir, publish=publish, extra_flags=extra_flags)
    else:
        app_builder.create_app(clone_dir, publish=publish, extra_flags=extra_flags)

    return {}


dxpy.run()
