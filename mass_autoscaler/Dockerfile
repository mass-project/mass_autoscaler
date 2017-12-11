FROM alpine
RUN apk add --no-cache python3 && \
    apk add --no-cache git && \
    apk add --update --repository http://dl-cdn.alpinelinux.org/alpine/edge/community/ tini docker
COPY requirements.txt /
RUN pip3 install -r /requirements.txt

## create image from local data ##
ADD . /
ENTRYPOINT python3 -u autoscaler.py

## download from MASS repository and create image ##
#RUN git clone https://github.com/mass-project/mass_autoscaler.git -b master
#WORKDIR mass_autoscaler/mass_autoscaler
#ENTRYPOINT python3 autoscaler.py