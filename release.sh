#!/usr/bin/env bash
echo "--> Updating version to $1"
echo "__version__ = '$1'" > src/pycliarr/version.py

echo "--> Building wheel version $1"
pixi run release

if [ $? -ne 0 ]; then 
  echo "The command failed with exit status $?" 
  exit 1 
fi

echo "--> Pushing commit and generating github release v$1"
igit up -m "Update release to $1"
if [ $? -ne 0 ]; then 
  echo "The command failed with exit status $?" 
  exit 1 
fi

echo "--> Generating github release v$1"
gh release create v$1 --generate-notes
if [ $? -ne 0 ]; then 
  echo "The command failed with exit status $?" 
  exit 1 
fi

# echo "--> Publish $1 release to pypi"
# python3 -m twine upload --repository pycliarr dist/pycliarr-$1*
