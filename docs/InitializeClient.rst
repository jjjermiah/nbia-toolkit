Initialize Client
-----------------
By default, nbiatoolkit uses the guest account to access all collections in the API that are publicly available.
If you have a user account that has been granted specific access to a collection, you can use your credentials to
initialize the client when performing a query.

.. tabs::

   .. tab:: Python

      To do the same in Python, run the following code:

      .. tabs::

         .. tab:: Guest Account

            .. code-block:: python

               from nbiatoolkit import NBIAClient

               client = NBIAClient()
               client.getCollections(prefix='TCGA')

         .. tab:: Your Account

            .. code-block:: python

               from nbiatoolkit import NBIAClient

               client = NBIAClient(username = "<USERNAME>", password = "<PASSWORD>")
               client.getCollections(prefix='TCGA')

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




Logging
^^^^^^^
The client can be initialized with a log level to control the verbosity of the logs. This is primarily intended for debugging and development purposes.
The default log level is 'INFO' and the available log levels are 'DEBUG', 'INFO', 'WARNING', 'ERROR'.

.. tabs::

   .. tab:: Python

      .. code-block:: python

         from nbiatoolkit import NBIAClient

         client = NBIAClient(log_level='DEBUG)
         client.getCollections(prefix='TCGA')
