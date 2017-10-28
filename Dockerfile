FROM continuumio/anaconda3:5.0.1

RUN apt-get install -y \
      libatlas-base-dev python-dev gfortran pkg-config libfreetype6-dev
RUN conda install jupyter cvxopt=1.1.8 -y --quiet

WORKDIR /opt/yapo

CMD "bin/docker-entrypoint.sh"
