# shared-file-converter
This application creates the [shared-file-format](https://gitlab2.informatik.uni-wuerzburg.de/document-recognition/shared-file-format)
based on files from previous formats. It's constructed to be extensible for other file formats.   
The basic structure consists of two modules. The `validator` matches the input for the possible file format. 
The matching file format is selected here. The `strategies` module applies the selected strategies.  
New file formats can be integrated by adding a working `validator` which detects the file as the given format
and a matching `strategy`.
 
## currently supported file formats
* Page XML 2017

## requirements
* access to the `shared-file-format` repository

## Development
* run `setup-development.sh`
* activate your `venv` with `source .venv/bin/activate`

## Available scripts
See the `--help` option for further help on how to run these scripts. 
* `scripts/convert-file.py` to convert a single file
* `scripts/convert-dir.py` to monitor a complete folder on new files. This script will run until you terminate
it manually.  
Please be aware that it will remove the files from the specifies directory.

## Tests
* run the tests via: `python -m pytest tests/`
