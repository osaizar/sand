import socket
import time
from bitstring import BitArray

HOST = 'localhost'
PORT = 5553  # Arbitrary non-privileged port

ITERATIONS = 20
PACKET_SIZE = 1024


def get_send_rate(n):
    if n == "0":
        return 1024 * 50
    else:
        return 1024 * 100


def seg_to_bs(numSeconds, sendRate):
    return numSeconds*sendRate


def bs_to_seg(numBytes, sendRate):
    return float(numBytes)/sendRate


def send_file(file_bytes):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    # We'll add to this tally as we send() bytes, and subtract from
    # at the schedule specified by (sendRate)
    # bytesAheadOfSchedule = 0

    # Dummy data buffer, just for testing
    dataBuf = bytearray(PACKET_SIZE)

    # prevTime = None

    for b in file_bytes:
        sendRate = get_send_rate(b)
        print ("[DEBUG] sending "+b+" Rate "+str(sendRate/1024)+" kb/s")

        for i in range(ITERATIONS):
            now = time.time()
            numBytesSent = sock.send(dataBuf)
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


def main():
    in_file = open("test.txt", "rb")
    data = in_file.read()
    in_file.close()

    print ("[+] Got file, sending")
    file_bytes = BitArray(data).bin
    send_file(file_bytes)


if __name__ == '__main__':
    main()
