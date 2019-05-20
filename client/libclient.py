###########################################################
#  Imports
###########################################################
import socket
import time
import zlib
from bitstring import BitArray
import numpy as np
from permatrix import MATRIX

###########################################################
#  Variables
###########################################################
KEY = 1843220 # TODO

HOST = 'localhost'
PORT = 5554  # Arbitrary non-privileged port

ITERATIONS = 4
PACKET_SIZE = 1024

LIMITS = [10, 20]
THRESHOLD = ((LIMITS[0] + LIMITS[1]) / 2) * 1024
###########################################################
#  Utilities
###########################################################
def get_send_rate(n):
    if n == "0":
        return 1024 * LIMITS[0]
    else:
        return 1024 * LIMITS[1]

def seg_to_bs(numSeconds, sendRate):
    return numSeconds*sendRate

def bs_to_seg(numBytes, sendRate):
    return float(numBytes)/sendRate

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
    print ("[DEBUG] crc : "+str(crc))
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

def send_network(sock, secret_bits, covert=None):
    if not covert:
        covert = bytearray(PACKET_SIZE) # Dummy data buffer, just for testing
    elif len(covert) < PACKET_SIZE:
        covert += bytearray(PACKET_SIZE - len(covert))
    elif len(covert) > PACKET_SIZE:
        covert = covert[:PACKET_SIZE]

    print ("[DEBUG] Sending data")
    for b in secret_bits:
        sendRate = get_send_rate(b)
        print ("[DEBUG] sending "+b+" Rate "+str(sendRate/1024)+" kb/s")

        for i in range(ITERATIONS):
            now = time.time()
            numBytesSent = sock.send(covert)
            after = time.time()
            send_time = after - now

            if numBytesSent > 0:
                ideal_send_time = bs_to_seg(numBytesSent, sendRate)
                sleep_time = ideal_send_time - send_time
                if sleep_time > 0:
                    time.sleep(sleep_time)

            else:
                print ("[!] Error sending data, exiting!")
                break

def send_end(sock, covert=None):
    if not covert:
        covert = bytearray(PACKET_SIZE) # Dummy data buffer, just for testing

    sendRate = (LIMITS[0] * 1024)/4 # End Signal
    print ("[DEBUG] Finishing... connection Rate "+str(sendRate/1024)+" kb/s")
    covert = covert[:1024]
    for i in range(ITERATIONS):
        now = time.time()
        numBytesSent = sock.send(covert)
        after = time.time()
        send_time = after - now

        if numBytesSent > 0:
            ideal_send_time = bs_to_seg(numBytesSent, sendRate)
            sleep_time = ideal_send_time - send_time
            if sleep_time > 0:
                time.sleep(sleep_time)
        else:
            print ("[!] Error ending connection")
            break

def get_response(sock):
    state = sock.recv(PACKET_SIZE).decode('utf8')
    if state == "ok":
        print("[DEBUG] Got correct")
        return True
    else:
        print("[DEBUG] Got incorrect")
        return False

def send_file(secret_bytes, covert=None, key=KEY):
    crc = calculate_crc(secret_bytes)
    secret_bits = bytes_to_bits(secret_bytes)
    secret_bits = permutate(secret_bits, key)

    finish = False
    while not finish:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))

        send_network(sock, crc, covert) # send crc
        send_network(sock, secret_bits, covert) # send secret
        send_end(sock, covert)

        print("[DEBUG] File sent, awaiting response")
        finish = get_response(sock)
        if not finish:
            print("[DEBUG] Error: Resending file")

        sock.close()
