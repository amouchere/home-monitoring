FROM python:3.8

RUN pip install --upgrade pip
RUN pip install wheel
RUN python -m pip install serial requests datetime simplejson influxdb


WORKDIR /usr/src/app
COPY temp-server.py .

CMD ["python", "/usr/src/app/temp-server.py"]