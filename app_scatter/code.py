#!/usr/bin/env python
# app_scatter

from __future__ import absolute_import, division, print_function, unicode_literals
import dxpy
import time
import json

def is_dx_file(ivalue):
    return (isinstance(ivalue, dict) and
            '$dnanexus_link' in ivalue and
            ivalue['$dnanexus_link'].startswith("file-"))

# collect results, and return as JBOR arrays
#
#  output_spec: description of executable
#  jobs: array of jobs/analyses that were launched
def collect(output_spec, jobs):
    output_keys = []
    for d in output_spec:
        output_keys.append(d["name"])
    print("output_keys={}".format(output_keys))

    outputs = {}
    for okey in output_keys:
        values = []
        for j in jobs:
            out_val = j.get_output_ref(okey)
            values.append(out_val)
        outputs[okey] = values

    return outputs

# This currently overlaps with the validate method implemented in the
# core platform (TODO).
#
def validate(exec_id, batch_inputs, common_inputs, files, instance_types):
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
        if not is_dx_file(f):
            raise Exception("{} is not a dx:file".format(f))

    # validate instance_types array. Create a simpler array, with
    # an entry
    if not isinstance(instance_types, list):
        raise Exception("instance_types is not a list type")
    n_instances = len(instance_types)
    if n_instances == 0:
        # Use default instance type
        job_instance_types = []
    elif n_instances == 1:
        # Same instance type for all jobs
        job_instance_types = [instance_types[0]] * width
    elif n_instances == width:
        # Specify different type for each job
        job_instance_types = instance_types
    else:
        raise Exception("instance-type length ({}) is invalid, could be 0, 1, or {}"
                        .format(n_instances, width))

    return {"executable": executable,
            "launch_arrays": launch_arrays,
            "width": width,
            "output_spec": output_spec,
            "job_instance_types": job_instance_types}

# At this point, we have an array of dictionaries, each one has the arugments
# for one invocation. Launch a job for each dictionary.
def launch_jobs(executable, launch_dicts, job_instance_types):
    jobs = []
    if len(job_instance_types) == 0:
        # Using default instance type
        for d in launch_dicts:
            job = executable.run(d)
            jobs.append(job)
    else:
        for (d, i_type) in zip(launch_dicts, job_instance_types):
            print("Running executable with i_type={}".format(i_type))
            job = executable.run(d, instance_type=i_type)
            jobs.append(job)
    return jobs

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

    d = validate(exec_id, batch_inputs, common_inputs, files, instance_types)
    executable = d['executable']
    launch_arrays = d['launch_arrays']
    width = d['width']
    output_spec = d['output_spec']
    job_instance_types = d['job_instance_types']

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
    jobs = launch_jobs(executable, launch_dicts, job_instance_types)

    # Collect arrays of JBORs
    outputs = collect(output_spec, jobs)
    results = {
        'outputs': outputs,
        'launched': launch_dicts
    }
    return {'results': results}

dxpy.run()
