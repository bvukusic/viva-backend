FROM python:3.8.2
ENV PYTHONUNBUFFERED 1
#RUN apt-get update
#RUN apt-get install -y swig libssl-dev dpkg-dev netcat
#RUN apt-get install -y build-essential python-dev default-libmysqlclient-dev mysql-client
RUN mkdir /app
WORKDIR /app
COPY . /app/
RUN python -m pip install --upgrade pip
RUN pip install -r /app/requirements.txt