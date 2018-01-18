#!/usr/bin/env python

@dxpy.entry_point('main')
def main(**job_inputs):
    executable = job_inputs['executable']
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

    output = {}
    return output

dxpy.run()
