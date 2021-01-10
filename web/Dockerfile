FROM python:3.8-slim
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app
RUN pip3 install -r requirements.txt
ADD . /app
EXPOSE 443
CMD ["gunicorn", "--workers=3", "--certfile=host.cert", "--keyfile=host.key", "-b", "0.0.0.0:443", "app:app"]