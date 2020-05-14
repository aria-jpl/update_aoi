FROM hysds/pge-base:develop-es1

MAINTAINER jlinick "Justin.P.Linick@jpl.nasa.gov"
LABEL description="PGE for AOI update jobs"

USER root
# provision create_AOI PGE
USER ops
COPY . /home/ops/verdi/ops/update_aoi

# set entrypoint
WORKDIR /home/ops
CMD ["/bin/bash", "--login"]
