#!/bin/bash

dx run app_scatter -iexec_id=applet-SUM-XXXX -ibatch_inputs='{"a": [2,3,4], "b": [1,2,3]}' -iinstance_types=mem1_ssd1_x4 -y --watch

dx run app_scatter -iexec_id=applet-SUM-XXXX -ibatch_inputs='{"a": [2,3,4]}' -iinstance_types=mem1_ssd1_x4 -y --watch

dx run app_scatter -iexec_id=applet-F9QY6G00ZvgxfXBF1qzk1F50 -ibatch_inputs='{"a": [{"$dnanexus_link": "file-F5gkQ3Q0ZvgzxKZ28JX5YZjy"}], "b": [{"$dnanexus_link": "file-F5gkPXQ0Zvgp2y4Q8GJFYZ8G"}]}' -iin_files="file-F5gkQ3Q0ZvgzxKZ28JX5YZjy" -iin_files="file-F5gkPXQ0Zvgp2y4Q8GJFYZ8G" -iinstance_types="mem1_ssd1_x4" -y --watch

dx run app_scatter -iexec_id=applet-F9Y45g00pjvVJJP88gKpYkGg -ibatch_inputs='{"a": [{"$dnanexus_link": "file-F9Y4xq80pjvvJvjB8g6YQppQ"}]}' -iin_files="file-F9Y4xq80pjvvJvjB8g6YQppQ" -iinstance_types="mem1_ssd1_x4" -y --watch
