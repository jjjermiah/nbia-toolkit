Patient Methods
^^^^^^^^^^^^^^^

The :meth:`getPatients` method can provide insight to the
patient metadata available in the NBIA database.

.. automethod:: nbiatoolkit.NBIAClient.getPatients


By default, the :meth:`getPatients` method will return all
patients in the NBIA database. However, the method can be
filtered by `Collection`.

.. tabs::

   .. tab:: Python

      .. tabs::

         .. tab:: Get all patients
            .. exec_code::

               # --- hide: start ---
               from nbiatoolkit import NBIAClient
               # --- hide: stop ---

               with NBIAClient(return_type="dataframe") as client:
                  patients = client.getPatients()

               print(patients.head())

         .. tab:: Filter by Collection

            .. exec_code::

               # --- hide: start ---
               from nbiatoolkit import NBIAClient
               # --- hide: stop ---

               with NBIAClient(return_type="dataframe") as client:
                  patients = client.getPatients(Collection = "TCGA-BLCA")

               print(patients.head())


For more granular filtering, the :meth:`getPatientsByCollectionAndModality` method
can be used to filter by `Collection` **and** `Modality` as both are required.
Unlike the :meth:`getPatients` method which returns additional metadata such as
`SpeciesCode`, `SpeciesDescription`, `PatientSex`, and `EthnicGroup`, this method will
only return a list of Patient IDs.

.. automethod:: nbiatoolkit.NBIAClient.getPatientsByCollectionAndModality

.. tabs::

   .. tab:: Python

      .. exec_code::

        # --- hide: start ---
        from nbiatoolkit import NBIAClient
        # --- hide: stop ---

        with NBIAClient(return_type="dataframe") as client:
           patients = client.getPatientsByCollectionAndModality(Collection = "TCGA-BLCA", Modality = "MR")

        print(patients.head())


.. automethod:: nbiatoolkit.NBIAClient.getNewPatients

The :meth:`getNewPatients` method can be used to retrieve a list of patients that
have been added to the NBIA database within a specified time frame.

.. tabs::

   .. tab:: Python

      .. exec_code::

        # --- hide: start ---
        from nbiatoolkit import NBIAClient
        # --- hide: stop ---

        with NBIAClient(return_type="dataframe") as client:
            patients = client.getNewPatients(
                Collection="CMB-LCA",
                Date="2022/12/06",
            )

        print(patients.head())
