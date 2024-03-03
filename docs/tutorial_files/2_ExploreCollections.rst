API Query Methods
----------------------


Collection Methods
^^^^^^^^^^^^^^^^^^
The simplest way to get a list of collections is to use the
:meth:`nbiatoolkit.NBIAClient.getCollections` method.
This method returns a list of all collections available in the NBIA database.

The method has the following signature:

.. automethod:: nbiatoolkit.NBIAClient.getCollections

Passing no parameters to the method will return a list of all collections available in the NBIA database.
Passing a `prefix` parameter will return a list of collections that match the prefix.

.. tabs::

   .. tab:: Python

      .. exec_code::

         from nbiatoolkit import NBIAClient

         client = NBIAClient(return_type = "dataframe")
         collections_df = client.getCollections(prefix='TCGA')

         print(f"The number of available collections is {len(collections_df)}")

         print(collections_df)


.. automethod:: nbiatoolkit.NBIAClient.getCollectionDescriptions

.. tabs::

   .. tab:: Python

      .. exec_code::

         # --- hide: start ---
         from nbiatoolkit import NBIAClient
         from pprint import pprint as print
         # --- hide: stop ---

         with NBIAClient() as client:
            desc = client.getCollectionDescriptions(collectionName = "TCGA-BLCA")[0]

         print(desc['Description'])
         print(desc['DescriptionURI'])
         print(desc['LastUpdated'])



.. automethod:: nbiatoolkit.NBIAClient.getCollectionPatientCount


.. tabs::

   .. tab:: Python

      .. exec_code::

         # --- hide: start ---
         from nbiatoolkit import NBIAClient
         # --- hide: stop ---

         with NBIAClient() as client:
            counts_df = client.getCollectionPatientCount(
               prefix = "TCGA",
               return_type="dataframe"
            )

         print(counts_df)



Modality Methods
^^^^^^^^^^^^^^^^^^
The :meth:`getModalityValues` method can provide insight to the available modality types in the NBIA database.

The method has the following signature:

.. automethod:: nbiatoolkit.NBIAClient.getModalityValues

Passing no parameters to the method will return a list of all modality types available in the NBIA database.
Filtering by :code:`Collection` and :code:`BodyPartExamined` is also possible.
The :code:`Counts` parameter can be set to :code:`True` to return the number of patients for each modality type.

.. tabs::

   .. tab:: Python

      .. tabs::

         .. tab:: Default Query
            .. exec_code::

               # --- hide: start ---
               from nbiatoolkit import NBIAClient
               # --- hide: stop ---

               with NBIAClient(return_type="dataframe") as client:
                  modalities = client.getModalityValues()

               print(modalities)

         .. tab:: Filtered Query

            .. exec_code::

               # --- hide: start ---
               from nbiatoolkit import NBIAClient
               # --- hide: stop ---

               with NBIAClient(return_type="dataframe") as client:
                  modalities = client.getModalityValues(
                     collection = "TCGA-BLCA",
                  )

               print(modalities)

         .. tab:: Counts Query

            .. exec_code::

               # --- hide: start ---
               from nbiatoolkit import NBIAClient
               # --- hide: stop ---

               with NBIAClient(return_type="dataframe") as client:
                  modalities = client.getModalityValues(
                     collection = "TCGA-BLCA",
                     counts = True
                  )

               print(modalities)
