FROM ubuntu:22.04

ENV TZ="Asia/Kolkata"
RUN date

# Set timezone:
RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone

# Update and install the necessary packages
RUN apt update -y && apt upgrade -y && apt install -y python3 python3-pip python3-venv git python3-full

# Create the python virtual environment
RUN python3 -m venv /rero/venv
RUN . /rero/venv/bin/activate

# Install requirements
# Despite the use of volume, this is required as volumes are set up towards the end of the container setup
COPY ./requirements.txt /src/requirements.txt
RUN python3 -m pip install -r /src/requirements.txt

# Make a http folder for the static html files
RUN mkdir /srv/http
WORKDIR /srv/http

# Make a folder for the database
RUN mkdir /var/lib/sqlite

# Create a secret key for hashing, make it readonly
RUN openssl rand -hex 32 > /etc/secret
RUN chmod 400 /etc/secret

# Create directories for storing the files
RUN mkdir /tmp/iot
RUN mkdir /tmp/ros

# Only for development purposes allow acces via volumes

# Maintain the folder structure as index.html followed by folders for css & js
# COPY ./http/ /srv/http/ # TODO: Uncomment this line
VOLUME [ "/srv/http" ]

WORKDIR /rero/
# COPY ./src /src/ # TODO: Uncomment this line
VOLUME [ "/rero/app" ]

# Expose port 8080 for user interface
EXPOSE 8080

# Export port 8081 for the rosbot
EXPOSE 8081

# Export port 8082 for the iot
EXPOSE 8082

# TODO: Replace this with the command to run the server
CMD ["/bin/bash", "/rero/app/startup_dev.sh"]
# CMD [ "uvicorn",  "app.main:app", "--host", "0.0.0.0", "--port", "8080"]