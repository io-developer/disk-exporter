# Disk-Exporter

Disk-Exporter exports Prometheus metrics about the health of your system's
physical disks. It uses smartctl to do this.

This was written for a specific environment and therefore makes some assumptions.

## Disk metrics

The exporter detects disks using 'lsblk'. It assumes they follow the pattern
`^sd([a-z])\s`. The following key metrics are exported, but the script allows
for adding more if required, with relative ease.

Some may not be available depending on your drive.

* Overall disk health (Smartctl self-check "Passed" or not) 
* Disk reallocated sector count  
* Disk temperature 
* Disk reallocated event count  
* Disk offline uncorrectable count

## RAID metrics
Previous code was removed. Use **prom/node-exporter** for this purpose (node_md_* metrics)

## Installation

Docker hub - https://hub.docker.com/r/iodeveloper/prom_diskexporter

Example for **docker-compose.yml**
```yaml
version: '3.4'
services:
  diskexporter:
    image: iodeveloper/prom_diskexporter:latest
    user: root
    privileged: true
    restart: unless-stopped
    ports:
      - "9009:9009"
```