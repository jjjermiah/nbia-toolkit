
[![PyTests](https://github.com/jjjermiah/nbia-toolkit/actions/workflows/main.yml/badge.svg)](https://github.com/jjjermiah/nbia-toolkit/actions/workflows/main.yml)
[![Documentation Status](https://readthedocs.org/projects/nbia-toolkit/badge/?version=latest)](https://nbia-toolkit.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/jjjermiah/nbia-toolkit/graph/badge.svg?token=JKREY71D0R)](https://codecov.io/gh/jjjermiah/nbia-toolkit)
[![Python version](https://img.shields.io/pypi/pyversions/nbiatoolkit.svg)](https://img.shields.io/pypi/pyversions/nbiatoolkit.svg)
[![PyPI version](https://badge.fury.io/py/nbiatoolkit.svg)](https://badge.fury.io/py/nbiatoolkit)
[![Downloads](https://static.pepy.tech/badge/nbiatoolkit)](https://pepy.tech/project/nbiatoolkit)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/nbiatoolkit.svg?label=pypi%20downloads)](https://pypi.org/project/nbiatoolkit/)
![GitHub repo size](https://img.shields.io/github/repo-size/jjjermiah/nbia-toolkit)
[![Docker Pulls](https://img.shields.io/docker/pulls/jjjermiah/nbiatoolkit)](https://hub.docker.com/r/jjjermiah/nbiatoolkit)



![GitHub milestone details](https://img.shields.io/github/milestones/progress-percent/jjjermiah/nbia-toolkit/1?style=flat-square&label=1.0.0%20Stable%20Release%20Milestone&link=https%3A%2F%2Fgithub.com%2Fjjjermiah%2Fnbia-toolkit%2Fmilestone%2F1)![GitHub milestone details](https://img.shields.io/github/milestones/progress/jjjermiah/nbia-toolkit/1?style=flat-square&label=%20&link=https%3A%2F%2Fgithub.com%2Fjjjermiah%2Fnbia-toolkit%2Fmilestone%2F1)


# *NBIA Toolkit*
`nbiatoolkit` is a python package that provides programmatic access to query and download images from the National Biomedical Imaging Archive (**NBIA**) and The Cancer Imaging Archive (**TCIA**) databases.

## Features
- Use NBIA Guest account to access public data OR authenticate using OAuth with user credentials for limited access data (requires approved data access).
- ***Query NBIA database*** for metadata on ***collections***, ***patients***, ***studies***, ***series***, and ***images***
- Download images from NBIA
  - ***Validate doownloads with MD5 checksums*** for downloaded images
  - **Auto-sort** DICOM files using a user-defined pattern of DICOM tags with specialized ***DICOMSorter class***

See Documentation at [NBIA-Toolkit Read The Docs](https://nbia-toolkit.readthedocs.io/en/latest/)


## Installation

`nbiatoolkit` is currently under development.
It is made available via PyPI and can be installed using pip:
****
```bash
pip install nbiatoolkit
```

## CLI Usage

### getCollections
nbia-toolkit also provides a command line interface (CLI) to query the NBIA database for some queries.
``` bash
> getCollections --prefix NSCLC
NSCLC Radiogenomics
NSCLC-Radiomics
NSCLC-Radiomics-Genomics
NSCLC-Radiomics-Interobserver1

> getCollections --prefix TCGA | head -5
TCGA-BLCA
TCGA-BRCA
TCGA-CESC
TCGA-COAD
TCGA-ESCA
```


## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`nbiatoolkit` was created by Jermiah Joseph. It is licensed under the terms of the MIT license.

## User Agreements and Disclaimers
The NBIA-toolkit is NOT a product of the National Cancer Institute (NCI) and is not endorsed by the NCI.
The NBIA-toolkit is provided as an open-source tool based on the [NBIA REST API](https://wiki.cancerimagingarchive.net/display/Public/NBIA+Advanced+REST+API+Guide).
The NBIA-toolkit is provided "AS IS" without warranty of any kind.

In no event shall the authors or contributors be liable for any claim, damages or other liability, arising from, out of or in connection with the NBIA-toolkit or the use or other dealings in the NBIA-toolkit.

Users of the NBIA-toolkit are required to abide by the NBIA REST API Terms of Service and the [NBIA Data Usage Policies and Restrictions](https://www.cancerimagingarchive.net/data-usage-policies-and-restrictions/)
