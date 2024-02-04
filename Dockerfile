# This Dockerfile will create a container that builds the nbiatoolkit package
# using the code in this repository
#
# To build the container, run the following command from the root of the
# repository:
# docker build -t nbiatoolkit .
#
# ADD LABELS HERE

FROM python:3.12-slim

LABEL maintainer="Jermiah Joseph jermiahjoseph98@gmail.com"
LABEL description="This is a Dockerfile for the nbiatoolkit package."
LABEL license="MIT"
LABEL usage="docker run -it --rm <image_name> NBIAToolkit --help"
LABEL org.opencontainers.image.source="github.com/jjjermiah/nbiatoolkit"

# install the dependencies
RUN pip install --upgrade pip
RUN python -m pip install nbiatoolkit

RUN NBIAToolkit --help

# On run, open a bash shell
CMD ["/bin/bash"]

# to run this container in terminal mode, use the following command:
# docker run -it --rm nbiatoolkit