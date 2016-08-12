# Copyright (C) 2016 DNAnexus, Inc.
#
# This file is part of dx_asset_builder.
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

import os
from os import path
import subprocess
from subprocess import PIPE
import tempfile
import random
import time
import json
import sys
import re
import dxpy
from dxpy.utils.exec_utils import DXExecDependencyInstaller


def install_run_spec(exec_depends):
    run_spec = {"runSpec": {"execDepends": exec_depends}}
    job_desc = dxpy.get_handler(dxpy.JOB_ID).describe()
    dx_installer = DXExecDependencyInstaller(run_spec, job_desc)
    dx_installer.install()


def get_file_list(output_file, resources_to_ignore):
    """
    This method find all the files in the system and writes it to the output file
    """
    tmp_dir = path.dirname(output_file) + "*"
    skipped_paths = ["/proc*", tmp_dir, "/run*", "/boot*", "/home/dnanexus*", "/sys*"]
    cmd = ["sudo", "find", "/"]
    for ignore_dir in (skipped_paths + resources_to_ignore):
        cmd.extend(["-not", "-path", ignore_dir])

    env = os.environ.copy()
    env['LC_ALL'] = 'C'
    ps_pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    ps_file = subprocess.Popen(["sort"], stdin=ps_pipe.stdout, stdout=PIPE, env=env)

    with open(output_file, "w") as bfile:
        for line in ps_file.stdout:
            sp_code = ps_file.poll()
            file_name = line.rstrip()
            if file_name == "":
                if sp_code is not None:
                    break
                else:
                    continue
            if file_name == "/":
                continue
            try:
                mtime = str(os.path.getmtime(file_name))
            except OSError as os_err:
                print os_err
                mtime = ''
            # file_name should not have special characters
            # TODO escape the file name
            bfile.write(file_name + "\t" + str(mtime) + '\n')
    ps_file.stdout.close()


def get_file_diffs(first_file, second_file, diff_file):
    """ Get difference between two txt files and write the difference to the
    third file.
    """
    cmd = ["sudo", "comm", "-13", first_file, second_file]
    ps_pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    with open(diff_file, "w") as bfile:
        for line in ps_pipe.stdout:
            line = line.rstrip()
            file_name = '\t'.join(line.split('\t')[:-1])
            bfile.write(file_name + '\n')
            print(file_name)
    ps_pipe.stdout.close()


def get_system_snapshot(output_file_path, ignore_files):
    sys_tmp_dir = tempfile.gettempdir()
    tmp_file_name = "file_" + str(random.randint(0, 1000000)) + "_" + str(int(time.time() * 1000)) + ".txt"
    tmp_file_path = os.path.join(tempfile.gettempdir(), tmp_file_name)
    get_file_list(tmp_file_path, ignore_files)
    with open(output_file_path, 'w') as output_file_handle:
        proc = subprocess.Popen(['sort', tmp_file_path], stdout=output_file_handle)
        proc.communicate()


def build_asset(conf_json_fh, asset_makefile_fh, custom_asset_fh):
    conf_json_fh = dxpy.DXFile(conf_json_fh)

    if asset_makefile_fh is not None:
        asset_makefile_fh = dxpy.DXFile(asset_makefile_fh)
    if custom_asset_fh is not None:
        custom_asset_fh = dxpy.DXFile(custom_asset_fh)

    asset_conffile_path = "assetLib.json"
    custom_assetfile_path = "asset-dl.tar.gz"
    asset_makefile_path = "Makefile"

    dxpy.download_dxfile(conf_json_fh, asset_conffile_path)

    if asset_makefile_fh is not None:
        dxpy.download_dxfile(asset_makefile_fh, asset_makefile_path)
    if custom_asset_fh is not None:
        dxpy.download_dxfile(custom_asset_fh, custom_assetfile_path)

    with open(asset_conffile_path) as asset:
        conf_data = json.load(asset)

    # get list of directories in resources to ignore
    ignore_dir = conf_data.get("excludeResource", [])

    before_file_path_sort = tempfile.gettempdir() + '/before-sorted.txt'
    print >> sys.stderr, "Preparing the list of files in the system before installing any library."
    get_system_snapshot(before_file_path_sort, ignore_dir)

    if custom_asset_fh is not None:
        print >> sys.stderr, "Installing custom resources given by the user in the tarball."
        subprocess.call(["sudo", "tar", "-xzf", custom_assetfile_path, "-C", "/"])

    if "execDepends" in conf_data:
        print >> sys.stderr, "Installing execDepends."
        install_run_spec(conf_data['execDepends'])

    if asset_makefile_fh is not None:
        print >> sys.stderr, "Running make."
        mk_cmd = ["sudo", "make", "-C", os.getcwd()]
        subprocess.check_output(mk_cmd)

    after_file_path_sort = tempfile.gettempdir() + '/after-sorted.txt'
    print >> sys.stderr, "Preparing the list of files in the system after installing user libraries."
    get_system_snapshot(after_file_path_sort, ignore_dir)

    diff_file_path = tempfile.gettempdir() + "/diff.txt"
    print >> sys.stderr, "Preparing the list of new and updated files after the installation."
    get_file_diffs(before_file_path_sort, after_file_path_sort, diff_file_path)

    # TODO: temporary fix for dx-unpack not tokenizing its command line
    # correctly, resulting in being unable to extract filenames with whitespace
    # in them
    tar_output = re.sub(r"\s+", '-', conf_data["name"]) + ".tar.gz"
    print >> sys.stderr, "Creating the tarball '" + tar_output + "' of files listed in: " + diff_file_path
    tar_cmd = ["tar", "-Pcz", "--no-recursion", "-T", diff_file_path, "-f", "-"]

    tar_ps = subprocess.Popen(tar_cmd, stdout=subprocess.PIPE)
    upload_ps = subprocess.Popen(["dx", "upload", "-", "--wait", "--brief", "-o", tar_output,
                                  "--visibility", "hidden"],
                                  stdin=tar_ps.stdout, stdout=subprocess.PIPE)
    tar_ps.stdout.close()
    asset_tarball_id = upload_ps.communicate()[0].rstrip()
    tar_ps.wait()
    upload_ps.stdout.close()

    # Create a record object referring to this hidden file
    record_name = conf_data["name"]
    record_details = {"archiveFileId": {"$dnanexus_link": asset_tarball_id}}
    record_properties = {
                          "title": conf_data["title"],
                          "description": conf_data["description"],
                          "version": conf_data["version"],
                          "distribution": conf_data["distribution"],
                          "release": conf_data["release"]
                        }
    asset_bundle = dxpy.new_dxrecord(name=record_name,
                                     types=["AssetBundle"], details=record_details,
                                     properties=record_properties, close=True)

    # Add a property called {"AssetBundle": record-xxx} to the hidden tarball
    asset_file = dxpy.DXFile(asset_tarball_id)
    asset_file.set_properties({"AssetBundle": asset_bundle.get_id()})

    print >> sys.stderr, "\n'" + record_name + "' asset bundle created!\n"

    output = {}
    output["asset_bundle"] = dxpy.dxlink(asset_bundle)
    return output
