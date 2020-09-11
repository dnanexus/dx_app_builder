# Copyright (C) 2016 DNAnexus, Inc.
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

import dxpy
import sys

sys.path.append('/opt/pythonlibs')
import app_builder_py3 as app_builder

@dxpy.entry_point('main')
def main(input_file, recurse=False, publish=False, build_options=None):

    unpack_dir = app_builder.unpack_tarball(input_file)

    if recurse:
        for app_dir in app_builder.find_app_directories(unpack_dir):
            app_builder.create_app(app_dir, publish=publish, build_options=build_options)
    else:
        app_builder.create_app(unpack_dir, publish=publish, build_options=build_options)

    return {}


dxpy.run()
