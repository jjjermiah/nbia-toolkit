Initialize Client
-----
By default, nbiatoolkit uses the guest account to access all collections in the API that are publicly available.
If you have a user account that has been granted specific access to a collection, you can use your credentials to
initialize the client when performing a query.


.. tabs::

    .. tab::







    .. tab:: Python

        To perform the same operation using the Python package, follow these steps:

        .. code-block:: python

            from your_python_package import YourClass

            instance = YourClass(option1='value1', option2='value2')
            instance.run_operation()



.. tabs::

   To get a list of available public collections that start with "TCGA", run the following command:

   .. tab:: Command Line

      .. tabs::

         .. tab:: Guest Account

            .. code-block:: bash

               getCollections --prefix TCGA

         .. tab:: Your Account

               getCollections -u <USERNAME> -p <PASSWORD> --prefix TCGA

   .. tab:: Python

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

.. tabs::

   .. tab:: Apples

      Apples are green, or sometimes red.

   .. tab:: Pears

      Pears are green.

   .. tab:: Oranges

      Oranges are orange.


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
