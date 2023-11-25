[![PyTests](https://github.com/jjjermiah/NBIA-toolkit/actions/workflows/main.yml/badge.svg)](https://github.com/jjjermiah/NBIA-toolkit/actions/workflows/main.yml)
[![Documentation Status](https://readthedocs.org/projects/nbia-toolkit/badge/?version=latest)](https://nbia-toolkit.readthedocs.io/en/latest/?badge=latest)

# NBIA Toolkit 
- Packaged code to access the NBIA REST API 

See Documentation at [NBIA-Toolkit Read The Docs](https://nbia-toolkit.readthedocs.io/en/latest/)

    TODO::readthedocs::error in the example first cell
    TODO::auth.py::implement better access token handling
    TODO::auth.py::implement better error handling
    TODO::auth.py::implement refresh token functionality
    TODO::auth.py::implement logout functionality
    TODO::auth.py::implement encryption for username and password
    TODO::nbia.py::implement better error handling
    TODO::nbia.py::implement better logging & logger configuration
    TODO::nbia.py::enforce type checking for all functions and add type hints
    TODO::nbia.py::implement return formats for dict, and pandas.DataFrames
    TODO::nbia.py::handle error case of if resposne is not bytes 
    TODO::nbia.py::add tests for download Series
    TODO::nbia.py::add functionality for downloadSeries to take in a list of seriesUIDs
    TODO::md5.py::add tests
    TODO::md5.py::add logging and error handling for non-existent files
    TODO::dicomsort.py::come up with more efficient algorithm for sorting
    TODO::dicomsort.py::implement better error handling
    TODO::dicomsort.py::come up with solution to only use part of UIDs (last 5 digits)?


Wiki is empty for now:
See the [Wiki](https://github.com/jjjermiah/NBIA-toolkit/wiki) for more information.

# nbiatoolkit

A python package to query the National Biomedical Imaging Archive (NBIA) database.

## Installation

```bash
$ pip install nbiatoolkit
```

## Usage

See Documentation at [NBIA-Toolkit Read The Docs](https://nbia-toolkit.readthedocs.io/en/latest/)

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`nbiatoolkit` was created by Jermiah Joseph. It is licensed under the terms of the MIT license.

## Credits

`nbiatoolkit` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
