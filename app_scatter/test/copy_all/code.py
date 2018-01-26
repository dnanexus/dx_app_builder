#!/usr/bin/env python

@dxpy.entry_point('main')
def main(**job_inputs):
    # process inputs
    plant = job_inputs['plant']
    thresholds = job_inputs['thresholds']
    pie = job_inputs['pie']
    misc = job_inputs['misc']

    # Return output
    output = {}
    output["plant"] = plant
    output["thresholds"] = thresholds
    output["pie"] = pie + 1
    output["misc"] = {"n": "non",
                      "y": "oui"}
    return output

dxpy.run()
