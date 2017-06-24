FROM alpine:3.5
RUN apk add --update python3 py3-pip
COPY requirements.txt /src/requirements.txt
RUN pip3 install -r /src/requirements.txt
COPY main.py /src/main.py
COPY config.py /src/config.py
COPY pxvm /src/pxvm
CMD python3 /src/main.py