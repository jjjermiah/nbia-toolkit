

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
                     Collection = "TCGA-BLCA",
                  )

               print(modalities)

         .. tab:: Counts Query

            .. exec_code::

               # --- hide: start ---
               from nbiatoolkit import NBIAClient
               # --- hide: stop ---

               with NBIAClient(return_type="dataframe") as client:
                  modalities = client.getModalityValues(
                     Collection = "TCGA-BLCA",
                     Counts = True
                  )

               print(modalities)
