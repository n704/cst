#FROM ubuntu:latest
#RUN apt-get update -y
#RUN apt-get install -y python-pip
#RUN apt-get install -y  libmysqlclient-dev libssl-dev libffi-dev python-dev libncurses5-dev libxml2-dev libxslt1-dev
#RUN apt-get install -y python-dev build-essential
#COPY . /reservation
#RUN pip install -r requirements.txt
#WORKDIR /reservation/reservation
#CMD python manage.py runserver 0.0.0.0:8082

FROM python:2.7
RUN mkdir /reservation
COPY . /reservation
RUN pip install -U pip
RUN pip install -r /reservation/requirements.txt
WORKDIR /reservation/reservation
RUN python ./manage.py migrate
RUN python ./manage.py create_data
CMD python ./manage.py runserver 0:8082
