FROM python:2.7
RUN mkdir /cst
COPY . /cst
RUN pip install -U pip
RUN pip install -r /cst/requirements.txt
WORKDIR /cst
RUN python ./manage.py migrate
CMD python ./manage.py runserver 0:8080
