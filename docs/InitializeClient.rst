Initialize Client
-----------------
By default, nbiatoolkit uses the guest account to access all collections in the API that are publicly available.
If you have a user account that has been granted specific access to a collection, you can use your credentials to
initialize the client when performing a query.

.. tabs::

   .. tab:: Python

      Initializing without any credientials will use the guest account.
      To use your credentials, simply pass them as arguments to the NBIAClient class.

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


Context Manager for Client
^^^^^^^^^^^^^^^^^^^^^^^^^^
The client can be used as a context manager to ensure that the client is properly logged out after use.
This is especially useful when using the client in a script with a predefined scope and lifetime to ensure graceful termination of the client.

.. tabs::

   .. tab:: Python

      .. code-block:: python

         from nbiatoolkit import NBIAClient

         with NBIAClient() as client:
            client.getCollections(prefix='TCGA')

   .. tab:: Command Line

      The context manager is not available in the command line interface.


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

   .. tab:: Command Line

         Logging is not yet available in the command line interface. Feel free to open an issue on the GitHub repository if you would like to see this feature added.
