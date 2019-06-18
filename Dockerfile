FROM python:3.7-slim

RUN apt-get update && \
    apt-get -y install python3-gdbm git tk

# install the notebook package
RUN pip install --no-cache --upgrade pip && \
    pip install --no-cache notebook && \
    pip install git+https://github.com/okama-io/yapo.git

# create user with a home directory
ARG NB_USER
ARG NB_UID
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}
WORKDIR ${HOME}
USER ${USER}

RUN git clone --depth 20 https://github.com/okama-io/yapo.git /tmp/yapo/ && \
    mv /tmp/yapo/* .
