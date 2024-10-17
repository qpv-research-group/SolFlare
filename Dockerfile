FROM python:3.11.7-bookworm
RUN apt-get update
RUN apt-get install --yes gfortran
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

# Create an App directory and install Python and dependencies
WORKDIR /usr/src/app
ENV PYTHONPATH=/usr/src/app
COPY requirements.txt . 
RUN pip3 install --no-cache-dir -r /usr/src/app/requirements.txt
WORKDIR /usr/src/app
COPY . .

# Run the Docker application
EXPOSE 8000
CMD ["/bin/sh", "start.sh"]

