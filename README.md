# Disk-Exporter

Disk-Exporter exports Prometheus metrics about the health of your system's
physical disks and software RAID arrays. It uses smartctl and mdadm to do this.

This was written for a specific environment and therefore makes some assumptions
about your server.

## Disk metrics

The exporter detects disks using 'lsblk'. It assumes they follow the pattern
`^sd([a-z])\s`. The following key metrics are exported, but the script allows
for adding more if required, with relative ease.

Some may not be available depending on your drive.

* Overall disk health (Smartctl self-check "Passed" or not) Disk reallocated
* sector count  Disk temperature Disk reallocated event count  Disk offline
* uncorrectable

## RAID metrics

This simply uses mdadm to check the health of each array it finds.

* "Clean" and "OK" are the only acceptable array states.
