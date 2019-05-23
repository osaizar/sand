###########################################################
#  Imports
###########################################################
import socket
import sys
import time
import threading
import zlib
from bitstring import BitArray
from statistics import mode
import numpy as np
from permatrix import MATRIX
from config import *

###########################################################
#  Utilities
###########################################################
def to_file(in_bytes, addr):
    file_name = addr[0].replace(".","-") + "_" + str(addr[1]) + ".out"
    with open(file_name, 'wb') as file:
        file.write(in_bytes)

def translate(bs):
    if bs < THRESHOLD:
        return "0"
    else:
        return "1"

def check_end(bs):
    if bs < (LIMITS[0] * 1024)/2:
        return True
    else:
        return False

def bytes_to_bits(byte_array):
    byte_array = np.array(list(byte_array), dtype=np.uint8)
    bit_array = np.unpackbits(byte_array)
    bit_array = [str(x) for x in bit_array]
    return bit_array

def bits_to_bytes(bit_array):
    bit_array = [int(x) for x in bit_array]
    byte_array = np.packbits(bit_array)
    byte_array = bytes(byte_array.tolist())
    return byte_array

def print_debug(str):
    if DEBUG:
        print_debug("[DEBUG] "+str)
###########################################################
#  Main functions
###########################################################
def calculate_crc(secret_bytes):
    #crc = BitArray(int=zlib.crc32(secret_bytes), length=32).bin
    b = hex(zlib.crc32(secret_bytes))[2:]
    c = [int(b[x:x+2], 16) for x in range(0, len(b), 2)]
    crc = np.array(c, dtype=np.uint8)
    crc = np.unpackbits(crc)
    crc = "".join([str(x) for x in crc])
    print_debug("crc : "+str(crc))
    return crc

def permutate(secret_bits, key):
    if isinstance(secret_bits[0], str):
        secret_bits = [int(x) for x in secret_bits]
    np.random.seed(key)
    for i in range(0, len(secret_bits), 8):
        key = np.random.randint(0,255)
        secret_bits[i:i+8] = np.dot(secret_bits[i:i+8], MATRIX[key])
    secret_bits = [str(x) for x in secret_bits]
    return secret_bits

def verify_crc(secret_bytes, crc_bits):
    crc_new = calculate_crc(secret_bytes)
    print_debug("got crc: "+crc_bits)
    print_debug("gen crc: "+crc_new)
    if (crc_new == crc_bits):
        print_debug("Correct CRC")
        return True
    else:
        print_debug("Incorrect CRC")
        return False

def recv_bits(conn):
    in_bits = ""
    finish = False
    prev_end = False
    times = []
    in_bits = ""
    while not finish:
        prev = time.time()
        data = conn.recv(PACKET_SIZE)
        after = time.time()
        curr = float(after) - float(prev)
        times.append(curr)

        bs = PACKET_SIZE / curr

        if check_end(bs):
            if prev_end:
                print_debug("Got end signal")
                finish = True
            else:
                prev_end = True
                in_bits += mode(times)
                print_debug("Got "+mode(times))
                times = []
        else:
            prev_end = False
            print_debug("Speed "+str(bs))
            times.append(translate(bs))

    return in_bits

def client_thread(conn, addr, key=KEY):
    in_bits = recv_bits(conn)
    crc_bits = in_bits[:32]
    in_bits = in_bits[32:]

    print_debug("Transmission ended, permutating")

    secret_bits = permutate(in_bits, key)
    secret_bits = "".join(secret_bits)
    secret_bytes = bits_to_bytes(secret_bits)

    print_debug("Permutation ended, checking crc")

    if verify_crc(secret_bytes, crc_bits):
        conn.send(str("ok").encode('utf8'))
        print("[+] Got file from "+addr[0])
        to_file(secret_bytes, addr)
    else:
        print("[+] Got corrupted file from "+addr[0])
        conn.send(str("nok").encode('utf8'))

    print("[+] Ended connection with " + addr[0] + ":" + str(addr[1]))

def server_main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('[+] Socket created')

    # Bind socket to local host and port
    try:
        s.bind((HOST, PORT))
    except socket.error as msg:
        print("[!] Bind failed. Error Code : " + str(msg[0]) + " Message "
              + msg[1])
        sys.exit()

    print("[+] Socket bind complete")

    # Start listening on socket
    s.listen(10)
    print("[+] Socket now listening")

    # Now keep talking with the client
    try:
        while True:
            # Wait to accept a connection - blocking call
            conn, addr = s.accept()
            print ("[+] Connected with " + addr[0] + ":" + str(addr[1]))

            threading.Thread(target=client_thread,
                             args=(conn, addr),).start()
    except Exception as e:
        print("[!] Exception: " + str(e))
        print("[!] Closing")

    s.close()
