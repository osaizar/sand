import socket
import time

HOST = 'localhost'
PORT = 5553	# Arbitrary non-privileged port

ITERATIONS = 20
PACKET_SIZE = 1024

def get_send_rate(n):
    if n == 0:
        return 1024 * 50
    else:
        return 1024 * 100

def seg_to_bs(numSeconds, sendRate):
   return numSeconds*sendRate

def bs_to_seg(numBytes, sendRate):
   return float(numBytes)/sendRate


def send_file(file_bytes):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST,PORT))

    # We'll add to this tally as we send() bytes, and subtract from
    # at the schedule specified by (sendRate)
    bytesAheadOfSchedule = 0

    # Dummy data buffer, just for testing
    dataBuf = bytearray(PACKET_SIZE)

    prevTime = None

    for b in [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]:
        sendRate = get_send_rate(b)

        for i in range(ITERATIONS):
           now = time.time()

           if prevTime is not None:
              bytesAheadOfSchedule -= seg_to_bs(now-prevTime, sendRate)

           prevTime = now
           numBytesSent = sock.send(dataBuf)

           if (numBytesSent > 0):
              bytesAheadOfSchedule += numBytesSent
              if (bytesAheadOfSchedule > 0):
                  time.sleep(bs_to_seg(bytesAheadOfSchedule, sendRate))
           else:
              print ("[!] Error sending data, exiting!")
              break

def main():
    in_file = open("in.jpeg", "rb")
    data = in_file.read()
    in_file.close()

    print ("[+] Got file, sending")
    send_file(data)

if __name__ == '__main__':
    main()
