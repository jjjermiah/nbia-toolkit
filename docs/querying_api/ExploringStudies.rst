Studies Methods
^^^^^^^^^^^^^^^

The :meth:`getStudies` method can provide insight to the available studies in the
NBIA database.


.. automethod:: nbiatoolkit.NBIAClient.getStudies

By default, the method requires filtering by **Collection**, but can optionally
be also filtered by **PatientID** and/or **StudyInstanceUID** as well.


The following example demonstrates how to use the :meth:`getStudies` method to filter the studies by the collection name.

.. tabs::

   .. tab:: Python

      .. tabs::

         .. tab:: Get all studies
            .. exec_code::

               # --- hide: start ---
               from nbiatoolkit import NBIAClient
               # --- hide: stop ---

               with NBIAClient(return_type="dataframe") as client:
                  studies = client.getStudies(
                    Collection = "TCGA-BLCA"
                )

               print(studies.iloc[0])

         .. tab:: Filter by Collection

            .. exec_code::

               # --- hide: start ---
               from nbiatoolkit import NBIAClient
               # --- hide: stop ---

               with NBIAClient(return_type="dataframe") as client:
                    studies = client.getStudies(
                        Collection = "TCGA-BLCA",
                        PatientID = "TCGA-G2-A2EK"
                    )

               print(studies.iloc[0])
