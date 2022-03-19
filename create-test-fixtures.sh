#!/bin/bash

usage(){
  echo "----------------------------------------------------------------"
  echo "create-test-fixtures automatically updates all fixtures to the latest state of the shared-file-converter"
  echo " "
  echo "./create-tst-fixtures.sh"
  echo " "
  echo "Please be aware that this changes the test fixtures which may lead into unintended passing of tests."
  echo "This script also deletes previous json fixtures. But these can be easily recovered using git."
  echo "It's advised to run this and view the changes in the git diff we to see if they're compatible with your code changes."
  echo "----------------------------------------------------------------"
}

usage
read -r -p "Are you sure you want to continue? [y/N] " response
response=${response,,}    # tolower
if [[ "$response" =~ ^(yes|y)$ ]]
then
  find tests -name "*.json" -type f -delete
  find tests -name "*.xml" -type f -exec python3 scripts/convert-file.py -i '{}' -o '{}'.json \;
  git add \*.json
else
  exit 1
fi
