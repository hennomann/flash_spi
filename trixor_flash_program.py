#!/usr/bin/env python3
import os
import sys
import math
import struct
import flash_spi as flash

from time import sleep

# Open SPI device
device = flash.open();

# Read device ID
print("Read SPI flash device ID:")
r=flash.read_id(device)
print("0x",end="")
for byte in r[1:-1]:
    print("{:02x}".format(byte),end="")
print()
if (r[1]==0xc2 and r[2]==0x28 and r[3]==0x17):
    print("Found correct device ID, continuing...")
else:
    sys.exit("Wrong flash device ID detected, exiting...")
print()

# Write enable
flash.write_enable(device)
sleep(0.1)


# Erase flash (bulk)
print("Starting flash erase:")
flash.erase(device)
i=0
cnt = 0
while True:
    sleep(1)
    r=flash.status(device)
    if r[1]==0:
        print("Flash erase finished")
        break
    else:
        print("Still erasing"+"."*cnt+" "*(3-cnt)+"\r",end='')
        i=i+1
        cnt=(cnt+1)%4
print();
        
# Open bitfile and read bytes in binary mode:
with open('trixor_bitfile.bit','rb') as f:
    data_raw=f.read()
f.close()

# Convert binary object to list an discard unneccessary header data
start_byte = 113
data = list(data_raw[start_byte:])
#data = list(data_raw)
#for i in range(4):
#    data[i] = 0xff

# Pad data to have a full last page
pagecount = int(math.ceil(float(len(data))/256.))
n_pad = pagecount * 256 - len(data)
data += [0xff]*n_pad

'''
# Print parsed bitstream data to file
try:
    os.remove('trixor_bitstream_parsed.bin')
except:
    pass
    
with open('trixor_bitstream_parsed.bin','ab') as f:
    for byte in data:
        f.write(byte.to_bytes(1,'big'))
f.close()
'''

# Program flash page by page
print("Start programming flash:")
for i in range(pagecount):
    addr = i*256
    print("Writing page {:05d}/{:05d}\r".format(i,pagecount-1), end="")
    flash.page_program3B(device, addr, data[addr:addr+256])
    sleep(0.001)
print()
print("Programming flash finished")
print()

# Read flash content

#try:
#    os.remove('trixor_flash_dump.bin')
#except:
#    pass

print("Start verifying flash content:")
for i in range(pagecount):
    addr = i*256
    print("Reading page {:05d}/{:05d}\r".format(i,pagecount-1), end="")
    r=flash.read_page3B(device,addr)
    #print(r)
    #print(data[addr:addr+256])
    if list(r) != data[addr:addr+256]:
        print()
        print()
        print("Found bad flash content on page {:d}".format(i))
        print("Content of flash page:")
        print(list(r))
        print("Content of input bitstream page:")
        print(data[addr:addr+256])
        print()
        sys.exit("Verification failed! Exiting...")
    #with open('trixor_flash_dump.bin','ab') as f:
    #    for byte in r:
    #        f.write(byte.to_bytes(1,'big'))
#f.close()
print()
print("Flash content verified successfully!")
print()
print("Done")
