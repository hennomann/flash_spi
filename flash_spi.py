# Python functions for SPI communication
# between Raspberry Pi (master) and Micron SPI flash (slave)
# Henning Heggen, EE, GSI
# h.heggen@gsi.de
# Version 0.1

#!/usr/bin/env python3

import spidev
import struct
from time import sleep

# Open SPI connection
def open():
    try:
        spi_device = spidev.SpiDev()
        spi_device.open(0,0)
        spi_device.max_speed_hz = 10000000
        spi_device.mode = 0
    except Exception as e:
        print("Failed to open SPI connection")
        print(e.message, e.args)
        return
    return spi_device

# Enter 4-byte address mode
def enter_4b_am(device):
    msg = [0xb7]
    device.xfer2(msg)

# Exit 4-byte address mode
def exit_4b_am(device):
    msg = [0xe9]
    device.xfer2(msg)

# Read flash status register
def status(device):
    msg = [0x05,0x00]
    r = device.xfer2(msg)
    #print(hex(r[1]))
    return r

def flag_status(device):
    msg = [0x70,0x00]
    r = device.xfer2(msg)
    #print(hex(r[1]))
    return r[1:]

# Read flash status register
def read_id(device):
    msg = [0x9f,0x00,0x00,0x00,0x00]
    r = device.xfer2(msg)
    #print(hex(r[1]))
    return r

# Flash write enable command
def write_enable(device):
    msg = [0x06]
    device.xfer2(msg)

# Flash erase command
def erase(device):
    msg = [0x60]
    device.xfer2(msg)

# Flash 1 byte write operation (commands without payload)
def write(device,cmd):
    msg = [0x00]
    msg[0] = cmd
    device.xfer2(msg)

# Flash 1 byte write operation (commands without payload)
def page_program(device,addr,data):
    write_enable(device)
    msg = [0x02]
    msg += [((addr & 0xff000000) >> 24)]
    msg += [((addr & 0xff0000) >> 16)]
    msg += [((addr & 0xff00) >> 8)]
    msg += [(addr & 0xff)]
    for byte in data:
        msg += [byte]
    device.xfer2(msg)
    sleep(0.001)
    

# Read back 1 page (256 bytes) from flash memory
def read_page(device,addr):
    msg = [0x03]
    msg += [((addr & 0xff000000) >> 24)]
    msg += [((addr & 0xff0000) >> 16)]
    msg += [((addr & 0xff00) >> 8)]
    msg += [(addr & 0xff)]
    for i in range(256):
        msg += [0x00]
    r = device.xfer3(msg)
    return r[5:]

# Flash 1 byte write operation (commands without payload)
def page_program3B(device,addr,data):
    write_enable(device)
    msg = [0x02]
    msg += [((addr & 0xff0000) >> 16)]
    msg += [((addr & 0xff00) >> 8)]
    msg += [(addr & 0xff)]
    for byte in data:
        msg += [byte]
    device.xfer2(msg)
    sleep(0.001)
    

# Read back 1 page (256 bytes) from flash memory
def read_page3B(device,addr):
    msg = [0x03]
    msg += [((addr & 0xff0000) >> 16)]
    msg += [((addr & 0xff00) >> 8)]
    msg += [(addr & 0xff)]
    for i in range(256):
        msg += [0x00]
    r = device.xfer3(msg)
    return r[4:]

'''
# Register read function accepting integers as arguments
def read(device, cmd):
    msg = [0x00,0x00]
    msg[0] = cmd
    r = device.xfer2(msg)
    #print("0x ",end="")
    #for byte in r[1:]:
    #    print("{:02x} ".format(byte),end="")
    #print()
    return r

def read4(device, cmd):
    msg = [0x00,0x00,0x00,0x00,0x00]
    msg[0] = cmd
    r = device.xfer2(msg)
    return r

def read_flash_128(device):
    msg = [0x03,0x00,0x00,0x00]
    cycles = [0x00 for i in range(128)]
    msg.extend(cycles)
    r = device.xfer3(msg)
    return r

def read_flash_256(device):
    msg = [0x03,0x00,0x00,0x00,0x00]
    cycles = [0x00 for i in range(256)]
    msg.extend(cycles)
    r = device.xfer3(msg)
    return r[5:]
'''
