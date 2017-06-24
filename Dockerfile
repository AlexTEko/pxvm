FROM alpine:3.5
RUN apk add --update python3 py3-pip
COPY requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt
COPY pxvm /src/pxvm
CMD python3 /src/pxvm/main.py