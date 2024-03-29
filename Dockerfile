FROM python:3.9-slim-buster

RUN apt-get update -y && apt-get install -y git python3-dev gcc 

USER root
RUN apt-get install -y \
    build-essential \
    libpq-dev \
    libgeos-dev \
    wget \
    curl \
    sqlite3 \
    cmake \
    libtiff-dev \
    libsqlite3-dev \
    libcurl4-openssl-dev \
    pkg-config \
    tk \
    && rm -rf /var/lib/apt/lists/*

# Installing gdal on debian
# From https://stackoverflow.com/questions/70927081/cannot-install-gdal-on-docker-container
# This is just an example with hard-coded paths/uris and no cleanup...
RUN curl https://download.osgeo.org/proj/proj-8.2.1.tar.gz | tar -xz &&\
    cd proj-8.2.1 &&\
    mkdir build &&\
    cd build && \
    cmake .. &&\
    make && \
    make install

RUN wget http://download.osgeo.org/gdal/3.4.0/gdal-3.4.0.tar.gz
RUN tar xvfz gdal-3.4.0.tar.gz
WORKDIR ./gdal-3.4.0
RUN ./configure --with-python --with-pg --with-geos &&\
    make && \
    make install && \
    ldconfig

WORKDIR /

RUN rm -rf gdal-3.4.0  &&\
    rm -rf proj-8.2.1 &&\
    rm gdal-3.4.0.tar.gz
    
COPY requirements.txt .

RUN pip install --upgrade -r requirements.txt

ENV BUILD_ENV=production
ENV DISK=/var/data/v0.4
ENV MODEL_VERSION=0.4.3
ENV MODEL_IMAGE_SIZE=384
ENV MODEL_PATH="$DISK/v${MODEL_VERSION}-model.pkl"
ENV KG_FILE_PATH="$DISK/kg.tif"
ENV ELU_FILE_PATH="$DISK/elu.tif"
ENV DB_FILE_PATH="$DISK/api.sqlite3"
ENV STATIC_FILES=static
ENV OBSERVATION_IMAGES=/var/data/observation_images

COPY app app

WORKDIR /app

EXPOSE 8080

CMD ["python", "server.py"]
