FROM ubuntu:14.04
MAINTAINER Arthur Caranta <arthur@caranta.com>

# Set the UTF-8 encoding and locale
RUN locale-gen en_US.UTF-8  
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8 

# Make sure the package repository is up to date
RUN apt-get update && apt-get upgrade -y

# Install Python
RUN apt-get -y install python-pip
RUN pip install docker-py

# Clean up APT when done.
RUN apt-get -qy clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ADD backup.py /backup.py
WORKDIR /

ENTRYPOINT ["python",  "/backup.py" ]
