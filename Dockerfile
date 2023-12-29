FROM python:3.10.5
MAINTAINER Harris Kirk <cjtkirk@protonmail.com>

ENV INSTALL_PATH /gwa
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --upgrade
RUN pip install black
RUN pip install flake8

COPY ./gwa ./gwa

CMD gunicorn -b 0.0.0.0:8000 --access-logfile - "gwa.app:create_app()"


