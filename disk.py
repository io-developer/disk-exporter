#!/usr/bin/env python

# Prometheus disk exporter
# Exports smartctl and mdadm health statistics
# Jimmy Crutchfield 2017

import os
import re
import time
from subprocess import Popen, PIPE
from prometheus_client import start_http_server, Gauge

# Paths to binaries
smartctl = "/usr/sbin/smartctl"
mdadm = "/sbin/mdadm"

disks = []
arrays = []

# How often to re-poll smartctl and mdadm
check_frequency = 600

# Metrics to export
disk_healthy = Gauge('disk_healthy', 'SMART Healthcheck status', ['device'])
disk_reallocated_sector_count = Gauge('disk_reallocated_sector_count', 'Reallocated sectors', ['device'])
disk_temperature = Gauge('disk_temperature', 'Drive temperature (if available)', ['device'])
disk_reallocated_event_count = Gauge('disk_reallocated_event_count', 'Reallocated Event Count (if available)', ['device'])
disk_offline_uncorrectable = Gauge('disk_offline_uncorrectable', 'Offline uncorrectable count (if available)', ['device'])
array_healthy = Gauge('array_healthy', 'RAID Array Healthcheck status', ['device'])

# Check we have smartctl
def sanity_checks():
	if os.path.isfile(smartctl) == False:
		print "Smartctl not found, Disk checks will not work"
		exit(1)
	if os.path.isfile(smartctl) == False:
		# Don't exit, this isn't a fatal condition
		print "Mdadm not found, RAID checks will not work."
	return

# Returns a list of disks
def get_physical_devices():
	p1 = Popen(["lsblk", "-d"], stdout=PIPE)
	output =  p1.communicate()[0]
	lines = output.split('\n')
	for line in lines:
		is_physical_disk = re.match('^sd([a-z])\s', line)
		if is_physical_disk:
			disks.append(is_physical_disk.group(0).strip())
	return disks

# Run smartctl and return output
def run_smartctl_check(disk):
	disk_to_check = "/dev/" + str(disk)
	proc = Popen(["smartctl", "-a", disk_to_check], stdout=PIPE)
	output =  proc.communicate()[0]
	return output

# Parse the output and extract metrics
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

		# Parse stats
		parts = line.split()
		if len(parts) > 0:
			# With reallocated sector count, double check value ID
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

# Get a list of RAID arrays seen by mdadm
def get_arrays():
	mdadm_scan = os.popen("/sbin/mdadm --detail --scan").readlines()
	for line in mdadm_scan:
		if "ARRAY" in line:
			array = line.split()[1]
			arrays.append(array)
		if len(arrays) == 0:
			print "No raid arrays found. No RAID metrics to export."
		else:
			return arrays

# Check their health; "clean" and "active" are good
def run_mdadm_check(array):
	mdadm_output = os.popen("/sbin/mdadm --detail %s" % (array)).readlines()

	for line in mdadm_output:
            if "State :" in line:
                state = line.split(":")[-1][1:-1]
                state = state.strip()
                re_clean = re.compile('^clean(, no-errors)?$')
                if not re_clean.match(state) and state != "active" and "checking" not in state:
                	array_healthy.labels(array).set(0)
                else:
                	array_healthy.labels(array).set(1)
					
# Main runner for the script
def event_loop():
	sanity_checks()
	get_physical_devices()
	get_arrays()

	if disks < 1:
		print "No physical disks found. No disk metrics to export."
		exit(1)

	for disk in disks:
		parse_output(disk,run_smartctl_check(disk))

	for array in arrays:
		run_mdadm_check(array)

	time.sleep(check_frequency)
	

if __name__ == "__main__":
	start_http_server(9009)
	print "Started metrics server."
	while True:
		event_loop()


