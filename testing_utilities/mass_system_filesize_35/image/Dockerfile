FROM alpine
RUN apk add --no-cache python3 && \
    apk add --no-cache git
RUN apk update && apk upgrade
   apk add --no-cache docker
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
ADD . /
ENTRYPOINT python3 filesize_analysis_instance.py
