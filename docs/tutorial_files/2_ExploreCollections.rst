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
