Download Series
^^^^^^^^^^^^^^


The :meth:`downloadSeries` method is used to download an entire SeriesInstanceUID
from the NBIA Database.

One of the features provided by the `nbiatoolkit` is the ability to configure
the folder structure of the downloaded files. This functionality is handled internally
by the `DICOMSorter` class.

Configuration of the folder structure is done by passing a **`filePattern`** argument to the
:meth:`downloadSeries` method. The **`filePattern`** argument is a string constructed from
tags in the DICOM header. Tags are enclosed in `%` characters. For example, the following
**`filePattern`** string:

.. code-block:: python

    filePattern = '%PatientID/%StudyInstanceUID/%SeriesInstanceUID/%InstanceNumber.dcm'

will create a folder structure that looks like this:

.. code-block:: bash

    PatientID
    ├── StudyInstanceUID
    │   └── SeriesInstanceUID
    │       ├── 1.dcm
    │       ├── 2.dcm
    │       └── ...
    ├── StudyInstanceUID
    │   └── SeriesInstanceUID
    │       ├── 1.dcm
    │       ├── 2.dcm
    │       └── ...
    └── ...

The **`filePattern`** string can be constructed from any DICOM tag. The following tags are
good candidates for constructing a **`filePattern`** string:

- PatientID
- BodyPartExamined
- Modality
- StudyInstanceUID
- SeriesInstanceUID
- InstanceNumber
- SOPInstanceUID


To download a SeriesInstanceUID from the NBIA Database, use the :meth:`downloadSeries` method.

.. automethod:: nbiatoolkit.NBIAClient.downloadSeries


.. tabs::
   .. tab:: Python
        .. exec_code::

            # --- hide: start ---
            from nbiatoolkit import NBIAClient
            # --- hide: stop ---

            filePattern = '%PatientID/%StudyInstanceUID/%SeriesInstanceUID/%InstanceNumber.dcm'
            downloadDir = './NBIA-Download'
            nParallel = 5

            with NBIAClient(return_type="dataframe") as client:
                series = client.getSeries(
                    PatientID='TCGA-G2-A2EK'
                )

                client.downloadSeries(
                    series.SeriesInstanceUID,
                    downloadDir,
                    filePattern,
                    nParallel
                )
