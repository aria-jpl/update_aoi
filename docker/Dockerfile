FROM hysds/pge-base:latest

MAINTAINER jlinick "Justin.P.Linick@jpl.nasa.gov"
LABEL description="PGE for AOI update jobs"

ARG id
ARG gid

#Change UID and GID from build
USER root
RUN set -ex && \
  usermod -u ${id} ops && \
  groupmod -g ${gid} ops && \
  chown -R ops:ops /home/ops/ /data && \
  usermod -g ${gid} ops

#install shapely
RUN pip install shapely

#install redis
#RUN set -ex && \
#  yum install -y redis

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
