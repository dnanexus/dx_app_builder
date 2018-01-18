#!/usr/bin/env python
# app_scatter

from __future__ import absolute_import, division, print_function, unicode_literals
import dxpy
import time
import json

@dxpy.entry_point('main')
def main(**job_inputs):
    # Process input arguments, some of which may be empty
    executable_id = job_inputs['executable_id']
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
    if executable_id.startswith("app-"):
        executable = dxpy.DXApp("'" + executable_id + "'")
    elif executable_id.startswith("applet-"):
        executable = dxpy.DXApplet("'" + executable_id + "'")
    elif executable_id.startswith("workflow-"):
        executable = dxpy.DXWorkflow("'" + executable_id + "'")
    if executable is None:
        raise DXError("Executable {} is not an app, applet, or workflow")

    # Get input and output specifications
    output_spec = executable.describe()['outputSpec']
    output_keys = output_spec.keys()

    # validate batch arguments
    launch_arrays = {}
    width = None
    if !isinstance(batch_inputs, dict):
        raise DXError("batch_inputs is not a dictionary type")
    for key, arrValues in batch_inputs.iteritems():
        if !isinstance(arrValues, list):
            raise DXError("batch_inputs value {} is not a list type".format(arrValues))
        arr_width = len(arrValues)
        if width is None:
            width = arr_width
        else:
            if width != arr_width:
                raise DXError("Input array sizes do not match {} width={} actual_width={}"
                              .format(key, width, actual_width))
        launch_arrays[key] = arrValues
    if !isinstance(common_inputs, dict):
        raise DXError("common_inputs is not a dictionary type")

    # validate files argument
    if !isinstance(files, list):
        raise DXError("files argument is not a list type")
    for f in files:
        if !isinstance(f, DXFile):
            raise DXError("{} is not a dx:file".format(f))

    # build dictionary for each invocation
    # TODO: What happens to null values?
    launch_dicts = []
    for i in range(0, width):
        args = {}
        for k, arrValues = launch_arrays.iteritems():
            args[k] = arrValues(i)
        for k, v = common_inputs.iteritems():
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
        output[okey] = values

    results = {
        'outputs': outputs,
        'launched': launch_dicts
    }
    return {'results': results}

dxpy.run()
