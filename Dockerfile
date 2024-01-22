# This Dockerfile will create a container that builds the nbiatoolkit package
# using the code in this repository
#
# To build the container, run the following command from the root of the
# repository:
# docker build -t nbiatoolkit .
#

FROM python:3.12-slim

# install the dependencies
RUN python -m pip install nbiatoolkit

RUN python -c 'import nbiatoolkit; print(nbiatoolkit.__version__)'

# On run, open a bash shell
CMD ["/bin/bash"]

# to run this container in terminal mode, use the following command:
# docker run -it --rm nbiatoolkit