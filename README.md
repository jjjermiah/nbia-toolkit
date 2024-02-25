# *NBIA Toolkit*
## A python package that provides programmatic access to query and download images from the National Biomedical Imaging Archive (**NBIA**) and The Cancer Imaging Archive (**TCIA**) databases.
[![PyTests](https://github.com/jjjermiah/nbia-toolkit/actions/workflows/main.yml/badge.svg)](https://github.com/jjjermiah/nbia-toolkit/actions/workflows/main.yml)
[![Documentation Status](https://readthedocs.org/projects/nbia-toolkit/badge/?version=latest)](https://nbia-toolkit.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/jjjermiah/nbia-toolkit/graph/badge.svg?token=JKREY71D0R)](https://codecov.io/gh/jjjermiah/nbia-toolkit)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Python version](https://img.shields.io/pypi/pyversions/nbiatoolkit.svg)](https://img.shields.io/pypi/pyversions/nbiatoolkit.svg)
[![CodeFactor](https://www.codefactor.io/repository/github/jjjermiah/nbia-toolkit/badge)](https://www.codefactor.io/repository/github/jjjermiah/nbia-toolkit)


![GitHub release (latest by date)](https://img.shields.io/github/v/release/jjjermiah/nbia-toolkit)
[![PyPI version](https://badge.fury.io/py/nbiatoolkit.svg)](https://badge.fury.io/py/nbiatoolkit)
[![Downloads](https://static.pepy.tech/badge/nbiatoolkit)](https://pepy.tech/project/nbiatoolkit)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/nbiatoolkit.svg?label=pypi%20downloads)](https://pypi.org/project/nbiatoolkit/)
![GitHub repo size](https://img.shields.io/github/repo-size/jjjermiah/nbia-toolkit)
[![Docker Pulls](https://img.shields.io/docker/pulls/jjjermiah/nbiatoolkit)](https://hub.docker.com/r/jjjermiah/nbiatoolkit)




![GitHub milestone details](https://img.shields.io/github/milestones/progress-percent/jjjermiah/nbia-toolkit/1?style=flat-square&label=1.0.0%20Stable%20Release%20Milestone&link=https%3A%2F%2Fgithub.com%2Fjjjermiah%2Fnbia-toolkit%2Fmilestone%2F1)![GitHub milestone details](https://img.shields.io/github/milestones/progress/jjjermiah/nbia-toolkit/1?style=flat-square&label=%20&link=https%3A%2F%2Fgithub.com%2Fjjjermiah%2Fnbia-toolkit%2Fmilestone%2F1)
[![GitHub issues](https://img.shields.io/github/issues/jjjermiah/nbia-toolkit)](https://github.com/jjjermiah/nbia-toolkit/issues)
![GitHub last commit](https://img.shields.io/github/last-commit/jjjermiah/nbia-toolkit)



## Features
> [!TIP]
> For a thorough description of the package and its available features, please refer to the Documentation at [NBIA-Toolkit Read The Docs](https://nbia-toolkit.readthedocs.io/en/latest/)

- ***Programmatic access*** to the National Biomedical Imaging Archive (NBIA) and The Cancer Imaging Archive (TCIA) databases
  - Use NBIA Guest account to access public data OR authenticate using OAuth with user credentials for limited access data (requires approved data access).
  - Custom `OAuth2` class for **NBIA**, **TCIA**, including special handling for dedicated server for the **NLST** collection.

- ***Query NBIA database*** for metadata on ***collections***, ***patients***, ***studies***, ***series***, and ***images***
- Download images from NBIA
  - ***Validate doownloads with MD5 checksums*** for downloaded images
  - **Auto-sort** DICOM files using a user-defined pattern of DICOM tags with specialized ***DICOMSorter class***



## Installation

> [!WARNING]
> `nbiatoolkit` is currently under development and is not guaranteed to be stable.

It is made available via PyPI and can be installed using pip:
****
```bash
pip install nbiatoolkit
```

## Python Usage
Using a context manager, you can easily access the NBIA database and query for metadata on collections, patients, studies, and series.

``` python
from nbiatoolkit import NBIAClient

with NBIAClient() as client:
    # Get a list of collections
    collections = client.getCollections()
    print(collections)

    # Get a list of patients in a collection
    patients = client.getPatients(Collection="TCGA-KIRC")
    print(patients)

    # Get a list of studies for a patient
    studies = client.getStudies(PatientID="TCGA-BP-4989")
    print(studies)

    # Get a list of series for a study
    series = client.getSeries(StudyInstanceUID=studies[0]["StudyInstanceUID"])
    print(series[0:5])
```

## CLI Usage
For quick access to the NBIA, the toolkit also provides a command line interface (CLI)

``` bash NBIAToolkit-Output
> NBIAToolkit --version

        _   ______  _______  ______            ____   _ __
       / | / / __ )/  _/   |/_  __/___  ____  / / /__(_) /_
      /  |/ / __  |/ // /| | / / / __ \/ __ \/ / //_/ / __/
     / /|  / /_/ // // ___ |/ / / /_/ / /_/ / / ,< / / /_
    /_/ |_/_____/___/_/  |_/_/  \____/\____/_/_/|_/_/\__/
    
Version: 0.32.1

Available CLI tools: 

getCollections [-h] [-u USERNAME] [-pw PASSWORD] [-p PREFIX]
               [-o OUTPUTFILE] [--version]

getBodyPartCounts [-h] [-u USERNAME] [-pw PASSWORD] [-c COLLECTION]
                  [-o OUTPUTFILE] [--version]

getPatients [-h] [-u USERNAME] [-pw PASSWORD] -c COLLECTION
            [-o OUTPUTFILE] [--version]

getNewPatients [-h] [-u USERNAME] [-pw PASSWORD] -c COLLECTION -d DATE
               [-o OUTPUTFILE] [--version]

getStudies [-h] [-u USERNAME] [-pw PASSWORD] -c COLLECTION
           [-p PATIENTID] [-s STUDYINSTANCEUID] [-o OUTPUTFILE]
           [--version]

getSeries [-h] [-u USERNAME] [-pw PASSWORD] [-c COLLECTION]
          [-p PATIENTID] [-m MODALITY] [-study STUDYINSTANCEUID]
          [--seriesInstanceUID SERIESINSTANCEUID]
          [--bodyPartExamined BODYPARTEXAMINED]
          [--manufacturerModelName MANUFACTURERMODELNAME]
          [--manufacturer MANUFACTURER] [-o OUTPUTFILE] [--version]

getNewSeries [-h] [-u USERNAME] [-pw PASSWORD] -d DATE [-o OUTPUTFILE]
             [--version]

```


## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License
`nbiatoolkit` was created by Jermiah Joseph. It is licensed under the terms of the MIT license.

## User Agreements and Disclaimers
> [!IMPORTANT]
>The NBIA-toolkit is NOT a product of the National Cancer Institute (NCI) and is not endorsed by the NCI.
> Users of the NBIA-toolkit are required to abide by the NBIA REST API Terms of Service and the [NBIA Data Usage Policies and Restrictions](https://www.cancerimagingarchive.net/data-usage-policies-and-restrictions/)
> The NBIA-toolkit is provided as an open-source tool based on the [NBIA REST API](https://wiki.cancerimagingarchive.net/display/Public/NBIA+Advanced+REST+API+Guide) and is provided "AS IS" without warranty of any kind.
> In no event shall the authors or contributors be liable for any claim, damages or other liability, arising from, out of or in connection with the NBIA-toolkit or the use or other dealings in the NBIA-toolkit.
