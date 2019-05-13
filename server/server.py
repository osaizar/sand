import socket
import sys
import time
import threading
from bitstring import BitArray

HOST = ''	# Symbolic name, meaning all available interfaces
PORT = 5553	# Arbitrary non-privileged port

ITERATIONS = 20
PACKET_SIZE = 1024

def to_file(in_bits):
    in_bits = BitArray(bin=in_bits)
    open("out", "wb").write(in_bits.tobytes())

def translate(bs):
    bs = bs / 1024
    if bs < 70:
        return "0"
    else:
        return "1"

def client_thread(conn, addr):
    in_bits = ""
    while True:
        prev = time.time()

        for i in range(ITERATIONS):
            data = conn.recv(PACKET_SIZE)

        if len(data) == 0:
            break

        after = time.time()
        trans = after - prev
        bs = int(ITERATIONS*PACKET_SIZE/trans)

        print ("[DEBUG] Speed "+str(bs)+" b/s translation = "+translate(bs))

        in_bits += translate(bs)

    print ("[+] Ended connection with " + addr[0] + ":" + str(addr[1]))
    to_file(in_bits)

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('[+] Socket created')

    #Bind socket to local host and port
    try:
    	s.bind((HOST, PORT))
    except socket.error as msg:
    	print("[!] Bind failed. Error Code : " + str(msg[0]) + " Message " + msg[1])
    	sys.exit()

    print ("[+] Socket bind complete")

    #Start listening on socket
    s.listen(10)
    print ("[+] Socket now listening")

    #now keep talking with the client
    try:
        while True:
            #wait to accept a connection - blocking call
            conn, addr = s.accept()
            print ("[+] Connected with " + addr[0] + ":" + str(addr[1]))

            threading.Thread(target=client_thread,
                    args=(conn, addr),
                    ).start()
    except:
        print("[!] Closing")

    s.close()


if __name__ == '__main__':
    main()
