FROM alpine:3.7
LABEL maintainer="Maks Sych <makssych@gmail.com>"
EXPOSE 8779
WORKDIR /usr/src/app
RUN apk add --no-cache \
        uwsgi-python3 \
        python3
COPY . /usr/src/app
RUN rm -rf public/*
RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python3", "main.py", "--help" ]