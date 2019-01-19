FROM python:2.7-stretch

RUN apt-get update \
    && apt-get install smartmontools -y --no-install-recommends \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && pip install prometheus_client

ADD disk.py /disk-exporter/disk.py

EXPOSE 9009

CMD ["python", "/disk-exporter/disk.py"]
