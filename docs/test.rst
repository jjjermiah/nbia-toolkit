Initialize Client
-----------------
By default, nbiatoolkit uses the guest account to access all collections in the API that are publicly available.
If you have a user account that has been granted specific access to a collection, you can use your credentials to
initialize the client when performing a query.

.. tabs::

   .. tab:: Command Line

      To get a list of available public collections that start with "TCGA", run the following command:

      .. tabs::

         .. tab:: Guest Account

            .. code-block:: bash

               getCollections --prefix TCGA

         .. tab:: Your Account

            .. code-block:: bash

               getCollections -u <USERNAME> -p <PASSWORD> --prefix TCGA

   .. tab:: Python

      To do the same in Python, run the following code:

      .. tabs::

         .. tab:: Guest Account

            .. code-block:: python

               from nbiatoolkit import NBIAClient

               client = NBIAClient()
               client.getCollections(prefix='TCGA')

            .. raw:: html

               <iframe src="_static/test_setup.html" width="100%" height="100%"></iframe>

         .. tab:: Your Account

            .. code-block:: python

               from nbiatoolkit import NBIAClient

               client = NBIAClient(username = "<USERNAME>", password = "<PASSWORD>")
               client.getCollections(prefix='TCGA')

            .. raw:: html

               <iframe src="_static/test_setup.html" width="100%" height="100%"></iframe>


Logging
^^^^^^^
.. tabs::

   .. tab:: Python

      .. code-block:: python

         from nbiatoolkit import NBIAClient

         client = NBIAClient(log_level='DEBUG)
         client.getCollections(prefix='TCGA')

   .. tab:: Command Line

      .. code-block:: bash

         getCollections --prefix TCGA # TODO:: implement logging for cli

.. tabs::

   .. group-tab:: Linux

      Linux tab content - tab set 1

   .. group-tab:: Mac OSX

      Mac OSX tab content - tab set 1

   .. group-tab:: Windows

      Windows tab content - tab set 1

.. tabs::

   .. group-tab:: Linux

      Linux tab content - tab set 2

   .. group-tab:: Mac OSX

      Mac OSX tab content - tab set 2

   .. group-tab:: Windows

      Windows tab content - tab set 2


.. tabs::

   .. code-tab:: c

         C Main Function

   .. code-tab:: c++

         C++ Main Function

   .. code-tab:: py

         Python Main Function

   .. code-tab:: java

         Java Main Function

   .. code-tab:: julia

         Julia Main Function

   .. code-tab:: fortran

         Fortran Main Function

   .. code-tab:: r R

         R Main Function

.. tabs::

   .. code-tab:: c

         int main(const int argc, const char **argv) {
         return 0;
         }

   .. code-tab:: c++

         int main(const int argc, const char **argv) {
         return 0;
         }

   .. code-tab:: py

         def main():
            return

   .. code-tab:: java

         class Main {
            public static void main(String[] args) {
            }
         }

   .. code-tab:: julia

         function main()
         end

   .. code-tab:: fortran

         PROGRAM main
         END PROGRAM main

   .. code-tab:: r R

         main <- function() {
            return(0)
         }
