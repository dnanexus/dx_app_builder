#!/bin/bash

# The following line causes bash to exit at any point if there is any error
# and to output each line as it is executed -- useful for debugging
set -e -x -o pipefail

main() {
    dx-download-all-inputs

    mkdir -p out/b
    cp -r in/a/* out/b/

    dx-upload-all-outputs
}
