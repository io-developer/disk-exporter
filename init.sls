/usr/local/bin/disk-exporter:
  file.managed:
    - source: salt://prometheus/disk-exporter/disk.py
    - target: /usr/local/bin/disk-exporter
    - mode: 755
    - makedirs: False

/etc/systemd/system/disk-exporter.service:
  file.managed:
    - source: salt://prometheus/disk-exporter/disk-exporter.service

Reload if changed:
  cmd.wait:
    - name: systemctl daemon-reload && systemctl enable disk-exporter && systemctl start disk-exporter
    - watch:
      - file: /usr/local/bin/disk-exporter

