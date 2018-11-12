FROM hysds/pge-base:latest

MAINTAINER jlinick "Justin.P.Linick@jpl.nasa.gov"
LABEL description="PGE for AOI update jobs"

USER root

#install shapely
RUN pip install shapely

# create work directory
RUN set -ex \
 && mkdir -p /data/work \
 && chmod -R 755 /data \
 && chown -R ops:ops /data

# provision create_AOI PGE
USER ops
COPY . /home/ops/verdi/ops/update_aoi

# set entrypoint
WORKDIR /home/ops
CMD ["/bin/bash", "--login"]
