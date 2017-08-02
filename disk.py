#!/usr/bin/env python

import os
import re
import time
import logger
from subprocess import Popen, PIPE
from prometheus_client import start_http_server, Gauge

smartctl = "/usr/sbin/smartctl"
disks = []
disk_healthy = Gauge('drive_health', 'SMART Healthcheck status', ['device'])
disk_reallocated_sector_count = Gauge('reallocated_sector_count', 'Reallocated sectors', ['device'])
disk_temperature = Gauge('drive_temperature', 'Drive temp if availables', ['device'])
disk_reallocated_event_count = Gauge('reallocated_event_count', 'Reallocated Event Count', ['device'])
disk_offline_uncorrectable = Gauge('offline_uncorrectable', 'Offline uncorrectable count', ['device'])

def sanity_checks():
	if os.path.isfile('/usr/sbin/smartctl') == False:
		print "Smartctl not found, this thing won't work!"
		exit(1)
	return

# returns a list of disks
def get_physical_devices():
	p1 = Popen(["lsblk", "-d"], stdout=PIPE)
	output =  p1.communicate()[0]
	lines = output.split('\n')
	for line in lines:
		is_physical_disk = re.match('^sd([a-z])\s', line)
		if is_physical_disk:
			disks.append(is_physical_disk.group(0).strip())
	return disks

def run_smartctl_check(disk):
	disk_to_check = "/dev/" + str(disk)
	proc = Popen(["smartctl", "-a", disk_to_check], stdout=PIPE)
	output =  proc.communicate()[0]
	return output

def parse_output(disk,output):
	lines = output.split('\n')
	for line in lines:
		# check overall status
		if "overall-health self-assessment test result" in line:
			if "PASSED" in line:
				disk_healthy.labels(disk).set(1)
			elif "OK" in line:
				disk_healthy.labels(disk).set(1)
			else:
				disk_healthy.labels(disk).set(0)

		# now lets parse the stats
		parts = line.split()
		if len(parts) > 0:
			# first, reallocated sectors, double check value ID
			if parts[0] == "5" and \
				parts[1] == "Reallocated_Sector_Ct":
				rsc = int(parts[9])
				disk_reallocated_sector_count.labels(disk).set(rsc)
			elif parts[0] == "190":
				temperature = int(parts[9])
				disk_temperature.labels(disk).set(temperature)
			elif parts[0] == "196":
				rec = int(parts[9])
				disk_reallocated_event_count.labels(disk).set(rec)
			elif parts[0] == "198":
				ou = int(parts[9])
				disk_offline_uncorrectable.labels(disk).set(ou)

def run_things():
	sanity_checks()
	get_physical_devices()

	if disks < 1:
		print "No physical disks found, exit!"

	for disk in disks:
		parse_output(disk,run_smartctl_check(disk))
	time.sleep(600)
	

if __name__ == "__main__":
	start_http_server(9009)
	while True:
		run_things()


