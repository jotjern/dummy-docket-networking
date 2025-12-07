FROM python:3.13-alpine

RUN apk add --no-cache iproute2

COPY listener.py .

CMD /usr/local/bin/python3 listener.py