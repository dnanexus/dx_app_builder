#!/usr/bin/env python
# app_scatter

from __future__ import absolute_import, division, print_function, unicode_literals
import dxpy
import time
import json

@dxpy.entry_point('main')
def main(**job_inputs):
    # Process input arguments, some of which may be empty
    exec_id = job_inputs['exec_id']
    batch_inputs = job_inputs['batch_inputs']
    common_inputs = {}
    if 'common_inputs' in job_inputs:
        common_inputs = job_inputs['common_inputs']
    files = []
    if 'files' in job_inputs:
        files = job_inputs['files']
    instance_types = []
    if 'instance_types' in job_inputs:
        instance_types = job_inputs['instance_types']

    # Validate inputs
    # Get a link to the executable, make sure it is one of {app, applet, workflow}
    executable = None
    if exec_id.startswith("app-"):
        executable = dxpy.DXApp(exec_id)
    elif exec_id.startswith("applet-"):
        executable = dxpy.DXApplet(exec_id)
    elif exec_id.startswith("workflow-"):
        executable = dxpy.DXWorkflow(exec_id)
    if executable is None:
        raise Exception("Executable {} is not an app, applet, or workflow")

    # Get output specification
    output_spec = executable.describe()['outputSpec']
    print(output_spec)
    output_keys = []
    for d in output_spec:
        output_keys.append(d["name"])
    print("output_keys={}".format(output_keys))

    # validate batch arguments
    launch_arrays = {}
    width = None
    if not isinstance(batch_inputs, dict):
        raise Exception("batch_inputs is not a dictionary type")
    for key, arrValues in batch_inputs.iteritems():
        if not isinstance(arrValues, list):
            raise Exception("batch_inputs value {} is not a list type".format(arrValues))
        crnt_width = len(arrValues)
        if width is None:
            width = crnt_width
        else:
            if width != crnt_width:
                raise Exception("Input array sizes do not match {} width={} crnt_width={}"
                              .format(key, width, crnt_width))
        launch_arrays[key] = arrValues
    if not isinstance(common_inputs, dict):
        raise Exception("common_inputs is not a dictionary type")

    # validate files argument
    if not isinstance(files, list):
        raise Exception("files argument is not a list type")
    for f in files:
        if not isinstance(f, DXFile):
            raise Exception("{} is not a dx:file".format(f))

    # build dictionary for each invocation
    # TODO: What happens to null values?
    launch_dicts = []
    for i in range(0, width):
        args = {}
        for k, arrValues in launch_arrays.iteritems():
            args[k] = arrValues[i]
        for k, v in common_inputs.iteritems():
            args[k] = v
        launch_dicts.append(args)

    # At this point, we have an array of dictionaries, each one has the arugments
    # for one invocation
    jobs = []
    for d in launch_dicts:
        job = executable.run(d)
        jobs.append(job)

    # Collect arrays of JBORs
    outputs = {}
    for okey in output_keys:
        values = []
        for j in jobs:
            out_val  = j.get_output_ref(okey)
            values.append(out_val)
        outputs[okey] = values

    results = {
        'outputs': outputs,
        'launched': launch_dicts
    }
    return {'results': results}

dxpy.run()
