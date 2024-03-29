# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim-buster

ARG APP_ENV

ENV APP_ENV=${APP_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \ 
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.10 \
  POETRY_VIRTUALENVS_CREATE=false \
  PATH="$PATH:/root/.poetry/bin"

# exposing default port for streamlit
EXPOSE 8501

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
# USER appuser

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$YOUR_ENV" == production && echo "--no-dev") --no-interaction --no-ansi


# Creating folders, and files for a project:
COPY . /app

# cmd to launch app when container is run
CMD streamlit run swisscovid.py

# streamlit-specific commands for config
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN mkdir -p /root/.streamlit

# TODO
# errors here because of user
# add user in a future release

# => ERROR [ 8/10] RUN mkdir -p /root/.streamlit                                                                                                                                                                  0.5s
#------
# > [ 8/10] RUN mkdir -p /root/.streamlit:
#12 0.501 mkdir: cannot create directory ‘/root’: Permission denied
#------
#executor failed running [/bin/sh -c mkdir -p /root/.streamlit]: exit code: 1

RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'

RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
" > /root/.streamlit/config.toml'