#!/bin/bash

dx run app_scatter -iexec_id=applet-SUM-XXXX -ibatch_inputs='{"a": [2,3,4], "b": [1,2,3]}' -iinstance_types=["mem1_ssd1_x4"] -y --watch

dx run app_scatter -iexec_id=applet-SUM-XXXX -ibatch_inputs='{"a": [2,3,4]}' -iinstance_types=["mem1_ssd1_x4"] -y --watch

dx run app_scatter -iexec_id=applet-F9QY6G00ZvgxfXBF1qzk1F50 -ibatch_inputs='{"a": [{"$dnanexus_link": "file-F5gkQ3Q0ZvgzxKZ28JX5YZjy"}], "b": [{"$dnanexus_link": "file-F5gkPXQ0Zvgp2y4Q8GJFYZ8G"}]}' -ifiles="file-F5gkQ3Q0ZvgzxKZ28JX5YZjy" -ifiles="file-F5gkPXQ0Zvgp2y4Q8GJFYZ8G" -iinstance_types=["mem1_ssd1_x4"] -y --watch
