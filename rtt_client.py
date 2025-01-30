#!/usr/bin/env python3

from telnetlib import Telnet
import threading
import socket
import time
import re
import argparse

verbose = 0
inited = threading.Event()
class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def debug(msg, end='\n'):
    if verbose > 0:
        print(f'{BColors.OKCYAN}{msg}{BColors.ENDC}', end=end, flush=True)

def info(msg, end='\n'):
    print(f'{BColors.BOLD}{msg}{BColors.ENDC}', end=end, flush=True)

def setup_loop(address, size):
    server_stop_cmd = b'rtt server stop 9090\n'
    server_start_cmd = b'rtt server start 9090 0\n'

    def setup(telnet, address, size):
        setup_cmd = f'rtt setup {address} {size} "SEGGER RTT"\n'.encode()
        core_start_cmd = b'rtt start\n'
        core_stop_cmd = b'rtt stop\n'

        telnet.read_until(b'Open On-Chip Debugger')
        debug('\nConnected to OpenOCD')

        telnet.write(server_stop_cmd)
        telnet.write(core_stop_cmd)
        telnet.write(setup_cmd)
        debug('RTT Setup')
        telnet.expect([re.compile(b'>')])

        while True:
            telnet.write(core_start_cmd)
            debug('Searching for control block')
            (idx,match,data) = telnet.expect([re.compile(b'^(.*?)No control block found',flags=re.DOTALL), re.compile(b'^(.*?)Control block found at(.*?)$',flags=re.DOTALL)],timeout=1.0)
            if idx == 1:
                debug('Control block found')
                break
            time.sleep(1)

        telnet.write(server_stop_cmd)
        telnet.write(server_start_cmd)
        debug('Start RTT server')
        telnet.expect([re.compile(b'^(.*?)Listening on port ([0-9]+?) for rtt connections',flags=re.DOTALL)],timeout=1.0)
        debug('RTT server online\n')

    def watch(telnet):
        telnet.expect([re.compile(b'^(.*?)rtt: Failed',flags=re.DOTALL), re.compile(b'^(.*?)rtt: Up-channel \\d* is not active',flags=re.DOTALL)])
        debug('RTT terminated\n')
        telnet.write(server_stop_cmd)

    while True:
        try:
            with Telnet('localhost', 4444) as telnet:
                setup(telnet, address, size)
                inited.set()
                watch(telnet)
        except ConnectionRefusedError:
            debug('.', end='')
            time.sleep(1)
        except (ConnectionResetError, BrokenPipeError):
            debug('OpenOCD Disconnected')
            time.sleep(1)

def rtt_loop(address, size):
    info('Connecting to RTT')
    inited.wait(timeout=5)
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('127.0.0.1', 9090))
                info('RTT Connected\n')
                while True:
                    ret = s.recv(1024)
                    if len(ret) == 0:
                        time.sleep(1)
                        break
                    print(ret.decode(), end='', flush=True)
        except ConnectionRefusedError:
            info('.', end='')
            time.sleep(1)
        except (ConnectionResetError, BrokenPipeError):
            info('RTT Disconnected', end='')
            time.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.description = 'Simple RTT client for OpenOCD'
    parser.add_argument('address', type=lambda x: int(x,0), default=0x20000000,
                        help='control block search address (default: 0x%(default)X)', nargs='?')
    parser.add_argument('size', type=lambda x: int(x,0), default=0x4000,
                        help='search size (default: 0x%(default)X)', nargs='?')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='verbose')
    args = parser.parse_args()
    verbose = args.verbose
    setup_thread = threading.Thread(target=setup_loop, args=(args.address, args.size),daemon=True)
    setup_thread.start()
    rtt_loop(args.address, args.size)
