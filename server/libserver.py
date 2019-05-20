###########################################################
#  Imports
###########################################################
import socket
import sys
import time
import threading
import zlib
from bitstring import BitArray
from statistics import median_high
import numpy as np
from permatrix import MATRIX

###########################################################
#  Variables
###########################################################
KEY = 1843220 # TODO

HOST = ''  # Symbolic name, meaning all available interfaces
PORT = 5554  # Arbitrary non-privileged port

ITERATIONS = 4
PACKET_SIZE = 1024

LIMITS = [10, 20]

THRESHOLD = ((LIMITS[0] + LIMITS[1]) / 2) * 1024

###########################################################
#  Utilities
###########################################################
def to_file(in_bytes, addr):
    file_name = "out.out" # DEBUG
    #file_name = addr[0].replace(".","-") + "_" + str(addr[1]) + ".out"
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

def bytes_to_bits(bytes):
    return BitArray(bytes).bin

def bits_to_bytes(bits):
    return BitArray(bin=bits).tobytes()

###########################################################
#  Main functions
###########################################################
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
    crc_new = BitArray(int=zlib.crc32(secret_bytes), length=32).bin
    print("[DEBUG] got crc: "+crc_bits)
    print("[DEBUG] gen crc: "+crc_new)
    if (crc_new == crc_bits):
        print ("[DEBUG] Correct CRC")
        return True
    else:
        print ("[DEBUG] Incorrect CRC")
        return False

def recv_bits(conn):
    in_bits = ""
    finish = False
    while not finish:
        times = []

        for i in range(ITERATIONS):
            prev = time.time()
            data = conn.recv(PACKET_SIZE)
            after = time.time()
            times.append(float(after) - float(prev))

        print("[DEBUG] Times:")
        for t in times[1:]:
            print(str(t)+" seg")
        print("\n")

        bs = PACKET_SIZE / median_high(times[1:])

        if check_end(bs):
            print("[DEBUG] Got end signal")
            finish = True
        else:
            print ("[DEBUG] Speed "+str(bs)+" b/s translation = "+translate(bs))
            in_bits += translate(bs)

    return in_bits

def client_thread(conn, addr, key=KEY):
    in_bits = recv_bits(conn)
    crc_bits = in_bits[:32]
    in_bits = in_bits[32:]

    print ("[DEBUG] Transmission ended, permutating")

    secret_bits = permutate(in_bits, key)
    secret_bits = "".join(secret_bits)
    secret_bytes = bits_to_bytes(secret_bits)

    print ("[DEBUG] Permutation ended, checking crc")

    if verify_crc(secret_bytes, crc_bits):
        conn.send(str("ok").encode('utf8'))
        to_file(secret_bytes, addr)
    else:
        conn.send(str("nok").encode('utf8'))
        to_file(secret_bytes, addr) # DEBUG

    print ("[+] Ended connection with " + addr[0] + ":" + str(addr[1]))

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

    print ("[+] Socket bind complete")

    # Start listening on socket
    s.listen(10)
    print ("[+] Socket now listening")

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
