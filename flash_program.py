#!/usr/bin/env python3
import os
import sys
import math
import struct
import flash_spi as flash
import RPi.GPIO as GPIO

from time import sleep

# Setup SPI select GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.OUT)

# Set SPI select signal (0 -> FPGA, 1 -> FLASH)
GPIO.output(2,1)

# Open SPI device
device = flash.open();

# Read device ID
print("Read SPI flash device ID:")
r=flash.read_id(device)
print("0x",end="")
for byte in r[1:-1]:
    print("{:02x}".format(byte),end="")
print()
if (r[1]==0x20 and r[2]==0xba and r[3]==0x19):
    print("Found correct device ID, continuing...")
else:
    sys.exit("Wrong flash device ID detected, exiting...")

# Enter 4-byte address mode
flash.enter_4b_am(device)
sleep(0.1)

# Write enable
print("Set write enable")
flash.write_enable(device)
sleep(0.1)

# Erase flash (bulk)
print("Starting flash erase:")
flash.erase(device)
i=0
while True:
    sleep(2)
    r=flash.status(device)
    if r[1]==0:
        print("Flash erase finished")
        break
    else:
        print("Still erasing...")
        i=i+1

# Open bitfile and read bytes in binary mode:
with open('bitfile.bit','rb') as f:
#with open('mcs.mcs','rb') as f:
    data_raw=f.read()
f.close()

# Convert binary object to list an discard unneccessary header data
start_byte = 103
data = list(data_raw[start_byte:])
for i in range(4):
    data[i] = 0xff

# Pad data to have a full last page
pagecount = int(math.ceil(float(len(data))/256.))
n_pad = pagecount * 256 - len(data)
data += [0xff]*n_pad
    
# Print parsed bitstream data to file
try:
    os.remove('bitstream_parsed.bin')
except:
    pass
    
with open('bitstream_parsed.bin','ab') as f:
    for byte in data:
        f.write(byte.to_bytes(1,'big'))
f.close()

# Program flash page by page
print("Start programming flash:")
for i in range(pagecount):
    addr = i*256
    print("Writing page {:05d}/{:05d}\r".format(i,pagecount-1), end="")
    flash.page_program(device, addr, data[addr:addr+256])
print()
print("Programming flash finished")

# Read flash content
try:
    os.remove('flash_dump.bin')
except:
    pass
print("Read back flash content:")
for i in range(pagecount):
#for i in range(131072):
    addr = i*256
    print("Reading page {:05d}/{:05d}\r".format(i,pagecount-1), end="")
    r=flash.read_page(device,addr)
    with open('flash_dump.bin','ab') as f:
        for byte in r:
            f.write(byte.to_bytes(1,'big'))
f.close()
print()
print("Reading back flash finished")

# Exit 4-byte address mode
flash.exit_4b_am(device)

# Set SPI select signal (0 -> FPGA, 1 -> FLASH)
GPIO.output(2,0)

print("Done")
