FROM python:3.12-slim

LABEL maintainer="Jermiah Joseph jermiahjoseph98@gmail.com"
LABEL description="This is a Dockerfile for the nbiatoolkit package."
LABEL license="MIT"
LABEL usage="docker run -it --rm <image_name> NBIAToolkit --help"
LABEL org.opencontainers.image.source="github.com/jjjermiah/nbiatoolkit"

# copy current directory to /nbiatoolkit
COPY . /nbiatoolkit

# set working directory
WORKDIR /nbiatoolkit

# install nbiatoolkit
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir .

RUN NBIAToolkit --help

# On run, open a bash shell
CMD ["/bin/bash"]
