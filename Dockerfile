# A dockerfile must always start by importing the base image.
# We use the keyword 'FROM' to do that.
# In our example, we want import the python image.
# So we write 'python' for the image name and 'latest' for the version.
#FROM python:latest
# but instead we use this because we specifically want python 3.8 and not the latest version
FROM ubuntu:18.04

# ubuntu installing - python, pip
RUN apt-get update &&\
    apt-get install python3.8 -y &&\
	apt-get install python3-pip -y

# exposing default port for streamlit
EXPOSE 8501

# making directory of app
WORKDIR /swisscovidapp

# copy over requirements
COPY requirements.txt ./requirements.txt

# install pip then packages
RUN pip3 install -r requirements.txt

# copying all files over
# It is typically not recommended to copy all files to the image (particularly if you have large files). 
# However, since this is a small example, it won't cause any issues for us.
COPY . .

# cmd to launch app when container is run
CMD streamlit run swisscovid.py

# streamlit-specific commands for config
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN mkdir -p /root/.streamlit
RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'

RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
" > /root/.streamlit/config.toml'