import socket
import time
from bitstring import BitArray

from permatrix import MATRIX

KEY = 2764644635623287432 # TODO

HOST = 'localhost'
PORT = 5553  # Arbitrary non-privileged port

ITERATIONS = 20
PACKET_SIZE = 1024


# Utilities:
def get_send_rate(n):
    if n == "0":
        return 1024 * 50
    else:
        return 1024 * 100


def seg_to_bs(numSeconds, sendRate):
    return numSeconds*sendRate


def bs_to_seg(numBytes, sendRate):
    return float(numBytes)/sendRate


def bytes_to_bits(bytes):
    pass


def bits_to_bytes(bits):
    pass

# Main functions
def calculate_crc(secret_bytes):
    pass


def permutate(secret_bits, key):
    pass

def send_network(secret_bits, covert=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    if not covert:
        covert = bytearray(PACKET_SIZE) # Dummy data buffer, just for testing

    for b in secret:
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


# Main function
def send_file(secret_bytes, covert=None):
    crc = calculate_crc(secret_bytes)
    secret_bits = bytes_to_bits(secret_bytes)
    secret_bits = permutate(secret_bits)

    send_network(secret_bits, covert)
