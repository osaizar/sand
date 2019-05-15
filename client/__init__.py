from libclient import *

def main():
    data = open("test.txt", "rb").read()

    print ("[+] Got file, sending")
    file_in_bits = BitArray(data).bin
    send_file(file_in_bits)


if __name__ == '__main__':
    main()
