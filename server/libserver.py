###########################################################
#  Imports
###########################################################
import socket
import sys
import time
import threading
from bitstring import BitArray
from statistics import median_high

from permatrix import MATRIX

###########################################################
#  Variables
###########################################################
KEY = 184322013250812 # TODO

HOST = ''  # Symbolic name, meaning all available interfaces
PORT = 5553  # Arbitrary non-privileged port

ITERATIONS = 2
PACKET_SIZE = 1024

THRESHOLD = ((5 + 10) / 2) * 1024

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

def bytes_to_bits(bytes):
    return BitArray(bytes).bin

def bits_to_bytes(bits):
    return BitArray(bin=bits).tobytes()

###########################################################
#  Main functions
###########################################################
def permutate(secret_bits, key):
    return secret_bits # TODO

def verify_crc(secret_bytes, crc):
    return True # TODO

def recv_bits(conn):
    in_bits = ""
    while True:
        times = []

        for i in range(ITERATIONS):
            prev = time.time()
            data = conn.recv(PACKET_SIZE)
            after = time.time()
            times.append(float(after) - float(prev))

        if len(data) == 0:
            break

        print("[DEBUG] Times:")
        for t in times[1:]:
            print(str(t)+" seg")
        print("\n\n")

        bs = PACKET_SIZE / median_high(times[1:])

        print ("[DEBUG] Speed "+str(bs)+" b/s translation = "+translate(bs))

        in_bits += translate(bs)

    return in_bits

def client_thread(conn, addr, key=KEY):
    crc = None # TODO
    in_bits = recv_bits(conn)
    secret_bits = permutate(in_bits, key)
    secret_bytes = bits_to_bytes(secret_bits)

    if verify_crc(secret_bytes, crc): # TODO: Get CRC at start
        # TODO: send okey signal
        to_file(secret_bytes, addr)
    else:
        pass # TODO: send not okey signal and restart

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
