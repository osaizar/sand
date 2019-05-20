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

###########################################################
#  Variables
###########################################################
KEY = 1843220 # TODO

HOST = ''  # Symbolic name, meaning all available interfaces
PORT = 5553  # Arbitrary non-privileged port

ITERATIONS = 15
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
    if bs < (LIMITS[0] * 1024)/4:
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
    return secret_bits
    if isinstance(secret_bits[0], str):
        secret_bits = [int(x) for x in secret_bits]
    np.random.seed(key)
    for i in range(0, len(secret_bits), 8):
        key = np.random.randint(0,255)
        secret_bits[i:i+8] = np.dot(secret_bits[i:i+8], MATRIX[key])
    secret_bits = [str(x) for x in secret_bits]
    return secret_bits

def verify_crc(secret_bytes, crc_bits):
    crc_new = BitArray(int=zlib.crc32(secret_bytes), length=33).bin
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
    cnt = 0
    times = []
    while not finish:
        prev = time.time()
        data = conn.recv(PACKET_SIZE)
        after = time.time()
        curr = float(after) - float(prev)
        cnt += 1

        bs = PACKET_SIZE / curr

        if check_end(bs):
            print("[DEBUG] Got end signal")
            finish = True
        else:
            print ("[DEBUG] Speed "+str(bs))
            times.append(translate(bs))

    print("[DEBUG] Total packet count: "+str(cnt))
    times = times[1:]
    return times

def parse_times(times):
    in_bits = ""

    finish = False
    cursor = 0

    while not finish:
        print("\n[DEBUG] cursor: " + str(cursor))
        l = times[cursor:cursor+ITERATIONS]
        print("[DEBUG] l = " + str(l))
        med = str(mode(l))
        print("[DEBUG] med = " + str(med))
        in_bits += med

        corr = 0
        for i,e in enumerate(l):
            if l[-(i+1)] == med:
                break
            else:
                corr = (i+1)

        next_med = mode(times[cursor + ITERATIONS - corr:cursor + ITERATIONS - corr + int(ITERATIONS/2)])
        if times[cursor + ITERATIONS - corr] == next_med:
            cursor = cursor + ITERATIONS - corr
        else:
            cursor = cursor + ITERATIONS

        if cursor+ITERATIONS > (len(times)-1):
            finish = True

    return in_bits

def client_thread(conn, addr, key=KEY):
    times = recv_bits(conn)
    in_bits = parse_times(times)
    print ("[DEBUG] in_bits "+in_bits)
    crc_bits = in_bits[:33]
    in_bits = in_bits[33:]

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
