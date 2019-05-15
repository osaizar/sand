import socket
import sys
import time
import threading
from bitstring import BitArray
from statistics import median_high

from permatrix import MATRIX

KEY = 184322013250812 # TODO

HOST = ''  # Symbolic name, meaning all available interfaces
PORT = 5553  # Arbitrary non-privileged port

ITERATIONS = 20
PACKET_SIZE = 1024

# Utilities
def to_file(in_bytes, addr):
    file_name = addr[0].replace(".","-") + "_" + str(addr[1]) + ".out"
    with open(file_name, 'wb') as file:
        file.write(in_bytes)


def translate(bs):
    if bs < 70:
        return "0"
    else:
        return "1"


def bits_to_bytes(bits):
    pass


# Main functions
def permutate(secret_bits, key):
    pass


def recv_bits(conn):
    in_bits = ""
    while True:
        times = []

        for i in range(ITERATIONS):
            prev = time.time()
            data = conn.recv(PACKET_SIZE)
            after = time.time()
            times.append(float(after - prev))

        if len(data) == 0:
            break

        bs = median_high(times) * PACKET_SIZE

        print ("[DEBUG] Speed "+str(bs)+" kb/s translation = "+translate(bs))

        in_bits += translate(bs)

    return in_bits


def client_thread(conn, addr):
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
