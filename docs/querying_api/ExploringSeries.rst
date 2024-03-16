Series Methods
^^^^^^^^^^^^^^

The :meth:`getSeries` method can provide insight to the available series
in the NBIA database.

.. automethod:: nbiatoolkit.NBIAClient.getSeries

By default, the method will return all the series in the database. However,
it can be filtered by the following parameters:

- **Collection**
- **PatientID**
- **StudyInstanceUID**
- **Modality**
- **SeriesInstanceUID**
- **BodyPartExamined**
- **ManufacturerModelName**
- **Manufacturer**

The following examples demonstrate using the :meth:`getSeries`.

.. tabs::
   .. tab:: Python
      .. tabs::
         .. tab:: Filter by Collection
            .. exec_code::

                # --- hide: start ---
                from nbiatoolkit import NBIAClient
                # --- hide: stop ---

                with NBIAClient(return_type="dataframe") as client:
                    series = client.Series(
                        Collection = "TCGA-BLCA"
                    )

               print(series.iloc[0])

        .. tab:: Filter by Collection and PatientID
            .. exec_code::

                # --- hide: start ---
                from nbiatoolkit import NBIAClient
                # --- hide: stop ---

                with NBIAClient(return_type="dataframe") as client:
                    series = client.getSeries(
                        Collection = "TCGA-BLCA",
                        PatientID = "TCGA-G2-A2EK"
                    )

                print(series.iloc[0])
