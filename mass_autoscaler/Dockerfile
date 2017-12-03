FROM alpine
RUN apk add --no-cache python3 && \
    apk add --no-cache git
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
#ADD . /
RUN git clone https://github.com/mass-project/mass_autoscaler.git
WORKDIR mass_autoscaler/mass_autoscaler
ENTRYPOINT python3 autoscaler.py