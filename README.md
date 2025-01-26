# Simple SEGGER RTT client for OpenOCD

A RTT client works (nearly) the same way as **JLinkRTTClient**.

- Configure OpenOCD RTT Output
- Display Received RTT messages

Usage:
```
rtt_client.py [-h] [-v] [address] [size]

Simple RTT client for OpenOCD

positional arguments:
  address        control block search address (default: 0x20000000)
  size           search size (default: 0x4000)

options:
  -h, --help     show this help message and exit
  -v, --verbose  verbose
```

Example:

1. Start Debugging on STM32H7S3L8 MCU

`openocd -c "gdb_port 3333" -c "telnet_port 4444" -s /opt/share/openocd/scripts -f stm32h7s3_nucleo.cfg -c "program firmware.elf" -c "init;reset run;"` 

2. Start RTT client

`rtt_client.py 0x24000000`

**For other MCUs you may need to check linker map to get RTT control block (.bss._SEGGER_RTT) address**
