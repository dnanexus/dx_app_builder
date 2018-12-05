#!/bin/bash
# Test build of asset on 16.04 instance
#
# Strategy:
#   1. Create asset
#   2. Download Hidden file to local machine
#   3. Compare tar identity with expected files
#   4. Clean up test side effects

set -e -o pipefail

# Delete the project on test script fail or success
clean-up () {
    script_return_value=$?
    echo "Cleaning up"
    [[ -n "$PROJECT_ID" ]] && dx rmproject -y "${PROJECT_ID}"
    [[ -d "$TMP_DIR" ]] && rm -rf "$TMP_DIR"
    exit $script_return_value
}
trap clean-up EXIT

if [[ ( $# -ne 1 ) || ( ! "$1" =~ ^(xenial|trusty)$ ) ]]; then
  echo "
  Rudimentary script to Execute asset build test. Expected inputs:
    xenial
    trusty

  Arguments:
        \$1 - target Ubuntu Release
  "
  exit 1
fi
# Set up test and expected tar file contents
echo "Test setup"

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
BUILDER_DIR="${SCRIPTPATH}/data/sample_${1}_asset"
EXPECTED_ITEMS_FILE="${SCRIPTPATH}/data/sample_${1}_asset/expected_asset_tar_contents"

PROJECT_ID=$(dx new project "TMP_AssetBuilder_${RANDOM}" -s --brief)


# Build asset
echo "Building asset"
response=$(dx build_asset "$BUILDER_DIR" -d "${PROJECT_ID}:/" --no-watch --json)

# Populate helpful variables
echo "Populate job run variables for test"
record_id=$(<<<"$response" jq -r '.id' )
tar_file_id=$(dx describe "$record_id" --json | jq -r '.details.archiveFileId."$dnanexus_link"')

# Write actual tar file contents
#
# Bash tempdirs:
#   https://unix.stackexchange.com/questions/30091/fix-or-alternative-for-mktemp-in-os-x
TMP_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'tmpdir')
actual_items_file="${TMP_DIR}/actual"
dx cat "$tar_file_id" | tar -tf - > "${actual_items_file}"

# Verify asset contains target dirs and files
echo "Run test"
echo
echo "Unexpected dirs and files"
comm -13 "$EXPECTED_ITEMS_FILE" "${actual_items_file}"
echo

echo "Expected and found dirs and files"
comm -12 "$EXPECTED_ITEMS_FILE" "${actual_items_file}"
echo

echo "VERIFICATION POINT: Expected, but NOT found dirs and files"
comm -23 "$EXPECTED_ITEMS_FILE" "${actual_items_file}"
if [[ -n $(comm -23 "$EXPECTED_ITEMS_FILE" "$actual_items_file") ]]; then
    echo ""
    echo "Test failed"
    exit 1
fi

echo "TEST PASS"
