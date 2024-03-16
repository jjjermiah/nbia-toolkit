Setup
-----------------


Initialize Client
^^^^^^^^^^^^^^^^^

By default, the `NBIAClient` uses the guest account to access all collections in the API that are publicly available.
If you have a user account that has been granted specific access to a collection, you can use your credentials to
initialize the client when performing a query.



.. tabs::

   .. tab:: Python

      Initializing without any credientials will use the guest account.
      To use your credentials, simply pass them as arguments to the NBIAClient class.

      .. tabs::

         .. tab:: Guest Account

            .. exec_code::

               from nbiatoolkit import NBIAClient

               client = NBIAClient()
               collections = client.getCollections(prefix='TCGA')

               print(collections[0:5])

         .. tab:: Your Account

            .. code-block:: python

               from nbiatoolkit import NBIAClient

               client = NBIAClient(username = "<USERNAME>", password = "<PASSWORD>")
               collections = client.getCollections(prefix='TCGA')


   .. tab:: Command Line

      All of the shell commands made available by nbiatoolkit have the option to use your credentials instead of the guest account.
      To do so, simply add the -u `USERNAME` and -pw `PASSWORD` flags to the command. For example:

      .. tabs::

         .. tab:: Guest Account

            .. code-block:: bash

               getCollections --prefix TCGA

         .. tab:: Your Account

            .. code-block:: bash

               getCollections -u <USERNAME> -pw <PASSWORD> --prefix TCGA


Context Manager for Client
^^^^^^^^^^^^^^^^^^^^^^^^^^
The client can be used as a context manager to ensure that the client is properly logged out after use.
This is especially useful when using the client in a script with a predefined scope and lifetime to ensure graceful termination of the client.

.. tabs::

   .. tab:: Python

      .. exec_code::

         from nbiatoolkit import NBIAClient

         with NBIAClient() as client:
            collections = client.getCollections(prefix='TCGA')

         print(collections[0:5])

   .. tab:: Command Line

      The context manager is not available in the command line interface.

Return Types of Methods
^^^^^^^^^^^^^^^^^^^^^^^
By default, most functions that query the API for metadata will return a list of dictionaries.
Available return types are made available through the `ReturnType` Enum which can be passed in as a parameter,
or its string representation. The available options as of writing are "list", and "dataframe".

If you would like to return the data as a pandas DataFrame, you can pass the
`return_type` argument to the respective class method:

.. tabs::

   .. tab:: Python

      .. exec_code::

         from nbiatoolkit import NBIAClient
         from nbiatoolkit.utils import ReturnType

         client = NBIAClient()
         collections_df = client.getCollections(
            prefix='TCGA', return_type='dataframe'
         )
         # equivalent to
         collections_df = client.getCollections(
            prefix='TCGA', return_type=ReturnType.DATAFRAME
         )

         print(collections_df.head())

   .. tab:: Command Line

      Return types are not yet available in the command line interface.
      Feel free to open an issue on the GitHub repository if you would like to see this feature added.


Alternatively, you can set the return type for all methods by passing the `return_type` argument when
initializing the NBIAClient class.

.. tabs::

   .. tab:: Python

      .. exec_code::

         from nbiatoolkit import NBIAClient

         client = NBIAClient(return_type='dataframe')
         collections_df = client.getCollections(prefix='TCGA')

         print(collections_df.head())

   .. tab:: Command Line

      Return types are not yet available in the command line interface.
      Feel free to open an issue on the GitHub repository if you would like to see this feature added.


Logging
^^^^^^^
The client can be initialized with a log level to control the verbosity of the logs. This is primarily
intended for debugging and development purposes.
The default log level is 'INFO' and the available log levels are `DEBUG`, `INFO`, `WARNING`, `ERROR`.

.. tabs::

   .. tab:: Python

      .. code-block:: python

         from nbiatoolkit import NBIAClient

         client = NBIAClient(log_level='DEBUG')
         client.getCollections(prefix='TCGA')

   .. tab:: Command Line

         Logging is not yet available in the command line interface.
         Feel free to open an issue on the GitHub repository if you would like to see this feature added.

For more configuration options for logging see :ref:`Configuring Logger`.
