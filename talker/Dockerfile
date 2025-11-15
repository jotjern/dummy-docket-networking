FROM python:3.13-alpine

RUN apk add --no-cache iproute2

COPY talker.py .
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/local/bin/python3", "talker.py"]
