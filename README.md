# Simple SEGGER RTT client for OpenOCD

A RTT client works (nearly) the same way as **JLinkRTTClient**.

- Configure OpenOCD RTT Output
- Display Received RTT messages

## Usage
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

## Example

### Use OpenOCD as debugger

1. Launch OpenOCD debugging on STM32H7S3L8 MCU

`openocd -c "gdb_port 3333" -c "telnet_port 4444" -s /opt/share/openocd/scripts -f stm32h7s3_nucleo.cfg -c "program firmware.elf" -c "init;reset run;"`

2. Start RTT client

`rtt_client.py 0x24000000`

3. Set your IDE's debugger to `GDB server` whith address `127.0.0.1 3333`

4. Start debugging in your IDE

### Use ST-Link shared mode

1. Add `st-link backend tcp` in your target configuration file (eg. `stm32h7s3_nucleo.cfg`)

2. Enable ST-Link shared mode in your IDE

In IAR : Debugger -> ST-LINK -> Multicore -> Enable multicore debugging / shared mode

3. Launch OpenOCD

`openocd.exe -s /opt/share/openocd/scripts -f stm32h7s3_nucleo.cfg -c "init;reset run"`

4. Start RTT client

5. Start debugging in your IDE

**For other MCUs you may need to check linker map to get RTT control block (.bss._SEGGER_RTT) address**
