# syntax=docker/dockerfile:1.0.0-experimental
###################################################################################
### Build image to develop, test and provision AWS Resources for ANCHORE ENGINE ###
###################################################################################

FROM python:alpine as stage

ARG AWS_DEFAULT_REGION
ARG AWS_CONTAINER_CREDENTIALS_RELATIVE_URI
ARG AWS_PROFILE
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_SESSION_TOKEN

RUN apk add --update \
    py-pip \
    make \
    git \
    zip \
    ruby-dev\
    gcc \
    glib-dev \
    libc-dev \
    bash

### Production
FROM stage as prod
WORKDIR /src
COPY . /src
RUN pip install -r requirements.pip
CMD ["/bin/bash"]

### Test
FROM stage as test
WORKDIR /src
COPY . /src
RUN pip install -r requirements-test.pip
RUN gem install --no-document json
RUN gem install --no-document cfn-nag
CMD ["/bin/bash"]
