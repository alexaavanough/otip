FROM python:3.9
MAINTAINER 2018-3-08-dav
WORKDIR labwork_2
RUN pip3 install elasticsearch-dsl==7.4.0
RUN pip3 install click
RUN pip3 install pytest && pip3 install pytest-cov
COPY . .
ENTRYPOINT ["python","main.py"]
