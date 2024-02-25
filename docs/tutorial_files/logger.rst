Configuring Logger
------------------

Any logger from the `logging` module can be used.
A utility function `setup_logger` is provided for convenience.

.. autofunction:: nbiatoolkit.logger.setup_logger

.. tabs::

    .. tab:: Python

        .. exec_code:: python

            from nbiatoolkit import NBIAClient
            from nbiatoolkit import setup_logger

            my_logger = setup_logger(
                name="my_logger",
                log_level="DEBUG",
                console_logging=False,
                log_file="logfile.log",
                log_dir="logs",
                log_format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
                datefmt="%y-%m-%d %H:%M",
            )

            # log some messages
            my_logger.info("This is an info message")


            # --- hide: start ---
            print("\n")
            # --- hide: stop ---

            # read in the log file
            print("Contents of logfile.log:")
            with open("logs/logfile.log", "r") as f:
                print(f.read())


            client_logger = setup_logger(
                name="NBIAClient",
                log_level="DEBUG",
                console_logging=False,
                log_file="logfile.log",
                log_dir="logs",
                log_format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
                datefmt="%y-%m-%d %H:%M",
            )

            client = NBIAClient(logger=client_logger)

            # --- hide: start ---
            print("\n")
            # --- hide: stop ---

            print("Contents of logfile.log after creating NBIAClient:")
            with open("logs/logfile.log", "r") as f:
                print(f.read())
