FROM mambaorg/micromamba:2.10.0
ENV DEBIAN_FRONTEND=noninteractive

COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /environment.yml
RUN micromamba install --name base --file /environment.yml --yes && \
    micromamba clean --all --yes
