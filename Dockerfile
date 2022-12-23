FROM python:3.10.5
MAINTAINER Harris Kirk <cjtkirk@protonmail.com>

ENV PATH=.:$PATH
WORKDIR /opt/gwa
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --upgrade
RUN pip install black

COPY . .

CMD  ["echo", "GWA", "success!"]

